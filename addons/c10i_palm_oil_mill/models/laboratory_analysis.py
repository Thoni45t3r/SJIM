# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   @author Pranoto Tahrir Fathoni <thoni.45t3r@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.addons import decimal_precision as dp
import time
class MillLaboratoryAnalysis(models.Model):
    _name = 'mill.laboratory.analysis'
    _description = "Mill Laboratory Analysis"
    
    name                = fields.Char('Nama')
    mill_order_id       = fields.Many2one('mrp.unbuild', string='Mill Order')
    date                = fields.Date('Tanggal', default=lambda self: datetime.now().strftime(DF), required=True, states={'done': [('readonly',True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')], string='Status', default='draft', index=True)
        
    kapasitas_produksi  = fields.Float(digits=dp.get_precision('Kapasitas Produksi'))
    stock_dalam_proses  = fields.Float(digits=dp.get_precision('Stock dalam Produksi'))
    
    start_proses_date   = fields.Date()
    #start_proses_time   = fields.datetime.Time()
    stop_proses_date    = fields.Date()
    #stop_proses_time    = fields.datetime.Time()
    jumlah_jam_olah     = fields.Integer('Jumlah Jam Olah')
    jumlah_jam_stagnasi = fields.Integer('Jumlah Jam Stagnasi')
    
    lhp_pko_lines       = fields.One2many('mill.lhp.pko.line', 'lab_id', string='Perincian Stock PKO', copy=True)
    lhp_pke_lines       = fields.One2many('mill.lhp.pke.line', 'lab_id', string='Perincian Stock Bungkil', copy=True)
    lhp_analisa_lab_pko_lines   = fields.One2many('mill.lhp.analisa.lab.pko', 'lab_id', string='Analisa FFA CPKO' , copy=True)
    lhp_analisa_lab_pke_lines   = fields.One2many('mill.lhp.analisa.lab.pke', 'lab_id', string='Analisa FFA Bungkil', copy=True) 
    lhp_kontrak_line    = fields.One2many('mill.lhp.kontrak.line', 'lab_id', string='Outstanding Kontrak', copy=True)
    lhp_note_lines      = fields.One2many('mill.lhp.note.line', 'lab_id', string='Catatan Analisa Laboratorium', copy=True)
    
    #perincian KWH listrik terpakai
    kwh_listrik_awal    = fields.Float('Meter Awal')
    kwh_listrik_akhir   = fields.Float('Meter Akhir')
    
    #perincian KWH boiler terpakai
    kwh_boiler_awal     = fields.Float('Meter Awal')
    kwh_boiler_akhir    = fields.Float('Meter Akhir')
    
    #perincian Solar terpakai
    stock_awal_solar        = fields.Float('Stock Awal Solar')
    pembelian_solar         = fields.Float('Pembelian Solar')
    solar_dipakai_mesin     = fields.Float('Dipakai Mesin')
    solar_dipakai_alat      = fields.Float('Dipakai Alat')
    stock_akhir_solar       = fields.Float('Stock Akhir Solar')
            
    @api.multi
    def unlink(self):
        for la in self:
            if la.state!='draft':
                raise UserError(_('You cannot delete Laboratory Analysis when it is not in DRAFT State'))
        return super(MillLaboratoryAnalysis, self).unlink()
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('mill.laboratory.analysis') or _('New')
        lab = super(MillLaboratoryAnalysis, self).create(vals)
        return lab
        
    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'
    
    @api.multi
    def action_set_draft(self):
        self.state = 'draft'
        
    @api.onchange('mill_order_id')
    def onchange_mill_order_id(self): 
        for lab in self:
            for order in lab.mill_order_id :
                lab.update({'date': order.date,
                            'start_proses_date': order.date,
                            'stop_proses_date': order.date})
                            
    @api.multi
    def action_unbuild(self):
        self.state = 'done'
        
    @api.multi
    def generate_lhp_tank(self):
        for lab in self:
            storage_id  = 0
            shift       = 0
            ffa_production    = 0.0
            iv_production     = 0.0
            resq = {}
            query_opening = """SELECT mlalp.storage_id, mlalp.shift, mlalp.ffa_production, mlalp.iv_production  
                FROM mill_lhp_analisa_lab_pko mlalp
                LEFT JOIN mill_laboratory_analysis mla ON mlalp.lab_id = mla.id
                WHERE date(mla.date) = (select date(mla.date) - 1)"""
            query_opening = query_opening
            self.env.cr.execute(query_opening)
            resq = self.env.cr.dictfetchone()
            if resq:
                storage_id      = resq.get('mlalp.storage_id',0)
                shift           = resq.get('mlalp.shift',0)
                ffa_production  = resq.get('mlalp.ffa_production',0.0)
                iv_production   = resq.get('mlalp.iv_production',0.0)
                    
            #lhp.update({'storage_id': storage_id,
                        #'shift': shift,
                        #'ffa_tank': ffa_production,
                        #'iv_tank': iv_production}) 
        
        return self.env['mill.lhp.analisa.lab.pko'].create({
            'storage_id': storage_id,
            'shift': shift,
            'ffa_tank': ffa_production,
            'iv_tank': iv_production,
            'lab_id'    : self.id,
        })
            
    @api.multi
    def generate_solar_stock(self):
        for lab in self:
            #for order in lab.mill_order_id:
                stock_awal = 0.0
                #for product_id in ('4392'):
                resq = {}
                query_opening = """SELECT  
                        product_id, sum(product_qty) as qty
                    FROM
                        (
                        (select product_id, product_qty from stock_move 
                        where product_id=%(product_id)s and location_id<>%(location_id)s and location_dest_id=%(location_id)s
                            and (date + INTERVAL '7 hours')::TIMESTAMP<'%(date)s' and state='done')
                        UNION ALL
                        (select product_id, -1*product_qty from stock_move 
                        where product_id=%(product_id)s and location_id=%(location_id)s and location_dest_id<>%(location_id)s
                            and (date + INTERVAL '7 hours')::TIMESTAMP<'%(date)s' and state='done')
                        ) dummy
                    GROUP BY product_id"""
                query_opening = query_opening%{'product_id': 4392, 'location_id': 15, 'date': lab.date + ' 00:00:00'}
                self.env.cr.execute(query_opening)
                resq = self.env.cr.dictfetchone()
                if resq:
                    #stock_awal = resq.get('qty',0.0)
                    lab.update({'stock_awal_solar': resq.get('qty',0.0)})
                #lab.update({'stock_awal_solar': stock_awal})
            
                resq1 = {}
                query_opening1 = """SELECT
                        product_id, sum(product_qty) as qty
                    FROM
                        (
                        (select product_id, product_qty from stock_move 
                        where product_id=%(product_id)s and location_id<>%(location_id)s and location_dest_id=%(location_id)s
                            and (date + INTERVAL '7 hours')::TIMESTAMP<'%(date)s' and state='done')
                        UNION ALL
                        (select product_id, -1*product_qty from stock_move 
                        where product_id=%(product_id)s and location_id=%(location_id)s and location_dest_id<>%(location_id)s
                            and (date + INTERVAL '7 hours')::TIMESTAMP<'%(date)s' and state='done')
                        ) dummy
                    GROUP BY product_id"""
                query_opening1 = query_opening1%{'product_id': 4392, 'location_id': 15, 'date': lab.date + ' 23:59:59'}
                self.env.cr.execute(query_opening1)
                resq1 = self.env.cr.dictfetchone()
                if resq1:
                    #stock_akhir = resq1.get('qty',0.0)
                    lab.update({'stock_akhir_solar': resq1.get('qty',0.0)})
                #lab.update({'stock_akhir_solar': stock_akhir})
            
                resq2 = {}
                query_incoming = """SELECT  
                        product_id, sum(product_qty) as qty
                    FROM
                        (select product_id, product_qty from stock_move 
                        where product_id=%(product_id)s and location_id<>%(location_id)s and location_dest_id=%(location_id)s
                            and (date + INTERVAL '7 hours')::TIMESTAMP between '%(date_start)s' and '%(date_stop)s' and state='done'
                        ) dummy
                    GROUP BY product_id"""
                query_incoming = query_incoming%{'product_id': 4392, 'location_id': 15, 'date_start': lab.date + ' 00:00:00', 'date_stop': lab.date + ' 23:59:59'}
                self.env.cr.execute(query_incoming)
                resq2 = self.env.cr.dictfetchone()
                if resq2:
                    #solar_beli = resq2.get('qty',0.0)
                    lab.update({'pembelian_solar': resq2.get('qty',0.0)})
                #order.update({'pembelian_solar': solar_beli})
            
                resq3 = {}
                query_outgoing = """SELECT  
                        product_id, sum(product_qty) as qty
                    FROM
                        (select product_id, product_qty from stock_move 
                        where product_id=%(product_id)s and location_id=%(location_id)s and location_dest_id<>%(location_id)s
                            and account_location_type_id=%(account_location_type_id)s
                            and (date + INTERVAL '7 hours')::TIMESTAMP between '%(date_start)s' and '%(date_stop)s' and state='done'
                        ) dummy
                    GROUP BY product_id"""
                query_outgoing = query_outgoing%{'product_id': 4392, 'account_location_type_id': 2, 'location_id': 15, 'date_start': lab.date + ' 00:00:00', 'date_stop': lab.date + ' 23:59:59'}
                self.env.cr.execute(query_outgoing)
                resq3 = self.env.cr.dictfetchone()
                if resq3:
                    #solar_untuk_msn = resq3.get('qty',0.0)
                    lab.update({'solar_dipakai_mesin': resq3.get('qty',0.0)})
                #order.update({'solar_dipakai_mesin': solar_untuk_msn})
            
                resq4 = {}
                query_outgoing1 = """SELECT  
                        product_id, sum(product_qty) as qty
                    FROM
                        (select product_id, product_qty from stock_move 
                        where product_id=%(product_id)s and location_id=%(location_id)s and location_dest_id<>%(location_id)s
                            and account_location_type_id=%(account_location_type_id)s
                            and (date + INTERVAL '7 hours')::TIMESTAMP between '%(date_start)s' and '%(date_stop)s' and state='done'
                        ) dummy
                    GROUP BY product_id"""
                query_outgoing1 = query_outgoing1%{'product_id': 4392, 'account_location_type_id': 4, 'location_id': 15, 'date_start': lab.date + ' 00:00:00', 'date_stop': lab.date + ' 23:59:59'}
                self.env.cr.execute(query_outgoing1)
                resq4 = self.env.cr.dictfetchone()
                if resq4:
                    #solar_untuk_alat = resq4.get('qty',0.0)
                    lab.update({'solar_dipakai_alat': resq4.get('qty',0.0)})
                #order.update({'solar_dipakai_alat': solar_untuk_alat})
            
    @api.multi
    def create_report_lhp(self):
        #data = self.read()[-1]
        date = datetime.strptime(self.date, DF)
        date_start = (date + relativedelta(day=1)).strftime(DF)
        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : 'report_lhp',
            'datas'         : {
                'model'         : 'mill.laboratory.analysis',
                'id'            : self.id,
                'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or[],
                'report_type'   : 'xlsx',
                'form'          : {
                    'id_lab'        : self.id,
                    #'id_mill_order' : self.mill_order_id,
                    'start_date'    : date_start,
                    'mla_date'       : self.date,
                },
            },
            'nodestroy': False
        }	
        
class MillLhpPko(models.Model):
    _name   = "mill.lhp.pko.line"
    _description    = "Laporan Harian Produksi PKO"
    
    lab_id              = fields.Many2one('mill.laboratory.analysis', 'Laboratory Analysis')
    location_id         = fields.Many2one('stock.location', string='Lokasi', default=15)
    storage_id          = fields.Many2one('mill.storage', 'Storage Tank', default=1)
    ffa_mix             = fields.Float('FFA Mix')
    iv_mix              = fields.Float('IV Mix')
    unit_of_measure     = fields.Many2one('product.uom', string='Satuan', default=3)
    stock_quantity      = fields.Float('Stock Quantity')
    
        
    #@api.onchange('storage_id')
    #def onchange_storage_id(self):
        #for pko in self:
            #for lab in pko.lab_id:
                #date = datetime.strptime(lab.date, DF)
                #last_date = (date - relativedelta(days=1)).strftime(DF)
                
                #qty_awal    = 0.0
                #qty_prod    = 0.0
                #resq = {}
                #query_opening = """SELECT mlp.stock_quantity_awal AS quantity_awal, mlp.quantity_production AS quantity_prod
                    #FROM mill_lhp_pko_line mlp
                    #LEFT JOIN mill_laboratory_analysis mla ON mlp.lab_id = mla.id
                    #WHERE mla.date = '%(yesterday)s'
                        #AND mlp.location_id = %(location)s
                        #AND mlp.storage_id = %(storage)s"""
                #query_opening = query_opening%{'yesterday': last_date, 'storage': pko.storage_id.id, 'location': pko.location_id.id}
                #self.env.cr.execute(query_opening)
                #resq = self.env.cr.dictfetchone()
                #if resq:
                    #qty_awal    = resq.get('quantity_awal',0.0)
                    #qty_prod    = resq.get('quantity_prod',0.0)
                    
                #pko.update({'stock_quantity_awal': (qty_awal + qty_prod)})
    
class MillLhpPke(models.Model):
    _name   = "mill.lhp.pke.line"
    _description    = "Laporan Harian Produksi PKE"
    
    lab_id              = fields.Many2one('mill.laboratory.analysis', 'Laboratory Analysis')
    location_id         = fields.Many2one('stock.location', string='Lokasi', default=15)
    warehouse_id        = fields.Many2one('mill.warehouse', string='Gudang', default=1)
    unit_of_measure     = fields.Many2one('product.uom', string='Satuan', default=3)
    stock_quantity      = fields.Float('Stock Quantity')
    
    #@api.onchange('warehouse_id')
    #def onchange_warehouse_id(self):
        #for pke in self:
            #for lab in pke.lab_id:
                #date = datetime.strptime(lab.date, DF)
                #last_date = (date - relativedelta(days=1)).strftime(DF)
                
                #qty_awal    = 0.0
                #qty_prod    = 0.0
                #resq = {}
                #query_opening = """SELECT mlp.stock_quantity_awal AS quantity_awal, mlp.quantity_production AS quantity_prod
                    #FROM mill_lhp_pke_line mlp
                    #LEFT JOIN mill_laboratory_analysis mla ON mlp.lab_id = mla.id
                    #WHERE mla.date = '%(yesterday)s'
                        #AND mlp.location_id = %(location)s
                        #AND mlp.storage_id = %(gudang)s"""
                #query_opening = query_opening%{'yesterday': last_date, 'gudang': pke.warehouse_id.id, 'location': pke.location_id.id}
                #self.env.cr.execute(query_opening)
                #resq = self.env.cr.dictfetchone()
                #if resq:
                    #qty_awal    = resq.get('quantity_awal',0.0)
                    #qty_prod    = resq.get('quantity_prod',0.0)
                    
                #pke.update({'stock_quantity_awal': (qty_awal + qty_prod)})
    
class MillAnalisaLabPko(models.Model):
    _name   = "mill.lhp.analisa.lab.pko"
    _description    = "Laporan Hasil Analisa FFA PKO"
    
    storage_id      = fields.Many2one('mill.storage', 'Storage Tank', default=1)
    lab_id          = fields.Many2one('mill.laboratory.analysis', 'Laboratory Analysis')
    shift           = fields.Integer('Shift')
    ffa_tank        = fields.Float('FFA Tangki')
    iv_tank         = fields.Float('IV Tangki')
    ffa_production  = fields.Float('FFA Produksi')
    iv_production   = fields.Float('IV Produksi')
    ffa_mix         = fields.Float('FFA Mix')
    iv_mix          = fields.Float('IV Mix')
    
    #@api.onchange('shift')
    #def onchange_shift(self): 
        #for ffa in self:
            #for lab in ffa.lab_id :
                #date = datetime.strptime(lab.date, DF)
                #last_date = (date - relativedelta(days=1)).strftime(DF)
                
                #ffa_production    = 0.0
                #iv_production     = 0.0
                #resq = {}
                #query_opening = """SELECT mlalp.ffa_production AS ffa_prod, mlalp.iv_production AS iv_prod  
                    #FROM mill_lhp_analisa_lab_pko mlalp
                    #LEFT JOIN mill_laboratory_analysis mlab ON mlalp.lab_id = mlab.id
                    #WHERE mlab.date = '%(yesterday)s'
                        #AND mlalp.storage_id = %(storage)s
                        #AND mlalp.shift = %(shift)s"""
                #query_opening = query_opening%{'yesterday': last_date, 'storage': ffa.storage_id.id, 'shift': ffa.shift}
                #self.env.cr.execute(query_opening)
                #resq = self.env.cr.dictfetchone()
                #if resq:
                    #ffa_production  = resq.get('ffa_prod',0.0)
                    #iv_production   = resq.get('iv_prod',0.0)
                    
                #ffa.update({'ffa_tank': ffa_production,
                            #'iv_tank': iv_production})
         
class MillAnalisaLabPke(models.Model):
    _name   = "mill.lhp.analisa.lab.pke"
    _description    = "Laporan Hasil Analisa FFA PKE"
    
    lab_id          = fields.Many2one('mill.laboratory.analysis', 'Laboratory Analysis')
    shift           = fields.Integer('Shift')
    line            = fields.Integer('Line')
    minyak_bungkil  = fields.Float(digits=dp.get_precision('Minyak Bungkil'))  
    kadar_air       = fields.Float(digits=dp.get_precision('Kadar Air'))
    ffa             = fields.Float(digits=dp.get_precision('FFA Tangki'))
    iv              = fields.Float(digits=dp.get_precision('IV Tangki'))
    
class MillLhpKontrak(models.Model):
    _name   = "mill.lhp.kontrak.line"
    _description    = "Laporan Outstanding Kontrak"
    
    lab_id          = fields.Many2one('mill.laboratory.analysis', 'Laboratory Analysis')
    order_id        = fields.Many2one('sale.order', 'Kontrak', default=0)
    partner_id      = fields.Many2one('res.partner', 'Customer')
    date            = fields.Date('Tanggal Kontrak')
    unit_of_measure = fields.Many2one('product.uom', string='Satuan', default=3)
    product_uom_qty = fields.Float('Stock Akhir')
    qty_delivered   = fields.Float('Quantity Terkirim')
    
    @api.onchange('order_id')
    def onchange_order_id(self):
        for kontrak in self:
            partner  = 0
            tanggal  = 0
            quantity = 0.0
            terkirim = 0.0
            
            if self.order_id:
                resq = {}
                query_opening = """SELECT so.partner_id AS customer, so.confirmation_date AS date_order, 
                                        sol.product_uom_qty AS stock_akhir, sol.qty_delivered AS qty_terkirim  
                    FROM sale_order_line sol
                    LEFT JOIN sale_order so ON so.id = sol.order_id
                    WHERE sol.order_id = %(order_id)s"""
                query_opening = query_opening%{'order_id': kontrak.order_id.id}
                self.env.cr.execute(query_opening)
                resq = self.env.cr.dictfetchone()
                if resq:
                    partner  = resq.get('customer',0)
                    tanggal  = resq.get('date_order',0)
                    quantity = resq.get('stock_akhir',0.0)
                    terkirim = resq.get('qty_terkirim',0.0)
                    
                kontrak.update({'partner_id': partner,
                                'date': tanggal,
                                'product_uom_qty': quantity * 1000,
                                'qty_delivered': terkirim * 1000})
                                
    #@api.multi
    #def get_kontrak(self):
        #for kontrak in self:               
    
class MillLhpNote(models.Model):
    _name           = "mill.lhp.note.line"
    _description    = "Catatan Analisa Laboratorium"
    
    lab_id          = fields.Many2one('mill.laboratory.analysis', 'Laboratory Analysis')
    note            = fields.Char('Catatan')