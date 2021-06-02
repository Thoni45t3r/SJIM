# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   @author Pranoto Tahrir Fathoni <Thoni.45t3r@gmail.com>
#
######################################################################################################
from odoo import models, fields, api, _
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report
import time

class wizard_rekap_timbangan_manual(models.TransientModel):
    _name           = "wizard.rekap.timbangan.manual"
    _description    = "Rekap Timbangan Manual"
    
    wb_picking_type_id = fields.Many2one('weighbridge.picking.type', string='Tipe Transaksi', required=True)
    report_type     = fields.Selection(JasperDataParser.REPORT_TYPE, string="Document Type", default=lambda *a: 'pdf')
    date_start		= fields.Date("Dari Tanggal", default=lambda *a: time.strftime('%Y-%m-01'))
    date_stop		= fields.Date("Sampai Tanggal", default=lambda *a: time.strftime('%Y-%m-%d'))
    #company_id      = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id)
    
    @api.multi
    def create_report(self):
        data = self.read()[-1]
        #currency = self.env['res.company'].browse(data['company_id'][0]).currency_id
        #if currency:
            #data.update({'currency_name': currency.name})
        #name = 'report_rekap_timbangan_manual'
        if data['report_type'] in ['xls', 'xlsx']:
            name = 'report_rekap_timbangan_manual'
        else:  
            name = 'report_rekap_timbangan_manual'
        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : name,
            'datas': {
                    'model'         :'wizard.rekap.timbangan.manual',
                    'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or  self.id,
                    'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or[],
                    'report_type'   : data['report_type'],
                    'form'          : data
                },
            'nodestroy'     : False
            }
wizard_rekap_timbangan_manual()