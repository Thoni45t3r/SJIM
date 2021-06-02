# -*- encoding: utf-8 -*-
# © 2018-2019 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
from odoo import api, fields, models, _

class AccountFinancialReports(models.Model):
    _name = 'account.financial.report.type'

    name = fields.Char('Report Name')
    code = fields.Char('Report Code')
    active = fields.Boolean(default=True)
    query = fields.Text('SQL Query')

