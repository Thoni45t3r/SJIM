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

class StockTransportInvoiceWizard(models.TransientModel):
    _name = "stock.transport.invoice.wizard"
    _description = "Transport Invoice Creation Wizard"

    partner_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier','=',True)], required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    date_start = fields.Date('Date Start', required=True)
    date_end = fields.Date('Date End', required=True)
    journal_id = fields.Many2one('account.journal', required=True, string='Journal', domain=[('type','=','purchase')])
    expense_account_id = fields.Many2one('account.account', required=True, string='Expense Account')

    @api.multi
    def create_invoice(self):
        for record in self:
            warning = ''
            invoice_lines = []
            per_partner = {}
            transport_moves = self.env['stock.transport.move'].search([
                ('partner_id', '=', record.partner_id.id),
                ('product_id', '=', record.product_id.id),
                ('date', '>=', record.date_start),
                ('date', '<=', record.date_end),
                ('invoiced', '=', False)
                ])
            if not transport_moves:
                raise Warning('Data tidak ditemukan!')
            
            for trans in transport_moves:
                # Grouping per Partner
                if not per_partner.get(trans.partner_id, False):
                    per_partner[trans.partner_id] = {}

                # Grouping per Product
                if not per_partner[trans.partner_id].get(trans.product_id, False):
                    per_partner[trans.partner_id][trans.product_id] = {}

                account_id = trans.accrued_account_id.id if (trans.accrued and trans.accrued_account_id) else record.expense_account_id.id
                # Grouping per Account
                if not per_partner[trans.partner_id][trans.product_id].get(account_id, False):
                    per_partner[trans.partner_id][trans.product_id][account_id] = {}
                    per_partner[trans.partner_id][trans.product_id][account_id]['amount'] = 0
                per_partner[trans.partner_id][trans.product_id][account_id]['amount'] = per_partner[trans.partner_id][trans.product_id][account_id].get('amount',0) + trans.price_unit*trans.product_qty
                trans.write({'invoiced': True})
    
            # Set invoice lines
            invoice_ids = []
            for partner in per_partner.keys():
                # Invoice Lines
                invoice_lines = []
                for product in per_partner[partner].keys():
                    for account_id in per_partner[partner][product].keys():
                        invoice_lines.append(
                            [0,0,{
                            'name': "Transport %s"%product.name,
                            'product_id': product.id,
                            'quantity': 1,
                            'price_unit': per_partner[partner][product][account_id]['amount'],
                            'account_id': account_id,
                            }])
                invoice_vals = {
                    'partner_id': partner.id,
                    'date_invoice': fields.Date.context_today(self),
                    'journal_id': record.journal_id.id,
                    'account_id': partner.property_account_payable_id.id,
                    'type': 'in_invoice',
                    'invoice_line_ids': invoice_lines,
                    }
                invoice = self.env['account.invoice'].sudo().create(invoice_vals)
                invoice_ids.append(invoice.id)

            return {
                'domain': [('id', 'in', invoice_ids)],
                'name': 'Created Invoice Transport',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
