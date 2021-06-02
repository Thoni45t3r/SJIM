from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class account_financial_report(models.Model):
	_inherit = 'account.financial.report'

	report_balance_amount_type = fields.Selection([
		('year_to_date', 'Year to Date Balance'),
		('periodic', 'Only Show Balance on Selected Period')], string='Report Balance Options')

	def generate_financial_report(self, report, accounts):
		seq = 0
		type_account = []
		for acc in sorted(accounts, key = lambda x: x.code):
			if acc.user_type_id.type=='view':
				new_parent = self.create({'name': acc.name, 'type': 'sum', 'sequence': seq, 'sign': 1, 'parent_id': report.id})
				child_ids = self.env['account.account'].with_context(show_parent_account=True).search([('parent_id','=',acc.id)])
				account_ids = self.generate_financial_report(new_parent, child_ids)
				if account_ids:
					new_parent.write({'type': 'accounts', 'account_ids': [(6,0,account_ids)]})
			else:
				type_account.append(acc.id)
				seq += 1
		return type_account