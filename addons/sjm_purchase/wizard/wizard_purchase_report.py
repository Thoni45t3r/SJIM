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

class wizard_purchase_report(models.TransientModel):
    _name           = "wizard.purchase.report"
    _description    = "Purchase Report"
    
    @api.model
    def _default_doc_type(self):
        company_id = self.env.user.company_id.id
        domain = [('purchase', '=', True),('company_id', '=', company_id)]
        if self.env.user.document_type_ids:
            domain.append(('id','in',self.env.user.document_type_ids.ids))
        doc_types = self.env['res.document.type'].search(domain)
        # return doc_types and [(6,0,doc_types.ids)] or []
        return []

    # report_type     = fields.Selection(JasperDataParser.REPORT_TYPE, string="Document Type", default=lambda *a: 'pdf')
    report_type     = fields.Selection([('xlsx', 'Excel Workbook')], string="Document Type", default=lambda *a: 'xlsx')
    date_start		= fields.Date("Dari Tanggal", default=lambda *a: time.strftime('%Y-%m-01'))
    date_stop		= fields.Date("Sampai Tanggal", default=lambda *a: time.strftime('%Y-%m-%d'))
    company_id      = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id)
    doc_type_ids    = fields.Many2many('res.document.type', string='Document Type', default=_default_doc_type)
    report_format   = fields.Selection([('rekap', 'Rekap Purchase'),('spk', 'SPK'),('rekap_spb', 'Rekap Purchase dengan SPB')], string='Format Laporan', default='rekap')

    
    @api.multi
    def create_report(self):
        data = self.read()[-1]
        if self.report_format == 'rekap':
            name = 'report_purchase_report_rekap_xlsx2'
        elif self.report_format == 'spk':
            name = 'report_purchase_report_rekap_spk_xlsx2'
        else:
            name = 'report_purchase_report_rekap_spb_xlsx2'

        # return {
        #     'type'          : 'ir.actions.report.xml',
        #     'report_name'   : name,
        #     'datas': {
        #             'model': 'wizard.purchase.report',
        #             'id': self._context.get('active_ids') and self._context.get('active_ids')[0] or  self.id,
        #             'ids': self._context.get('active_ids') and self._context.get('active_ids') or[],
        #             'report_type': data['report_type'],
        #             'form': data
        #         },
        #     'nodestroy'     : False
        #     }
        res = self.env['report'].get_action(self, name)
        return res
wizard_purchase_report()


