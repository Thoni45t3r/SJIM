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

class AccountPaymentInstruction(models.Model):
    _name = 'account.payment.instruction'
    _description = 'Payment Instruction'
    _order = 'payment_date desc'

    name = fields.Char('Number', default='/', copy=False)
    payment_date = fields.Date('Payment at', required=True, copy=False, readonly=True, states={'draft': [('readonly',False)]})
    journal_id = fields.Many2one('account.journal','Payment Method', required=True, readonly=True, states={'draft': [('readonly',False)]})
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id, readonly=True, states={'draft': [('readonly',False)]})
    line_ids = fields.One2many('account.payment.instruction.line', 'instruction_id', string='Request Lines', copy=False, readonly=True, states={'draft': [('readonly',False)]})

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id, readonly=True, states={'draft': [('readonly',False)]})
    state = fields.Selection([('draft','New'),('confirm','Confirmed'),('done','Posted'),('cancel','Cancelled')], string='Status', default='draft')

    request_ids = fields.Many2many('account.payment.request', 'request_payment_instruction_rel', 'instruction_id', 'request_id', string='Payment Request')
    payment_ids = fields.Many2many('account.payment', 'account_payment_payment_instruction_rel', 'instruction_id', 'payment_id', string='Vendor Payments')
    voucher_ids = fields.Many2many('account.voucher', 'account_voucher_payment_instruction_rel', 'instruction_id', 'voucher_id', string='Direct Payments')
    statement_line_id = fields.Many2one('account.bank.statement.line', 'Statement Line', readonly=True)
    payment_id = fields.Many2one('account.payment', 'Payment', readonly=True)
    amount = fields.Float('Total Amount', compute='_amount_total', store=True)

    check_number = fields.Char('Check Number')
    check_date = fields.Date('Check Date')

    @api.depends('line_ids','line_ids.amount')
    def _amount_total(self):
        for ins in self:
            amount_total = 0.0
            for line in ins.line_ids:
                amount_total += line.amount
            ins.amount = amount_total

    @api.onchange('journal_id', 'company_id')
    def onchange_journal(self):
        for ins in self:
            default_currency = ins.company_id.currency_id.id
            if ins.journal_id and ins.journal_id.currency_id:
                default_currency = ins.journal_id.currency_id.id
            ins.currency_id = default_currency

    @api.model
    def create(self, vals):
        journal = self.env['account.journal'].browse(vals['journal_id'])
        if journal.sequence_id:
            if not journal.sequence_id.active:
                raise UserError(_('Please activate the sequence of selected journal !'))
        else:
            raise UserError(_('Please define a sequence on the journal.'))
        if journal.type in ('cash','bank') and journal.receipt_sequence:
            if journal.receipt_sequence_id:
                if not journal.receipt_sequence_id:
                    raise UserError(_('Please activate the Receipt Sequence of selected journal !'))
            else:
                raise UserError(_('Please define a Receipt Sequence on the journal.'))
        date = vals.get('payment_date', datetime.now().strftime('%Y-%m-%d'))
        if journal.sequence_id:
            vals['name'] = journal.sequence_id.with_context(ir_sequence_date=date).next_by_id()
        return super(AccountPaymentInstruction, self).create(vals)

    @api.multi
    def button_outstanding(self):
        InstLine = self.env['account.payment.instruction.line']
        for ins in self:
            request_ids = ins.line_ids.mapped('request_id').ids
            if request_ids:
                domain_req = [('state','=','draft'),('id','not in', ins.request_ids.ids)]
            else:
                domain_req = [('state','=','draft')]
            requests = self.env['account.payment.request'].search(domain_req)
            for req in requests:
                if req.invoice_id or req.invoice_advance_id:
                    line_vals = {
                        'instruction_id': ins.id,
                        'request_id': req.id,
                        'user_id': req.user_id.id,
                        'partner_id': req.partner_id.id,
                        'invoice_id': req.invoice_id.id,
                        'invoice_advance_id': req.invoice_advance_id.id,
                        'account_id': req.invoice_id.account_id.id if req.invoice_id else req.invoice_advance_id.account_id.id,
                        'name': req.name + ('\n'+req.memo if req.memo else ''),
                    }
                    if ins.currency_id!=req.currency_id:
                        line_vals.update({'amount': req.currency_id.compute(req.amount, ins.currency_id, round=False)})
                    else:
                        line_vals.update({'amount': req.amount})
                    if req.invoice_id:
                        move_line_id = req.invoice_id.move_id.line_ids.filtered(lambda x: x.account_id.id==req.invoice_id.account_id.id).ensure_one()
                        line_vals.update({
                            'move_line_id': move_line_id.id,
                            'operating_unit_id': req.invoice_id.operating_unit_id.id,
                        })
                    else:
                        line_vals.update({
                            'move_line_id': req.invoice_advance_id.move_line_id.id,
                            'operating_unit_id': req.invoice_advance_id.operating_unit_id.id,
                        })
                    InstLine.create(line_vals)
                else:
                    for req_line in req.line_ids:
                        line_vals = {
                            'instruction_id': ins.id,
                            'request_id': req.id,
                            'user_id': req.user_id.id,
                            'partner_id': req.partner_id.id,
                            'account_id': req_line.account_id.id,
                            'name': req_line.name,
                            'account_location_type_id': req_line.account_location_type_id.id,
                            'account_location_id': req_line.account_location_id.id,
                            'operating_unit_id': req_line.operating_unit_id.id or req.operating_unit_id.ids,
                        }
                        if ins.currency_id!=req.currency_id:
                            line_vals.update({'amount': req.currency_id.compute(req_line.amount, ins.currency_id, round=False)})
                        else:
                            line_vals.update({'amount': req_line.amount})
                        InstLine.create(line_vals)
                request_ids.append(req.id)
            ins.request_ids = [(6,0,request_ids)]

    @api.multi
    def confirm(self):
        request_to_confirm = self.env['account.payment.request'].sudo()
        for ins in self:
            for line in ins.line_ids:
                request_to_confirm |= line.request_id
            ins.state = 'confirm'
            ins.request_ids = [(6, 0, request_to_confirm.ids)]
        request_to_confirm.write({'state': 'done'})
        return True

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        name = self.name
        return {
            'name': name,
            'date': self.payment_date,
            'ref': '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
        }

    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {
            'partner_id': False,
            'invoice_id': invoice_id,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
        }

    def _create_payment_entry_multi(self, amount, invoice, move, line):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = line.move_line_id and line.move_line_id.currency_id or False
        debit, credit, amount_currency, currency_id  = aml_obj.\
            with_context(date=self.payment_date, force_rate=self.payment_date).\
                compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)

        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, invoice_id=line.invoice_id.id)
        counterpart_aml_dict['partner_id'] = line.partner_id.id
        counterpart_aml_dict.update(line.with_context(self._context)._get_counterpart_move_line_vals(invoice=line.invoice_id))
        counterpart_aml_dict.update({'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)
        # TO DO : Tambahkan disini untuk handle Write off Amount

        if line.move_line_id and (line.invoice_id or line.invoice_advance_id):
            line.reconcile_payment_line(counterpart_aml)

    @api.model
    def balancing_move_line_create(self, amount, move_id):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit = credit = 0.0
        if amount < 0:
            debit = abs(amount)
            account_id = self.company_id.currency_exchange_journal_id.default_debit_account_id.id
        else:
            credit = amount
            account_id = self.company_id.currency_exchange_journal_id.default_credit_account_id.id
        if not account_id:
            raise UserError(_('Configuration Error !'), _('You need to define Expense/Income Account in Configuration'))
        move_line = {
            'journal_id': self.journal_id.id,
            'name': 'Balancing Rounding Difference',
            'account_id': account_id,
            'move_id': move_id,
            'partner_id': False,
            'debit': debit,
            'credit': credit,
            'date': self.payment_date,
            'amount_currency': 0.0,
            'currency_id': False,
            'operating_unit_id': self.journal_id.operating_unit_id.id,
        }
        aml_obj.create(move_line)

    def _create_liquidity_entry(self, total_amount, move):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = aml_obj.\
                with_context(date=self.payment_date, force_rate=self.payment_date).\
                    compute_amount_fields(total_amount, self.currency_id, self.company_id.currency_id, self.currency_id)
        liquidity_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        liquidity_aml_dict.update({
                'name': _('Payment Instruction'),
                'account_id': self.journal_id.default_credit_account_id.id,
                'journal_id': self.journal_id.id,
                'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                'payment_id': self._context.get('payment_id'),
                'operating_unit_id': self.journal_id.operating_unit_id.id,
            })
        aml_obj.create(liquidity_aml_dict)
        # check journal balance
        if self.currency_id.round(sum(move.line_ids.mapped('balance'))):
            self.balancing_move_line_create(sum(move.line_ids.mapped('balance')), move.id)
        move.post()
        return move

    @api.multi
    def account_payment_create(self, total_amount):
        payment_methods = self.journal_id.outbound_payment_method_ids
        payment_type = 'outbound'
        partner_type = 'supplier'
        sequence_code = 'account.payment.supplier.invoice'
        name = self.env['ir.sequence'].with_context(ir_sequence_date=self.payment_date).next_by_code(sequence_code)
        return {
            'name': name,
            'payment_type': payment_type,
            'payment_method_id': payment_methods and payment_methods[0].id or False,
            'partner_type': partner_type,
            'partner_id': False,
            'amount': abs(total_amount),
            'currency_id': self.currency_id.id,
            'payment_date': self.payment_date,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'communication': self.name,
            'state': 'reconciled',
        }

    @api.multi
    def post(self):
        AccountMove = self.env['account.move']
        Statement = self.env['account.bank.statement']
        for ins in self:
            move = AccountMove.create(self._get_move_vals())
            total_amount = 0.0
            amount = sum(ins.line_ids.mapped('amount'))
            ctx = {}
            ctx['payment_id'] = self.env['account.payment'].create(self.account_payment_create(amount)).id
            for line in ins.line_ids:
                ins.with_context(ctx)._create_payment_entry_multi(line.amount, line.invoice_id, move, line)
                total_amount += (line.amount * -1)
            # TOTAL AMOUNT
            ins.with_context(ctx)._create_liquidity_entry(total_amount, move)
            # CREATE STATEMENT LINE
            statement = Statement.search([('journal_id', '=', ins.journal_id.id),
                                             ('date', '=', ins.payment_date)], limit=1)
            if not statement:
                statement = Statement.with_context({'journal_id': ins.journal_id.id}).create(
                    {'journal_id': ins.journal_id.id, 'date': ins.payment_date})

            statement_line = self.env['account.bank.statement.line'].create({
                        'statement_id': statement.id,
                        'date': ins.payment_date,
                        'name': ins.name,
                        'partner_id': False,
                        'amount': total_amount,
                    })
            ins.statement_line_id = statement_line.id
            ins.state = 'done'
            ins.payment_id = ctx['payment_id']

    @api.multi
    def cancel(self):
        for ins in self:
            if ins.statement_line_id:
                if ins.statement_line_id.statement_id.state=='confirm':
                    raise UserError(_("Please set the bank statement to New before canceling."))
                ins.statement_line_id.unlink()
            if ins.payment_id:
                for move in ins.payment_id.move_line_ids.mapped('move_id'):
                    move.line_ids.remove_move_reconcile()
                    move.button_cancel()
                    move.unlink()
                ins.payment_id.move_name = False
                ins.payment_id.unlink()
            if ins.state=='confirm':
                for voucher in ins.voucher_ids:
                    voucher.number = False
                    voucher.unlink()
                for payment in ins.payment_ids:
                    payment.move_name = False
                    payment.unlink()
            elif ins.state=='done':
                for voucher in self.voucher_ids:
                    voucher.cancel_voucher()
                for payment in self.payment_ids:
                    payment.cancel()
            ins.state = 'cancel'
            ins.line_ids.mapped('request_id').write({'state': 'draft'})

    @api.multi
    def set_draft(self):
        for ins in self:
            if ins.state!='cancel':
                continue
            ins.state = 'draft'

    @api.multi
    def button_request(self):
        return {
            'name': _('Approved Requests'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment.request',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.request_ids.ids)],
        }

    @api.multi
    def button_payment(self):
        return {
            'name': _('Vendor Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.payment_ids.ids)],
        }

    @api.multi
    def button_voucher(self):
        return {
            'name': _('Direct Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.voucher',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.voucher_ids.ids)],
        }

    @api.multi
    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', 'in', self.mapped('payment_id').ids)],
        }

    @api.multi
    def print_request_approval(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_ins_request_approval',
            'datas': {
                'model': 'account.payment.instruction',
                'id': self.id,
                'ids': [self.id],
                'report_type': 'pdf',
                'form': {
                    'id': self.id,
                },
            },
            'nodestroy': False
        }

    @api.multi
    def print_instruction(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_ins_payment_instruction',
            'datas': {
                'model': 'account.payment.instruction',
                'id': self.id,
                'ids': [self.id],
                'report_type': 'pdf',
                'form': {
                    'id': self.id,
                },
            },
            'nodestroy': False
        }

    @api.multi
    def print_voucher(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_ins_voucher_payment',
            'datas': {
                'model': 'account.payment.instruction',
                'id': self.id,
                'ids': [self.id],
                'report_type': 'pdf',
                'form': {
                    'id': self.id,
                },
            },
            'nodestroy': False
        }

class AccountPaymentInstructionLine(models.Model):
    _name = 'account.payment.instruction.line'
    _description = 'Payment Instruction Line'

    instruction_id = fields.Many2one('account.payment.instruction', string='Instruction')
    currency_id = fields.Many2one('res.currency', related='instruction_id.currency_id', string='Currency')
    request_id = fields.Many2one('account.payment.request', string='Request')
    # user_id = fields.Many2one('res.users', related='request_id.user_id', string='Requested By', store=True)
    user_id = fields.Many2one('res.users', string='Requested By')
    # invoice_id = fields.Many2one('account.invoice', related='request_id.invoice_id', string='Invoice', store=True)
    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    # invoice_advance_id = fields.Many2one('account.invoice.advance', related='request_id.invoice_advance_id', string='Advance', store=True)
    invoice_advance_id = fields.Many2one('account.invoice.advance', string='Advance')
    # partner_id = fields.Many2one('res.partner', related='request_id.partner_id', string='Vendor', store=True)
    partner_id = fields.Many2one('res.partner', string='Vendor')
    account_id = fields.Many2one('account.account', string='Account')
    move_line_id = fields.Many2one('account.move.line', string='Account')
    amount = fields.Float(string='Amount to Pay')
    name = fields.Char('Description')

    account_location_type_id = fields.Many2one("account.location.type", "Tipe Lokasi", ondelete="restrict", readonly=True)
    account_location_id = fields.Many2one("account.location", "Lokasi", ondelete="restrict", readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', readonly=True)

    @api.model
    def reconcile_payment_line(self, counterpart_lines, writeoff_account=False, writeoff_journal=False):
        self.ensure_one()
        if not self.move_line_id:
            return False
        to_reconcile = self.env['account.move.line']
        to_reconcile |= self.move_line_id
        for move_line in counterpart_lines:
            to_reconcile |= move_line
        to_reconcile.reconcile(writeoff_account, writeoff_journal)

    def _get_counterpart_move_line_vals(self, invoice=False):
        return {
            'name': self.name,
            'account_id': self.account_id.id,
            'journal_id': self.instruction_id.journal_id.id,
            'currency_id': self.instruction_id.currency_id != self.instruction_id.company_id.currency_id and self.instruction_id.currency_id.id or False,
            'payment_id': self._context.get('payment_id'),
            'account_location_type_id': self.account_location_type_id.id,
            'account_location_id': self.account_location_id.id,
            'operating_unit_id': self.operating_unit_id.id,
        }