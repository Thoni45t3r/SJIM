# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
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
from odoo.tools import float_compare, float_is_zero

class AccountPaymentRequest(models.Model):
    _name = 'account.payment.request'
    _description = 'Payment Request'
    _order = 'date desc'

    name = fields.Char('Origin', default='/', copy=False, readonly=True, states={'draft': [('readonly',False)]})
    date = fields.Date('Payment at', required=True, copy=False, readonly=True, states={'draft': [('readonly',False)]})
    date_due = fields.Date('Due Date', copy=False, readonly=True, states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('account.payment.request.line', 'request_id', string='Request Lines', copy=False, readonly=True, states={'draft': [('readonly',False)]})
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id, readonly=True, states={'draft': [('readonly',False)]})
    user_id = fields.Many2one('res.users','Requested By', default=lambda self: self.env.user.id)
    
    memo = fields.Char('Memo Payment', readonly=True, states={'draft': [('readonly',False)]})
    partner_id = fields.Many2one('res.partner', 'Vendor', readonly=True, states={'draft': [('readonly',False)]})

    invoice_id = fields.Many2one('account.invoice', 'Invoice', readonly=True, states={'draft': [('readonly',False)]})
    invoice_advance_id = fields.Many2one('account.invoice.advance', 'Advance', readonly=True, states={'draft': [('readonly',False)]})
    full_reconcile = fields.Boolean('Full Reconcile', readonly=True, states={'draft': [('readonly',False)]})
    amount = fields.Monetary('Amount to Pay', required=True, readonly=True, states={'draft': [('readonly',False)]})
    
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id, readonly=True, states={'draft': [('readonly',False)]})
    state = fields.Selection([('draft','Requested'),('done','Approved'),('cancel','Cancelled')], string='Status', default='draft')

    operating_unit_id = fields.Many2one('operating.unit', 'Default Operating Unit', default=lambda self: self.env['res.users'].operating_unit_default_get(
            self._uid),)

    @api.multi
    @api.constrains('operating_unit_id', 'company_id')
    def _check_company_operating_unit(self):
        for rec in self:
            if rec.company_id and rec.operating_unit_id and \
                    rec.company_id != rec.operating_unit_id.company_id:
                raise ValidationError(_('The Company in the voucher and in the'
                                        'Operating Unit must be the same.'
                                        ))

    @api.onchange('invoice_id','invoice_advance_id','full_reconcile')
    def onchange_invoice(self):
        self.ensure_one()
        if self.invoice_id or self.invoice_advance_id:
            self.currency_id = self.invoice_id.currency_id.id if self.invoice_id else self.invoice_advance_id.currency_id.id
            if self.full_reconcile:
                self.amount=self.invoice_id.residual if self.invoice_id else self.invoice_advance_id.residual

    @api.onchange('line_ids')
    def onchange_line(self):
        self.ensure_one()
        amount = 0.0
        if self.line_ids:
            for line in self.line_ids:
                amount += line.amount
            self.invoice_id = False
            self.invoice_advance_id = False
            self.full_reconcile = False
        self.amount = amount

    @api.model
    def create(self, vals):
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].next_by_code(self._name+'.sequence')
        if not vals.get('date_due',False):
            vals['date_due'] = vals['date']
        return super(AccountPaymentRequest, self).create(vals)

class AccountPaymentRequestLine(models.Model):
    _name = 'account.payment.request.line'
    _description = 'Payment Request Line'

    request_id = fields.Many2one('account.payment.request', 'Request Ref')
    currency_id = fields.Many2one('res.currency', related='request_id.currency_id', string='Currency')
    account_id = fields.Many2one('account.account', 'Account', required=True)
    name = fields.Char('Description')
    amount = fields.Monetary('Amount', required=True)

    account_location_type_id = fields.Many2one("account.location.type", "Tipe Lokasi", ondelete="restrict")
    account_location_id = fields.Many2one("account.location", "Lokasi", ondelete="restrict")
    account_location_type_no_location = fields.Boolean("Plantation Validator", related="account_location_type_id.no_location")
    account_account_location_ids = fields.Many2many('account.account', string='Daftar Account')
    account_location_type_name = fields.Char("Tipe Lokasi", related="account_location_type_id.name", required=True)
    account_location_name = fields.Char("Lokasi", related="account_location_id.name", required=True)

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', default=lambda self: self._context.get('default_operating_unit', False))

    @api.onchange('account_location_type_id')
    def _onchange_account_location_type_id(self):
        if self.account_location_type_id:
            self.account_location_id = False
            if self.account_location_type_id.no_location and (self.account_location_type_id.general_charge):
                self.account_id = False
            else:
                self.account_id = self.account_location_type_id.account_id and self.account_location_type_id.account_id.id or False
            if self.account_location_type_id.account_ids:
                self.account_account_location_ids = self.account_location_type_id.account_ids.ids
            else:
                self.account_account_location_ids = self.env['account.account'].search([]).ids

    @api.onchange('account_location_id')
    def _onchange_account_location_id(self):
        if self.account_location_type_id.project and self.account_location_id:
            if self.account_location_type_id.project:
                project_data = self.env['mill.project'].search([('location_id', '=', self.account_location_id.id)])
                if project_data.categ_id.account_id:
                    self.account_account_location_ids = [(6, 0, [project_data.categ_id.account_id.id])]
                else:
                    self.account_account_location_ids = False