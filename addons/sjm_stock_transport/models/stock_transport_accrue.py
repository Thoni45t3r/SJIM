import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.addons import decimal_precision as dp
import time
import os, base64, xlrd
import logging
_logger = logging.getLogger(__name__)

class StockTransportAccrueSummary(models.Model):
	_name = "stock.transport.accrue.summary"

	relasi = fields.Char("Relasi")
	partner_id = fields.Many2one("res.partner", "Transportir")
	product_qty = fields.Float("Total Quantity")
	transport_accrue_id = fields.Many2one("stock.transport.accrue")

class StockTransportAccrue(models.Model):
	_name = "stock.transport.accrue"
	_description = "Transport Accrual Creation"

	name = fields.Char("Name", default="Draft")
	partner_ids = fields.Many2many('res.partner', string='Vendor', domain=[('supplier','=',True)], required=True)
	# partner_ids = fields.Many2many('res.partner', string='Vendor', domain=[('supplier','=',True)], required=False)
	product_id = fields.Many2one('product.product', string='Product', required=True)
	date_start = fields.Date('Start Date', required=True)
	date_end = fields.Date('End Date', required=True)
	journal_id = fields.Many2one('account.journal', required=True, string='Journal')
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'), ('validate', 'Validated')], string='State', default='draft')
	line_ids = fields.One2many("stock.transport.move", 'transport_accrue_id', "Transport Moves")
	summary_line_ids = fields.One2many('stock.transport.accrue.summary', 'transport_accrue_id', string='Summary')
	move_id = fields.Many2one("account.move", string="Journal Entry")
	company_id = fields.Many2one('res.company', string='Company', required=True,
		default=lambda self: self.env['res.company']._company_default_get('account.account'))
	
	@api.model
	def create(self, vals):
		new_name = self.env['ir.sequence'].next_by_code('transport.accrue.sequence')
		vals['name'] = new_name
		result = super(StockTransportAccrue, self).create(vals)
		return result

	def print_report(self):
		return self.env['report'].get_action(self, 'report_transport_accrue_xlsx')

	@api.multi
	def action_confirm(self):
		for res in self:
			res.generate_summary()
			res.state = "confirmed"

	@api.multi
	def action_draft(self):
		for res in self:
			res.state = "draft"
			for x in res.summary_line_ids:
				x.unlink()

	@api.multi
	def generate_summary(self):
		self.ensure_one()
		grouped_lines = {}
		for x in self.summary_line_ids:
			x.unlink()
		for line in self.line_ids:
			if line.partner_id.id not in grouped_lines.keys():
				grouped_lines.update({line.partner_id.id: {}})
			if line.relasi not in grouped_lines[line.partner_id.id].keys():
				grouped_lines[line.partner_id.id].update({line.relasi: {
					'partner_id': line.partner_id.id,
					'relasi': line.relasi,
					'product_qty': 0.0,
					}})
			if line.rate_type=='by_weight':
				grouped_lines[line.partner_id.id][line.relasi]['product_qty'] += line.product_qty
			else:
				grouped_lines[line.partner_id.id][line.relasi]['product_qty'] += 1

		for partner_id in grouped_lines.keys():
			for value in grouped_lines[partner_id].values():
				self.summary_line_ids = [(0,0,value)]

	@api.multi
	def generate_data(self):
		for res in self:
			stock_transport_move = self.env['stock.transport.move'].search([('product_id', '=', self.product_id.id),
																			('partner_id', 'in', self.partner_ids.ids),
																			('date', '>=', self.date_start),
																			('date', '<=', self.date_end),
																			('accrued', '=', False),
																			('invoiced', '=', False)])
			if not stock_transport_move:
				raise Warning('Data tidak ditemukan!')
			res.line_ids = stock_transport_move
			res.generate_summary()

	@api.multi
	def action_validate(self):
		for record in self:
			warning = ''
			move_lines = []
			for partner in record.partner_ids:
				per_product = {}
				accrued_account = partner.default_account_ongkos_angkut_id
				if not accrued_account:
					raise Warning('Akun belum didefinisikan di partner %s!'%partner.name)
				for trans in record.line_ids.filtered(lambda x:x.partner_id == partner):
					# Grouping per product 
					if not per_product.get(trans.product_id, False):
						per_product.update({
							trans.product_id: {}
							})
					if not per_product[trans.product_id].get(trans.product_spk_id, False):
						per_product[trans.product_id].update({
								trans.product_spk_id: {
									'amount': 0.0
								}
							})
					if trans.rate_type == 'by_weight':
						amount = trans.price_unit * trans.product_qty
					else:
						amount = trans.price_unit * 1
					per_product[trans.product_id][trans.product_spk_id]['amount'] += amount
					trans.write({'accrued': True, 'accrued_account_id': accrued_account.id})
				# Set move lines
				for product in per_product.keys():
					for product_spk, item in per_product[product].items():
						expense_account = product_spk.property_account_expense_id or product_spk.categ_id.property_account_expense_categ_id
						if not expense_account:
							raise Warning('Akun belum didefinisikan di product %s!'%product_spk.name)

						# Debit Move
						move_lines.append(
							[0,0,{
							'account_id': expense_account.id,
							'partner_id': partner.id,
							'debit': item['amount'],
							'credit': 0,
							'name': product.name,
							'journal_id': record.journal_id.id
							}])

						# Credit Move
						move_lines.append(
							[0,0,{
							'account_id': accrued_account.id,
							'partner_id': partner.id,
							'debit': 0,
							'credit': item['amount'],
							'name': product.name,
							'journal_id': record.journal_id.id
							}])

			# Create JE
			if move_lines:
				move = self.env['account.move'].create(
					{
					'date': fields.Date.context_today(self),
					'journal_id': record.journal_id.id,
					'line_ids': move_lines,
					}
					)

				record.write({
								'state': 'validate',
								'move_id': move.id
							})
				return {
					'domain': [('id', 'in', [move.id])],
					'name': 'Created Accrual Transport Entry',
					'view_mode': 'tree,form',
					'res_model': 'account.move',
					'type': 'ir.actions.act_window',
					'target': 'current',
				}

	@api.multi
	def delete_all_lines(self):
		for res in self:
			res.line_ids = False