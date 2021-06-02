# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TaxPayment(models.Model):
    _name = 'tax.payment'
    _inherit = ['mail.thread']

    date_start = fields.Date(string='Tanggal Mulai', required=True)
    date_stop = fields.Date(string='Tanggal Akhir', required=True)
    account_ids = fields.Many2many(comodel_name='account.account', string='Account')
    move_line_ids = fields.Many2many(comodel_name='account.move.line', string='Account Move Line')
    line_ids = fields.One2many('tax.payment.line', 'tax_payment_id', string='Line Ids')
    amount_to_pay = fields.Float(compute='_amount_to_pay', string='Total', store=True)
    state = fields.Selection([('draft', 'Draft'),('open', 'Open'),('paid', 'Paid'),], string='Status', default='draft')
    voucher_id = fields.Many2one('account.voucher', string='Voucher')
    
    @api.multi
    def get_data(self):
        for doc in self:
            move_lines = self.env['account.move.line'].search([('account_id', 'in', doc.account_ids.ids),('date', '>=', doc.date_start),('date', '<=', doc.date_stop)]) 
            if move_lines:
                doc.move_line_ids = [(6, 0 , move_lines.ids)] 
            else:
                continue

            temp_lines = {}
            for line in move_lines:
                if line.account_id.id not in temp_lines.keys():
                    temp_lines.update({line.account_id.id:{
                        'name': "Balance %s periode between %s and  %s" % (line.name, doc.date_start, doc.date_stop), 
                        'account_id': line.account_id.id, 
                        'amount': 0.0,
                    }})
                temp_lines[line.account_id.id]['amount'] += (line.credit - line.debit)
            for line_vals in temp_lines.values():
                doc.line_ids = [(0, 0, line_vals)]
            
            prev_tax_payments = self.env['tax.payment'].search([('amount_to_pay', '<', 0),('state', '=', 'open'),('create_date', '<', doc.create_date)]) #tambah tgl
            if prev_tax_payments:
                record_tax = {}
                for line in prev_tax_payments.mapped('line_ids'):
                    if line.account_id.id not in record_tax.keys():
                        record_tax.update({line.account_id.id:{
                            'name': line.name, 
                            'account_id': line.account_id.id, 
                            'amount': line.amount
                        }})
                    record_tax[line.account_id.id]
                for line_vals in record_tax.values():
                    doc.line_ids = [(0, 0, line_vals)]
            else:
                continue
                    # lines = [(0, 0, temp_lines_values),(0, 0, record_tax_values)]
                    # lines2 = [(0, 0, line_vals)]
                    # doc.line_ids = lines
        doc.state = 'open'

    @api.depends('line_ids')
    def _amount_to_pay(self):
        for doc in self:
            amount_to_pay = sum(doc.line_ids.mapped('amount'))
            doc.amount_to_pay = amount_to_pay

    def set_open(self):
        for doc in self:
            doc.state = 'open'

    def set_draft(self):        
        for doc in self:
            doc.state = 'draft'
            self.env['tax.payment.line'].search([('tax_payment_id', '=', doc.id)]).unlink()

    @api.multi
    def _prepare_voucher_line(self, voucher_id):
        self.ensure_one()
        temp_lines = {}
        for line in self.line_ids:
            if line.account_id.id not in temp_lines.keys():
                temp_lines.update({line.account_id.id:{
                    'voucher_id': voucher_id,
                    'name': line.name,
                    'account_id': line.account_id.id,
                    'price_unit': line.amount,
                }})
        return temp_lines.values()
            

    @api.multi
    def action_create_payment(self, payment_date, journal_id):
        Voucher = self.env['account.voucher']
        VoucherLine = self.env['account.voucher.line']
        res = []
        for doc in self:
            if not doc.amount_to_pay:
                continue
            voucher_vals = doc._prepare_voucher(payment_date, journal_id)
            voucher = Voucher.create(voucher_vals)


            for line in doc._prepare_voucher_line(voucher.id):
                print ">>>>>>>>>", line
                voucher_line_vals = line
                voucher_line = VoucherLine.create(voucher_line_vals)

            doc.write({
                'voucher_id': voucher.id, 
                'state': 'paid'
            })
            res.append(voucher.id)
        return res

    @api.multi
    def _prepare_voucher(self, payment_date, journal_id):
        self.ensure_one()
        voucher_type = self.amount_to_pay < 0 
        journal = self.env['account.journal'].browse(journal_id)
        account_id = journal.default_debit_account_id.id
        # account_id = journal.default_credit_account_id.id
        return {
            'voucher_type': voucher_type,
            'date': payment_date,
            'account_date': payment_date,
            'pay_now': 'pay_now',
            'account_id': account_id,
            'journal_id': journal_id,
        }