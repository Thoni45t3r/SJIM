# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################
from openerp import models, fields, api, _
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report
import time

class wizard_report_outstanding_payment_request(models.TransientModel):
    _name           = "wizard.report.outstanding.payment.request"
    _description    = "Report Outstanding Payment Request"
    
    report_type     = fields.Selection(JasperDataParser.REPORT_TYPE, string="Document Type", default=lambda *a: 'xlsx', readonly=1)
    to_date         = fields.Date(string="To", default=lambda *a: time.strftime('%Y-%m-%d'))
    company_id      = fields.Many2one(comodel_name='res.company', string="Company", default=lambda self: self.env.user.company_id, readonly=1)

    @api.multi
    def create_report(self):
        data = self.read()[-1]
        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : 'report_outstanding_payment_request_xls',
            'datas': {
                    'model'         :'wizard.report.outstanding.payment.request',
                    'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or  self.id,
                    'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or[],
                    'report_type'   : data['report_type'],
                    'form'          : data,
                },
            'nodestroy'     : False
            }
wizard_report_outstanding_payment_request()

class wizard_report_outstanding_payment_request_comodity(models.TransientModel):
    _name           = "wizard.report.outstanding.payment.request.comodity"
    _description    = "Report Outstanding Payment Request COmodity"

    report_type     = fields.Selection(JasperDataParser.REPORT_TYPE, string="Document Type", default=lambda *a: 'xlsx', readonly=1)
    to_date         = fields.Date(string="To", default=lambda *a: time.strftime('%Y-%m-%d'))
    company_id      = fields.Many2one(comodel_name='res.company', string="Company", default=lambda self: self.env.user.company_id, readonly=1)

    @api.multi
    def create_report(self):
        data = self.read()[-1]
        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : 'report_outstanding_payment_request_comodity_xls',
            'datas': {
                    'model'         :'wizard.report.outstanding.payment.request.comodity',
                    'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or  self.id,
                    'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or[],
                    'report_type'   : data['report_type'],
                    'form'          : data,
                },
            'nodestroy'     : False
            }
wizard_report_outstanding_payment_request_comodity()