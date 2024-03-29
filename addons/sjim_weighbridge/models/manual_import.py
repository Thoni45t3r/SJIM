# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

import time
import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import base64
import xlrd
from xlrd import open_workbook, XLRDError
from odoo import models, fields, tools, exceptions, api, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DT
import os
import tempfile

import logging
_logger = logging.getLogger(__name__)

# UNTUK IMPORT DATA TIMBANG: 99, BURSUMI, WTA PANJANG
class manual_import_dharmala(models.Model):
    _name = 'manual.import.dharmala'
    _inherit = ['mail.thread']
    _description = 'Manual Import Dharmala'

    # name = fields.Char("Name", default="/", states={'done': [('readonly',True)]})
    name = fields.Char("Name", default="/", readonly=True)
    description = fields.Char("Description", default="/", states={'done': [('readonly',True)]})
    book = fields.Binary(string='File Excel', states={'done': [('readonly',True)]})
    book_filename = fields.Char(string='File Name', states={'done': [('readonly',True)]})
    create_date = fields.Date('Creation Date', default=fields.Date.context_today, states={'done': [('readonly',True)]})
    line_ids = fields.One2many('manual.import.dharmala.line', 'import_id', string="Details", states={'done': [('readonly',True)]})
    error_note = fields.Text("Error Note", readonly=True)
    note = fields.Text("Note", states={'done': [('readonly',True)]})
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get(), states={'done': [('readonly',True)]})
    state = fields.Selection(selection=[('draft', 'New'), ('imported', 'Imported'), ('confirm', 'Confirmed'), ('done', 'Picking Created')], string='Status',  copy=False, default='draft', index=False, readonly=False, track_visibility='always')
    picking_ids = fields.Many2many('stock.picking', 'import_darmala_picking_rel', 'import_id', 'picking_id', string='Pickings', states={'done': [('readonly',True)]})

    @api.multi
    def unlink(self):
        for data in self:
            if data.state not in ('draft'):
                raise exceptions.UserError(_('You can not delete a manual import document when state not in draft!'))
        return super(manual_import_dharmala, self).unlink()

    @api.model
    def create(self, values):
        if values.get('name','/')=='/':
            name = self.env['ir.sequence'].next_by_code(self._name)
            values.update({'name': name})
        return super(manual_import_dharmala, self).create(values)

    @api.multi
    def set_to_draft(self):
        for data in self:
            data.state = 'draft'
            data.book = False
            data.book_filename = False
            for x in data.line_ids:
                x.unlink()

    @api.multi
    def confirm(self):
        self.ensure_one()
        found_error = False
        error_notes = []
        for line in self.line_ids:
            # allocate type location
            picking_type = self.env['weighbridge.picking.type'].search([('name','=',line.type)], limit=1)
            if not picking_type:
                found_error = True
                error_notes.append("Err Tiket %s : %s tidak dapat ditemukan di Jenis Transaksi Timbangan. \nSilahkan dibuatkan alokasinya di Master Data Weighbridge"%(line.no_timbang ,line.type))
                continue
            line.wb_picking_type_id = picking_type.id
            # allocate product
            product = self.env['weighbridge.product'].search([('name','=',line.product)], limit=1)
            if not product:
                found_error = True
                error_notes.append("Err Tiket %s : %s tidak dapat ditemukan di Produk Timbangan. \nSilahkan dibuatkan alokasinya di Master Data Weighbridge"%(line.no_timbang,line.product))
                continue
            line.wb_product_id = product.id
            # allocate transporter
            transporter = self.env['weighbridge.partner'].search([('name','=',line.transporter)], limit=1)
            if not transporter:
                found_error = True
                error_notes.append("Err Tiket %s : %s tidak dapat ditemukan di Relasi Timbangan. \nSilahkan dibuatkan alokasinya di Master Data Weighbridge"%(line.no_timbang,line.transporter))
                continue
            line.wb_transporter_id = transporter.id
            # allocate kontrak
            contract = self.env['weighbridge.contract'].search([('name','=',line.kontrak)], limit=1)
            if not contract:
                found_error = True
                error_notes.append("Err Tiket %s : %s tidak dapat ditemukan di Kontrak Timbangan. \nSilahkan dibuatkan alokasinya di Master Data Weighbridge"%(line.no_timbang,line.kontrak))
                continue
            line.wb_contract_id = contract.id
        if found_error and error_notes:
            self.error_note = '\n'.join(error_notes)
        else:
            self.error_note = ''
            self.state = 'confirm'
            count = 1
            for line in self.line_ids:
                line.number = "%s/%s"%(str(self.name),str(count))
                count += 1

    def import_manual(self):
        """
        XL_CELL_EMPTY	0	empty string ‘’
        XL_CELL_TEXT	1	a Unicode string
        XL_CELL_NUMBER	2	float
        XL_CELL_DATE	3	float
        XL_CELL_BOOLEAN	4	int; 1 means True, 0 means False
        XL_CELL_ERROR	5	int representing internal Excel codes; for a text representation, refer to the supplied dictionary error_text_from_code
        XL_CELL_BLANK	6	empty string ‘’. Note: this type will appear only when open_workbook(..., formatting_info= True) is used.
        """
        attendance_recap_line_obj   = self.env['manual.import.dharmala.line']
        if not self.book:
            raise exceptions.ValidationError(_("Upload your data first!"))
        if self.line_ids:
            for lines in self.line_ids:
                lines.unlink()
        data = base64.decodestring(self.book)
        try:
            xlrd.open_workbook(file_contents=data)
        except XLRDError:
            raise exceptions.ValidationError(_("Unsupported Format!"))
        wb = xlrd.open_workbook(file_contents=data)
        total_sheet = len(wb.sheet_names())
        error_notes  = []
        found_error = False
        for i in range(total_sheet):
            sheet = wb.sheet_by_index(i)
            for rows in range(sheet.nrows):
                #Rows 1 hanya untuk title
                if rows > 0:
                    mandatory_number = [5,6,7]
                    mandatory_text = [0,1,2,3,4,8,9,10]
                    for col in range(0,11):
                        if col in mandatory_number:
                            try:
                                x = float(str(sheet.cell_value(rows, col)).strip())
                            except:
                                found_error = True
                                error_notes.append(
                                    "Import Error Baris %s : Bruto, Tarra dan Netto harus berisi Angka" % str(rows))
                        elif col in mandatory_text:
                            if str(sheet.cell_value(rows, col)).strip()=='':
                                found_error = True
                                error_notes.append("Import Error Baris %s : Ada kolom kosong. Setiap Kolom Wajib diisi"%str(rows))

                    # tanggal
                    try:
                        date_str = float(str(sheet.cell_value(rows, 8)).strip())
                        seconds = (date_str - 25569) * 86400.0
                        date = datetime.datetime.utcfromtimestamp(seconds).strftime("%d/%m/%Y")
                    except:
                        date = str(sheet.cell_value(rows, 8)).strip()

                    try:
                        no_timbang = str(int(sheet.cell_value(rows, 1))).strip()
                    except:
                        no_timbang = str(sheet.cell_value(rows, 1)).strip()
                    attendance_recap_line_obj.create({
                        'import_id'         : self.id,
                        'name'              : "Timbang " + str(sheet.cell_value(rows, 1)).strip(),
                        'type'              : str(sheet.cell_value(rows, 0)).strip(),
                        'no_timbang'        : no_timbang,
                        'no_pol'            : str(sheet.cell_value(rows, 2)).strip(),
                        'vendor'            : str(sheet.cell_value(rows, 3)).strip(),
                        'kontrak'           : str(sheet.cell_value(rows, 4)).strip(),
                        'bruto'             : str(sheet.cell_value(rows, 5)).strip(),
                        'tarra'             : str(sheet.cell_value(rows, 6)).strip(),
                        'netto'             : str(sheet.cell_value(rows, 7)).strip(),
                        'date'              : date,
                        'transporter'       : str(sheet.cell_value(rows, 9)).strip(),
                        'product'           : str(sheet.cell_value(rows, 10)).strip(),
                        'note'              : str(sheet.cell_value(rows, 11)).strip(),
                    })
        if found_error and error_notes:
            self.error_note = "\n".join(list(set(error_notes)))
        else:
            self.state = 'imported'
            self.error_note = ''
        # self.name = "Timbangan"

    def _prepare_sale_move(self, line, sale_line, picking):
        procurement_line_id = self.env['procurement.order'].search([('sale_line_id', '=', sale_line.id)], order='id desc', limit=1)
        if not procurement_line_id:
            vals = sale_line._prepare_order_line_procurement(group_id=sale_line.order_id.procurement_group_id.id)
            vals['product_qty'] = sale_line.product_uom_qty
            procurement_line_id = self.env["procurement.order"].create(vals)
        return {
            'picking_id': picking.id,
            'name': sale_line.name,
            'company_id': sale_line.order_id.company_id.id,
            'product_id': line.product_id.id,
            'product_uom_qty': float(line.netto),
            'product_uom': line.product_id.uom_id.id,
            'warehouse_id': line.picking_type_id.warehouse_id.id,
            'location_id': line.picking_type_id.default_location_src_id.id,
            'location_dest_id': line.partner_id.property_stock_customer.id,
            'procurement_id': procurement_line_id.id,
            'group_id': sale_line.order_id.procurement_group_id.id,
            'picking_type_id': procurement_line_id.rule_id.picking_type_id.id,
            'state': 'draft',
            'gross_weight': float(line.bruto),
            'tara_weight': float(line.tarra),
            'net_weight': float(line.netto),
            'potongan_weight': 0.0,
        }

    def _prepare_purchase_move(self, line, purchase_line, picking):
        return {
            'company_id': purchase_line.order_id.company_id.id,
            'name': purchase_line.name,
            'picking_id': picking.id,
            'product_id': line.product_id.id,
            'product_uom_qty': float(line.netto),
            'product_uom': line.product_id.uom_id.id,
            'warehouse_id': line.picking_type_id.warehouse_id.id,
            'location_id': line.partner_id.property_stock_supplier.id,
            'location_dest_id': line.picking_type_id.default_location_dest_id.id,
            'picking_type_id': line.picking_type_id.id,
            'partner_id': line.partner_id.id,
            'state': 'draft',
            'netto_pks': float(line.netto),
            'gross_weight': float(line.bruto),
            'tara_weight': float(line.tarra),
            'net_weight': float(line.netto),
            'potongan_weight': 0.0,

            'purchase_line_id': purchase_line.id,
            'price_unit': purchase_line._get_stock_move_price_unit(),
            'procurement_id': False,
        }

    @api.multi
    def create_pickings(self):
        self.ensure_one()
        _logger.info('================START: Converting Detail Import to Picking')
        ################################ DETAIL IMPORT TO PICKING ##################################
        Picking = self.env['stock.picking']
        StockMove = self.env['stock.move']
        # BEGIN: Display Error
        new_pickings = self.env['stock.picking']
        found_error = False
        error_notes = []
        for line in self.line_ids:
            if line.picking_type_id.code == 'incoming':
                purchase_order = line.wb_contract_id.related_purchase_id
                if not purchase_order:
                    found_error = True
                    error_notes.append("Error %s. Kontrak %s tidak dapat ditemukan"%(line.no_timbang, line.kontrak))
                    continue
                if purchase_order.state not in ('purchase', 'done'):
                    found_error = True
                    error_notes.append("Error %s. Kontrak %s sudah Selesai atau Masih Draft" % (line.no_timbang, line.kontrak))
                    continue
                purchase_line = False
                for x in purchase_order.order_line:
                    if x.product_id.id == line.product_id.id:
                        purchase_line = x
                        break
                if not purchase_line:
                    found_error = True
                    error_notes.append("Error %s. Produk %s tidak dapat ditemukan di kontrak %s" % (line.no_timbang, line.product, line.kontrak))
                    continue
            elif line.picking_type_id.code == 'outgoing':
                sale_order = line.wb_contract_id.related_sale_id
                if not sale_order:
                    found_error = True
                    error_notes.append("Error %s. Kontrak %s tidak dapat ditemukan" % (line.no_timbang, line.kontrak))
                    continue
                if sale_order.state not in ('sale', 'done'):
                    found_error = True
                    error_notes.append("Error %s. Kontrak %s sudah Selesai atau Masih Draft" % (line.no_timbang, line.kontrak))
                    continue
                procurement_group = sale_order.procurement_group_id
                if not procurement_group:
                    proc_vals = sale_order._prepare_procurement_group()
                    procurement_group = self.env["procurement.group"].create(proc_vals)
                    sale_order.procurement_group_id = procurement_group.id
                sale_order_line = False
                for x in sale_order.order_line:
                    if x.product_id.id == line.product_id.id:
                        sale_order_line = x
                        break
                if not sale_order_line:
                    found_error = True
                    error_notes.append("Error %s. Produk %s tidak dapat ditemukan di kontrak %s" % (
                    line.no_timbang, line.product, line.kontrak))
                    continue
        if found_error:
            self.error_note = '\n'.join(error_notes)
            return False
        # END: Display Error

        # CREATE NEW PICKING
        for line in self.line_ids:
            if line.picking_type_id.code=='incoming':
                _logger.info('::::::::::::::::::: Converting Timbang %s to Receipt' % line.no_timbang)
                purchase_order = line.wb_contract_id.related_purchase_id
                if not purchase_order or purchase_order.state not in ('purchase', 'done'):
                    continue
                purchase_line = False
                for x in purchase_order.order_line:
                    if x.product_id.id == line.product_id.id:
                        purchase_line = x
                        break
                if not purchase_line:
                    continue
                purchase_line = purchase_line.ensure_one()
                new_picking = Picking.create({
                    'name': line.number,
                    'partner_id': line.partner_id.id,
                    'picking_type_id': line.picking_type_id.id,
                    'location_id': line.partner_id.property_stock_supplier.id,
                    'location_dest_id': line.picking_type_id.default_location_dest_id.id,
                    'date_done': datetime.datetime.strptime(line.date,'%d/%m/%Y').strftime('%Y-%m-%d 12:00:00'),
                    'origin': purchase_order.name,
                    'company_id': purchase_order.company_id.id,
                    'state': 'draft',
                    'transporter_id': line.transporter_id.id,
                    'tiket_timbang': line.no_timbang,
                    'driver_name': '',
                    'vehicle_number': line.no_pol,
                    # 'bea_cukai_ids': purchase_order.bea_cukai_id and [(4,purchase_order.bea_cukai_id.id)] or False,
                    })
                StockMove.create(self._prepare_purchase_move(line, purchase_line, new_picking))
            elif line.picking_type_id.code=='outgoing':
                _logger.info('::::::::::::::::::: Converting Timbang %s to Delivery' % line.no_timbang)
                sale_order = line.wb_contract_id.related_sale_id
                if not sale_order or sale_order.state not in ('sale', 'done'):
                    continue
                procurement_group = sale_order.procurement_group_id
                if not procurement_group:
                    proc_vals = sale_order._prepare_procurement_group()
                    procurement_group = self.env["procurement.group"].create(proc_vals)
                    sale_order.procurement_group_id = procurement_group.id
                sale_order_line = False
                for x in sale_order.order_line:
                    if x.product_id.id == line.product_id.id:
                        sale_order_line = x
                        break
                if not sale_order_line:
                    continue
                sale_order_line = sale_order_line.ensure_one()
                new_picking = Picking.create({
                    'name': line.number,
                    'partner_id': line.partner_id.id,
                    'picking_type_id': line.picking_type_id.id,
                    'location_id': line.picking_type_id.default_location_src_id.id,
                    'location_dest_id': line.partner_id.property_stock_customer.id,
                    'date_done': datetime.datetime.strptime(line.date,'%d/%m/%Y').strftime('%Y-%m-%d 12:00:00'),
                    'group_id': procurement_group.id,
                    'company_id': sale_order.company_id.id,
                    'state': 'draft',
                    'tiket_timbang': line.no_timbang,
                    'transporter_id': line.transporter_id.id,
                    'driver_name': '',
                    'vehicle_number': line.no_pol,
                    # 'bea_cukai_ids': sale_order.bea_cukai_id and [(4,0,sale_order.bea_cukai_id.id)] or False,
                    })
                new_move = StockMove.create(self._prepare_sale_move(line, sale_order_line, new_picking))

            new_picking.action_done()
            new_pickings |= new_picking
            # UPDATE TANGGAL TRANSAKSI
            for move in new_picking.move_lines:
                move.sudo().date = datetime.datetime.strptime(line.date,'%d/%m/%Y').strftime('%Y-%m-%d 12:00:00')
                if line.picking_type_id.code=='incoming':
                    move.quant_ids.sudo().write({'in_date' : datetime.datetime.strptime(line.date,'%d/%m/%Y').strftime('%Y-%m-%d 12:00:00')})
                    for amove in move.sudo().account_move_line_ids.mapped('move_id'):
                        try:
                            if amove.sudo().state != 'draft':
                                amove.sudo().button_cancel()
                                amove.sudo().write({'date': datetime.datetime.strptime(line.date,'%d/%m/%Y').strftime('%Y-%m-%d')})
                                amove.sudo().post()
                            else:
                                amove.sudo().write({'date': datetime.datetime.strptime(line.date,'%d/%m/%Y').strftime('%Y-%m-%d')})
                        except:
                            _logger.warning('Failed to update Journal')
            new_picking.date_done = datetime.datetime.strptime(line.date,'%d/%m/%Y').strftime('%Y-%m-%d 12:00:00')
            line.picking_date = datetime.datetime.strptime(line.date,'%d/%m/%Y').strftime('%Y-%m-%d 12:00:00')
            line.write({'picking_id': new_picking.id})
        self.picking_ids  = [(6,0,new_pickings.ids)]
        self.state = 'done'
        self.error_note = ''
        _logger.info('================END: Converting Detail Import to Picking')

class manual_import_dharmala_line(models.Model):
    _name = 'manual.import.dharmala.line'
    _description = 'Manual Import Dharmala Line'

    wb_picking_type_id = fields.Many2one('weighbridge.picking.type', 'Converter Picking Type')
    picking_type_id = fields.Many2one('stock.picking.type', related='wb_picking_type_id.related_picking_type_id', string='Picking Type')
    wb_product_id = fields.Many2one('weighbridge.product', 'Converter Product')
    product_id = fields.Many2one('product.product', related='wb_product_id.related_product_id', string='Product', domain=[('product_type','=','stockable')])
    wb_transporter_id = fields.Many2one('weighbridge.partner', 'Converter Transporter')
    transporter_id = fields.Many2one('res.partner', related='wb_transporter_id.related_partner_id', string='Transporter')
    wb_contract_id = fields.Many2one('weighbridge.contract', 'Converter Contract')
    partner_id = fields.Many2one('res.partner', related='wb_contract_id.related_partner_id', string='Partner', store=True)
    picking_id = fields.Many2one('stock.picking', 'Related Picking')
    wb_do = fields.Char(string="Delivery Order")
    picking_date = fields.Date()

    import_id = fields.Many2one('manual.import.dharmala', string="Import", ondelete="cascade")
    name = fields.Char("Name")
    number = fields.Char("Number")
    type = fields.Char("Tipe")
    date = fields.Char("Tanggal")
    no_timbang = fields.Char("No. Tiket Timbang")
    no_pol = fields.Char("No. Polisi")
    driver_name = fields.Char("Supir")
    product = fields.Char("Produk")
    bruto = fields.Char("Bruto")
    tarra = fields.Char("Tarra")
    netto = fields.Char("Netto")
    vendor = fields.Char("Vendor")
    kontrak = fields.Char("Kontrak")
    transporter = fields.Char("Transporter")
    note = fields.Char("Keterangan")