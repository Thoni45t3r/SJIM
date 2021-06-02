from odoo import models, fields, api

class TaxPaymentLine(models.Model):
    _name = 'tax.payment.line'

    tax_payment_id = fields.Many2one('tax.payment', string='Tax Payment')
    name = fields.Char(string='Name')
    account_id = fields.Many2one('account.account', string='Account')
    amount = fields.Float(string='Amount')