# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2020  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Anggar Bagus Kurniawan <anggar.bagus@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.addons import decimal_precision as dp
import time
import os, base64, xlrd
import logging
_logger = logging.getLogger(__name__)

class StockTransportAccrueWizard(models.TransientModel):
    _name = "stock.transport.accrue.wizard"
    _description = "Transport Accrual Creation Wizard"

    partner_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier','=',True)], required=True)
    # partner_ids = fields.Many2many('res.partner', string='Vendor', domain=[('supplier','=',True)], required=False)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    date_start = fields.Date('Date Start', required=True)
    date_end = fields.Date('Date End', required=True)
    journal_id = fields.Many2one('account.journal', required=True, string='Journal')
    expense_account_id = fields.Many2one('account.account', required=True, string='Expense Account')
    accrued_account_id = fields.Many2one('account.account', required=True, string='Accrual Account')

    @api.multi
    def create_accrue(self):
        for record in self:
            warning = ''
            move_lines = []
            per_product = {}
            transport_moves = self.env['stock.transport.move'].search([
                ('partner_id', '=', record.partner_id.id),
                ('product_id', '=', record.product_id.id),
                ('date', '>=', record.date_start),
                ('date', '<=', record.date_end),
                ('accrued', '=', False),
                ('invoiced', '=', False)
                ])
            if not transport_moves:
                raise Warning('Data tidak ditemukan!')
            
            for trans in transport_moves:
                # Grouping per product
                if not per_product.get(trans.product_id.id, False):
                    per_product[trans.product_id.id] = {}
                    per_product[trans.product_id.id]['amount'] = 0
                per_product[trans.product_id.id]['amount'] = per_product[trans.product_id.id].get('amount',0)+trans.price_unit*trans.product_qty
                trans.write({'accrued': True,
                    'accrued_account_id': record.accrued_account_id.id})

            # Set move lines
            for key, item in per_product.items():
                # Debit Move
                move_lines.append(
                    [0,0,{
                    'account_id': record.expense_account_id.id,
                    'partner_id': record.partner_id.id,
                    'debit': item['amount'],
                    'credit': 0,
                    'name': self.env['product.product'].browse(key).name,
                    'journal_id': record.journal_id.id
                    }])

                # Credit Move
                move_lines.append(
                    [0,0,{
                    'account_id': record.accrued_account_id.id,
                    'partner_id': record.partner_id.id,
                    'debit': 0,
                    'credit': item['amount'],
                    'name': self.env['product.product'].browse(key).name,
                    'journal_id': record.journal_id.id
                    }])

            # Create JE
            if move_lines:
                move = self.env['account.move'].create(
                    {
                    'date': fields.Date.context_today(self),
                    'journal_id': record.journal_id.id,
                    'line_ids': move_lines,
                    }
                    )

                return {
                    'domain': [('id', 'in', [move.id])],
                    'name': 'Created Accrual Transport Entry',
                    'view_mode': 'tree,form',
                    'res_model': 'account.move',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                }
