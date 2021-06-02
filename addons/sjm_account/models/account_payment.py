from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import openerp.addons.decimal_precision as dp
from datetime import datetime

class account_payment(models.Model):
    _inherit = "account.payment"

    # @api.multi
    # def confirm(self):
    # 	res = super(account_payment, self).confirm()
    # 	for rec in self:
    # 		payment_ref_list = []
    # 		if rec.register_ids:
    # 			for l in rec.register_ids:
    # 				if l.invoice_id:
    # 					check = False
    # 					if l.reconcile or (l.payment_difference and l.writeoff_account_id) or (l.amount_to_pay>=l.residual):
    # 						check = True
    # 					desc = "%s %s %s"%('Pelunasan' if check else 'Pembayaran', l.origin, l.amount_to_pay)
    # 					payment_ref_list.append(desc)
    # 				elif l.invoice_advance_id:
    # 					desc = "DP %s %s"%(l.origin, l.amount_to_pay)
    # 					payment_ref_list.append(desc)
    # 				else:
    # 					continue
    # 			if payment_ref_list:
    # 				rec.communication = "; ".join(payment_ref_list)
    # 	return res