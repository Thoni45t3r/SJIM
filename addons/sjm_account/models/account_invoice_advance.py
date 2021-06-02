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

class AccountInvoiceAdvance(models.Model):
    _inherit    = ['account.invoice.advance']

    reference = fields.Char(string='Vendor Reference', copy=False,
                            help="The partner reference of this invoice.", readonly=True,
                            states={'draft': [('readonly', False)],'open': [('readonly', False)], 'paid': [('readonly', False)]})

    @api.multi
    def write(self, update_vals):
        for inv in self:
            if update_vals.get('reference', False) and inv.reference!=update_vals.get('reference', False):
                if inv.move_id:
                    inv.move_id.ref = update_vals['reference']
        return super(AccountInvoiceAdvance, self).write(update_vals)

    @api.multi
    def action_invoice_open(self):
        new_number  = False
        res = super(AccountInvoiceAdvance, self).action_invoice_open()
        if self.partner_id and self.number:
            if self.number.find('custom_partner') > 0:
                partner_code    = str(self.partner_id.partner_code) if str(self.partner_id.partner_code) != 'False' else "INV-ADV"
                new_number      = self.number.replace(self.number[(self.number.find('custom_partner')):(self.number.find('custom_partner'))+14], str(partner_code))
        if new_number:
            self.number         = new_number
            self.move_id.name   = new_number
            self.move_name      = new_number
        return res
        
    @api.multi
    def print_report_kwitansi_advance(self):
        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : 'report_nota_kwitansi_advance_sjm',
            'datas'         : {
                'model'         : 'account.invoice.advance',
                'id'            : self.id,
                'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                'name'          : self.number or "Report Nota Kwitansi Advance",
                },
            'nodestroy'     : False
        }