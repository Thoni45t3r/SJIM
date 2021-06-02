# -*- coding: utf-8 -*-
######################################################################################################
#
#   @author Pranoto Tahrir Fathoni <Thoni.45t3r@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################
from openerp import models, fields, api, _
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report
import time

class wizard_general_ledger_by_locations(models.TransientModel):
    _name           = "wizard.general.ledger.by.locations"
    _description    = "Report General Ledger By Locations"
    
    report_type     = fields.Selection(JasperDataParser.REPORT_TYPE, string="Document Type", default=lambda *a: 'xlsx')
    from_date       = fields.Date(string="From", default=lambda *a: time.strftime('%Y-%m-%d'))
    to_date         = fields.Date(string="To", default=lambda *a: time.strftime('%Y-%m-%d'))
    target_move     = fields.Selection([('posted', 'All Posted Entries'),
                                        ('all', 'All Entries'),
                                        ], string='Target Moves', required=True, default='posted')
    company_id      = fields.Many2one(comodel_name='res.company', string="Company", default=lambda self: self.env.user.company_id)
    operating_unit_ids     = fields.Many2many('operating.unit', string="Operating Unit")
    
    @api.multi
    def create_report(self):
        data = self.read()[-1]
        name = 'report_general_ledger_by_locations'
        target = "'posted'"
        if data['report_type'] in ['xls', 'xlsx']:
            name = 'report_general_ledger_by_locations'
        if data['target_move'] == "all":
            target = "'posted','draft'"
        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : name,
            'datas': {
                    'model'         :'wizard.general.ledger.by.locations',
                    'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or  self.id,
                    'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or[],
                    'report_type'   : data['report_type'],
                    'form'          : data,
                    'target_move'   : target,
                },
            'nodestroy'     : False
            }

wizard_general_ledger_by_locations()