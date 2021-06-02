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

class WizardPaymentInstructionFromInvoice(models.TransientModel):
    _name = 'wizard.payment.instruction.from.invoice'

    instruction_id = fields.Many2one('account.payment.instruction', 'Instruction', required=True)
    partner_id = fields.Many2one('res.partner', 'Vendor', required=True)
    selected_invoice_ids = fields.Many2many('account.invoice', 'wizins_invoice_selected_rel', 'wizard_id', 'invoice_id', string='Selected Invoices')
    selected_invoice_advance_ids = fields.Many2many('account.invoice', 'wizins_advance_selected_rel', 'wizard_id', 'invoice_id', string='Selected Advance Invoices')
    invoice_ids = fields.Many2many('account.invoice', 'wizins_select_invoice_rel', 'wizard_id', 'invoice_id', string='Invoice(s)')
    invoice_advance_ids = fields.Many2many('account.invoice.advance', 'wizins_select_advance_invoice_rel', 'wizard_id', 'invoice_id', string='Invoice Advance(s)')

    @api.model
    def default_get(self, default_fields):
        Invoice = self.env['account.invoice']
        Advance = self.env['account.invoice.advance']
        Instruction = self.env['account.payment.instruction']
        context = self._context

        data = super(WizardPaymentInstructionFromInvoice, self).default_get(default_fields)
        if context.get('active_id'):
            instruction = Instruction.browse(context['active_id'])
            invoice_ids = []
            advance_ids = []
            for x in instruction.line_ids:
                if x.invoice_id:
                    invoice_ids.append(x.invoice_id.id)
                if x.invoice_advance_id:
                    advance_ids.append(x.invoice_advance_id.id)
            data['instruction_id'] = context['active_id']
            if invoice_ids:
                data['selected_invoice_ids'] = [(6,0,invoice_ids)]
            if advance_ids:
                data['selected_invoice_advance_ids'] = [(6,0,advance_ids)]
        return data

    @api.onchange('partner_id', 'selected_invoice_ids', 'selected_invoice_advance_ids')
    def change_partner(self):
        if self.partner_id:
            inv_domain = [('state','=','open'),('partner_id','=',self.partner_id.id)]
            if self.selected_invoice_ids:
                inv_domain.append(('id','not in',self.selected_invoice_ids.ids))
            invoices = self.env['account.invoice'].search(inv_domain)
            adv_domain = [('state','=','open'),('partner_id','=',self.partner_id.id)]
            if self.selected_invoice_advance_ids:
                inv_domain.append(('id','not in',self.selected_invoice_advance_ids.ids))
            advances = self.env['account.invoice.advance'].search(adv_domain)
            if invoices:
                self.invoice_ids = [(6,0,invoices.ids)]
            if advances:
                self.advance_ids = [(6,0,advances.ids)]

    @api.model
    def create(self, vals):
        if 'invoice_ids' in vals.keys():
            to_be_added = []
            for item in vals['invoice_ids']:
                if item[0]==1:
                    to_be_added.append(item[1])
                elif item[0]==6:
                    to_be_added.extend(item[2])
            if to_be_added:
                vals['invoice_ids'] = [(6,0, to_be_added)]
        if 'advance_ids' in vals.keys():
            to_be_added2 = []
            for item in vals['advance_ids']:
                if item[0]==1:
                    to_be_added2.append(item[1])
                elif item[0]==6:
                    to_be_added2.extend(item[2])
            if to_be_added2:
                vals['advance_ids'] = [(6,0, to_be_added2)]
        return super(WizardPaymentInstructionFromInvoice, self).create(vals)

    @api.multi
    def add_invoice(self):
        self.ensure_one()
        InstLine = self.env['account.payment.instruction.line']
        print ">>>>>>>>>>>>>>>>>>>.", self.invoice_ids
        for invoice in self.invoice_ids:
            line_vals = {
                'instruction_id': self.instruction_id.id,
                'request_id': False,
                'user_id': False,
                'partner_id': invoice.partner_id.id,
                'invoice_id': invoice.id,
                'invoice_advance_id': False,
                'account_id': invoice.account_id.id,
                'name': '%s%s'%(invoice.number, '('+invoice.origin+')' if invoice.origin else ''),
            }
            if self.instruction_id.currency_id!=invoice.currency_id:
                line_vals.update({'amount': invoice.currency_id.compute(invoice.residual, self.instruction_id.currency_id, round=False)})
            else:
                line_vals.update({'amount': invoice.residual})
            move_line_id = invoice.move_id.line_ids.filtered(lambda x: x.account_id.id==invoice.account_id.id).ensure_one()
            line_vals.update({
                'move_line_id': move_line_id.id,
                'operating_unit_id': invoice.operating_unit_id.id,
            })
            InstLine.create(line_vals)
        for advance in self.invoice_advance_ids:
            line_vals = {
                'instruction_id': self.instruction_id.id,
                'request_id': False,
                'user_id': False,
                'partner_id': advance.partner_id.id,
                'invoice_id': False,
                'invoice_advance_id': advance.id,
                'account_id': advance.account_id.id,
                'name': '%s%s'%(advance.number, '('+advance.origin+')' if advance.origin else ''),
            }
            if self.instruction_id.currency_id!=advance.currency_id:
                line_vals.update({'amount': advance.currency_id.compute(advance.residual, self.instruction_id.currency_id, round=False)})
            else:
                line_vals.update({'amount': advance.residual})
            line_vals.update({
                'move_line_id': advance.move_line_id.id,
                'operating_unit_id': advance.operating_unit_id.id,
            })
            InstLine.create(line_vals)
        return True