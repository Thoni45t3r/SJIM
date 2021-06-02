# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################
from odoo import models, fields, api, _
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report
import time

class wizard_report_picking_skb(models.TransientModel):
    _name           = "wizard.report.picking.skb"
    _description    = "Laporan SKB"
    
    @api.model
    def _default_doc_type(self):
        company_id = self.env.user.company_id.id
        domain = [('purchase', '=', True),('company_id', '=', company_id)]
        if self.env.user.document_type_ids:
            domain.append(('id','in',self.env.user.document_type_ids.ids))
        doc_types = self.env['res.document.type'].search(domain)
        return doc_types and [(6,0,doc_types.ids)] or []

    # report_type     = fields.Selection(JasperDataParser.REPORT_TYPE, string="Document Type", default=lambda *a: 'pdf')
    report_type     = fields.Selection([('xlsx', 'Excel Workbook'),('pdf','PDF')], string="Document Type", default=lambda *a: 'xlsx')
    date_start		= fields.Date("Dari Tanggal", default=lambda *a: time.strftime('%Y-%m-01'))
    date_stop		= fields.Date("Sampai Tanggal", default=lambda *a: time.strftime('%Y-%m-%d'))
    company_id      = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id)
    location_id     = fields.Many2many('stock.location', string="Location", required=1)
    type_location_id = fields.Many2many('account.location', string="Type Location")
    
    @api.multi
    def create_report(self):
        data = self.read()[-1]
        if self.report_type == 'xlsx':
            name = 'report_picking_skb_xlsx'
        else:
            name = 'report_picking_skb'

        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : name,
            'datas': {
                    'model': 'report_picking_skb_xlsx',
                    'id': self._context.get('active_ids') and self._context.get('active_ids')[0] or  self.id,
                    'ids': self._context.get('active_ids') and self._context.get('active_ids') or[],
                    'report_type': data['report_type'],
                    'form': data
                },
            'nodestroy'     : False
            }
            
    @api.multi
    def create_report_without_subtotal(self):
        data = self.read()[-1]
        if self.report_type == 'xlsx':
            name = 'report_picking_skb_without_subtotal'
        else:
            name = 'report_picking_skb'

        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : name,
            'datas'         : {
                    'model'         : 'report_picking_skb_without_subtotal',
                    'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or  self.id,
                    'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or[],
                    'report_type'   : data['report_type'],
                    'form'          : data
                },
            'nodestroy'     : False
            }
            
    @api.multi
    def create_report_with_type_locations(self):
        data = self.read()[-1]
        if self.report_type == 'xlsx':
            name = 'report_picking_skb_with_type_locations_xlsx'

        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : name,
            'datas': {
                    'model': 'report_picking_skb_with_type_locations_xlsx',
                    'id': self._context.get('active_ids') and self._context.get('active_ids')[0] or  self.id,
                    'ids': self._context.get('active_ids') and self._context.get('active_ids') or[],
                    'report_type': 'xlsx',
                    'form': data
                },
            'nodestroy'     : False
            }
wizard_report_picking_skb()

class wizard_general_ledger_by_locations(models.TransientModel):
    _inherit = 'wizard.general.ledger.by.locations'
    
    type_location_id = fields.Many2many('account.location', string="Type Location")
    
    