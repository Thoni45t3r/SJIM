# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

from odoo import models, fields, api, _

class AccountInvoice(models.Model):
    _inherit    = ['account.invoice']

    currency_name = fields.Char(related='currency_id.name', string="Currency Name", readonly=True)
    kmk_rate = fields.Float('Kurs KMK (IDR)', readonly=True, states={'draft':[('readonly','False')]})
    reference = fields.Char(string='Vendor Reference', copy=False,
                            help="The partner reference of this invoice.", readonly=True,
                            states={'draft': [('readonly', False)], 'open': [('readonly', False)], 'paid': [('readonly', False)]})

    @api.multi
    def print_report_kwitansi(self):
        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : 'report_nota_kwitansi_sjm',
            'datas'         : {
                'model'         : 'account.invoice',
                'id'            : self.id,
                'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                'name'          : self.number or "Report Nota Kwitansi",
                },
            'nodestroy'     : False
        }

    @api.multi
    def _write(self, vals):
        for invoice in self:
            new_number  = False
            if invoice.partner_id and vals.get('number', False):
                if vals.get('number', False).find('custom_partner') > 0:
                    partner_code    = str(invoice.partner_id.partner_code) if str(invoice.partner_id.partner_code) != 'False' else "INV"
                    new_number      = vals.get('number', False).replace(vals.get('number', False)[(vals.get('number', False).find('custom_partner')):(vals.get('number', False).find('custom_partner'))+14], str(partner_code))
                    if vals.get('number', False):
                        vals.update({'number' : new_number, 'move_name' : new_number})
            if invoice.move_id.name != new_number and new_number:
                invoice.move_id.write({'name' : new_number})

            if vals.get('reference', False) and invoice.reference != vals.get('reference', False):
                if invoice.move_id:
                    invoice.move_id.ref = vals['reference']

        res = super(AccountInvoice, self)._write(vals)
        return res

    # @api.onchange('reference')
    # def onchange_vendor_refernce(self):
    #     if self.reference:
    #         if not self.origin:
    #             self.origin = self.reference
    #         else:
    #             if self.origin.find('; ') > 0:
    #                 new_origin  = self.origin.replace(self.origin[29:], '; ' + self.reference)
    #                 self.origin = new_origin
    #             else:
    #                 new_origin  = self.origin + '; ' + self.reference
    #                 self.origin = new_origin

    @api.multi
    def compute_invoice_totals(self, company_currency, invoice_move_lines):
        if company_currency.name=='IDR' and self.currency_id!=company_currency and self.kmk_rate:
            total = 0
            total_currency = 0
            for line in invoice_move_lines:
                currency = self.currency_id
                if not (line.get('currency_id') and line.get('amount_currency')):
                    line['currency_id'] = currency.id
                    line['amount_currency'] = currency.round(line['price'])
                    line['price'] = line['price'] * self.kmk_rate

                if self.type in ('out_invoice', 'in_refund'):
                    total += line['price']
                    total_currency += line['amount_currency'] or line['price']
                    line['price'] = - line['price']
                else:
                    total -= line['price']
                    total_currency -= line['amount_currency'] or line['price']
            return total, total_currency, invoice_move_lines
        else:
            return super(AccountInvoice, self).compute_invoice_totals(company_currency, invoice_move_lines)