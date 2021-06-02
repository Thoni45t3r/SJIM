# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

from odoo import api, fields, models, _

class WizardRequestPaymentInvoice(models.TransientModel):
    _name = 'wizard.request.payment.invoice'

    amount_to_pay = fields.Float('Amount to Pay', required=True)
    scheduled_date = fields.Date('Scheduled Date', required=True)
    date_due = fields.Date('Due Date')
    invoice_id = fields.Many2one('account.invoice', 'Invoice', required=False)
    invoice_advance_id = fields.Many2one('account.invoice.advance', 'Invoice Advance', required=False)
    currency_id = fields.Many2one('res.currency', 'Currency')

    @api.model
    def default_get(self, default_fields):
        Invoice = self.env['account.invoice']
        Advance = self.env['account.invoice.advance']
        context = self._context

        data = super(WizardRequestPaymentInvoice, self).default_get(default_fields)
        if context.get('active_id'):
            if context.get('invoice_req'):
                invoice = Invoice.browse(context['active_id'])
                data['invoice_id'] = invoice.id
            else:
                invoice = Advance.browse(context['active_id'])
                data['invoice_advance_id'] = invoice.id
            data['date_due'] = invoice.date_due
            data['currency_id'] = invoice.currency_id.id
            data['amount_to_pay'] = invoice.residual
        return data

    @api.multi
    def create_request(self):
        Request = self.env['account.payment.request']
        self.ensure_one()
        vals = {
            'invoice_id': self.invoice_id.id,
            'invoice_advance_id': self.invoice_advance_id.id,
            'amount': self.amount_to_pay,
            'currency_id': self.currency_id.id,
            'partner_id': self.invoice_id.partner_id.id or self.invoice_advance_id.partner_id.id,
            'date': self.scheduled_date,
            'date_due': self.date_due,
        }
        if self.invoice_id:
            vals['name'] = '%s%s'%(self.invoice_id.number, '('+self.invoice_id.origin+')' if self.invoice_id.origin else '')
        elif self.invoice_advance_id:
            vals['name'] = '%s%s' % (self.invoice_advance_id.number, '(' + self.invoice_advance_id.origin + ')' if self.invoice_advance_id.origin else '')
        Request.create(vals)
        return True
