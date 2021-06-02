# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2020  Konsaltén Indonesia <www.konsaltenindonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
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
import urllib3
from lxml import etree
import time

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    @api.multi
    def invoice_print_plantation(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'c10i_lhm.report_invoice_lhm')

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    account_account_location_ids = fields.Many2many('account.account', string='Daftar Account')
    account_location_type_name = fields.Char("Tipe Lokasi by Name", related="account_location_type_id.name", required=True)
    account_location_name = fields.Char("Lokasi by Name", related="account_location_id.name", required=True)
    
    @api.onchange('account_location_type_id')
    def _onchange_account_location_type_id(self):
        if self.account_location_type_id:
            self.account_location_id = False
            if self.account_location_type_id.account_ids:
                self.account_account_location_ids = self.account_location_type_id.account_ids.ids
            else:
                self.account_account_location_ids = self.env['account.account'].search([]).ids
            if self.account_location_type_id.no_location and (self.account_location_type_id.general_charge):
                self.account_id = False
            elif self.account_location_type_id.no_location and not (self.account_location_type_id.general_charge):
                pass
            else:
                self.account_id = self.account_location_type_id.account_id and self.account_location_type_id.account_id.id or False

    @api.onchange('account_location_id')
    def _onchange_account_location_id(self):
        if self.account_location_type_id.project and self.account_location_id:
            if self.account_location_type_id.project:
                project_data = self.env['mill.project'].search([('location_id', '=', self.account_location_id.id)])
                if project_data.categ_id.account_id:
                    self.account_account_location_ids = [(6, 0, [project_data.categ_id.account_id.id])]
                else:
                    self.account_account_location_ids = False