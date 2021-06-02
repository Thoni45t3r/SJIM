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

class StockTransportInvoiceSummary(models.Model):
	_name = "stock.transport.invoice.summary"

	relasi = fields.Char("Relasi")
	partner_id = fields.Many2one("res.partner", "Transportir")
	product_qty = fields.Float("Total Quantity")
	transport_invoice_id = fields.Many2one("stock.transport.invoice")

class AccountInvoice(models.Model):
	_inherit    = ['account.invoice']

	transport_invoice_id = fields.Many2one("stock.transport.invoice")


class StockTransportInvoice(models.Model):
	_name = "stock.transport.invoice"
	_description = "Transport Invoice Creation"

	name = fields.Char("Name", default="Draft")
	partner_id = fields.Many2one('res.partner', string='Transportir', required=True)
	purchase_id = fields.Many2one('purchase.order', string='SPK')
	product_id = fields.Many2one('product.product', string='Product', required=False)
	partner_order_id = fields.Many2one('res.partner', string='Relasi')
	date_start = fields.Date('Start Date', required=True)
	date_end = fields.Date('End Date', required=True)
	journal_id = fields.Many2one('account.journal', string='Journal', domain=[('type','=','purchase')])
	# line_ids = fields.Many2many("stock.transport.move", 'transport_invoice_move_rel', 'transport_invoice_id', 'transport_move_id', "Transport Moves")
	line_ids = fields.One2many("stock.transport.move", 'transport_invoice_id', "Transport Moves")
	summary_line_ids = fields.One2many('stock.transport.invoice.summary', 'transport_invoice_id', string='Summary')
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'), ('validate', 'Validated')], string='State', default='draft')
	invoice_ids = fields.One2many('account.invoice', 'transport_invoice_id', String="Invoices")
	invoice_count = fields.Integer("Invoices", compute="_invoice_count")
	taxes_ids = fields.Many2many("account.tax", 'transport_invoice_id', string="Taxes")
	spk_ids = fields.One2many("purchase.order", "transport_invoice_id")
	spk_count = fields.Integer("SPK", compute="_spk_count")
	doc_type_id = fields.Many2one("res.document.type",string="Doc. Type")

	@api.onchange('partner_id')
	def onchange_partner(self):
		for record in self:
			if record.partner_id:
				record.taxes_ids = [(6,0,record.partner_id.default_invoice_taxes_ids.ids)]
			else:
				record.taxes_ids = False

	@api.model
	def create(self, vals):
		new_name = self.env['ir.sequence'].next_by_code('transport.invoice.sequence')
		vals['name'] = new_name
		result = super(StockTransportInvoice, self).create(vals)
		return result

	@api.depends('invoice_ids')
	def _invoice_count(self):
		for record in self:
			record.invoice_count = len(record.invoice_ids.ids)

	@api.depends('spk_ids')
	def _spk_count(self):
		for record in self:
			record.spk_count = len(record.spk_ids.ids)

	@api.multi
	def action_view_spk(self):
		self.ensure_one()
		return {
			'domain': [('id', 'in', self.spk_ids.ids)],
			'name': 'Created SPK Transport',
			'view_mode': 'tree,form',
			'res_model': 'purchase.order',
			'type': 'ir.actions.act_window',
			'target': 'current',
		}

	@api.multi
	def action_view_invoice(self):
		self.ensure_one()
		return {
			'domain': [('id', 'in', self.invoice_ids.ids)],
			'name': 'Created Invoice Transport',
			'view_mode': 'tree,form',
			'res_model': 'account.invoice',
			'type': 'ir.actions.act_window',
			'target': 'current',
		}

	@api.multi
	def generate_summary(self):
		self.ensure_one()
		grouped_lines = {}
		for x in self.summary_line_ids:
			x.unlink()
		for line in self.line_ids:
			if not line.transport_proceed_to_invoice:
				continue

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
				print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", value
				self.summary_line_ids = [(0,0,value)]

	@api.multi
	def action_confirm(self):
		for res in self:
			res.state = "confirmed"
			# res.line_ids = 
			for line in res.line_ids:
				if not line.transport_proceed_to_invoice:
					res.line_ids = [(3,line.id)]
			res.generate_summary()

	@api.multi
	def action_draft(self):
		for res in self:
			res.state = "draft"

	@api.multi
	def generate_data(self):
		for res in self:
			domain = [('product_id', '=', self.product_id.id),
				('partner_id', '=', self.partner_id.id),
				('date', '>=', self.date_start),
				('date', '<=', self.date_end),
				('invoiced', '=', False)]
			if res.partner_order_id:
				domain.append(('partner_order_id','=',res.partner_order_id.id))
			stock_transport_move = self.env['stock.transport.move'].search(domain)
			if not stock_transport_move:
				raise Warning('Data tidak ditemukan!')
			for data in stock_transport_move:
				data.transport_proceed_to_invoice = True
			res.line_ids = stock_transport_move
			res.generate_summary()

	@api.multi
	def action_validate(self):
		po_obj          = self.env['purchase.order']
		po_line_obj     = self.env['purchase.order.line']
		for record in self:
			warning = ''
			invoice_lines = []
			per_partner = {}
			label = {}
			
			for trans in record.line_ids:
				if not trans.product_spk_id:
					continue
				# Grouping per Partner
				if not per_partner.get(trans.partner_id, False):
					per_partner[trans.partner_id] = {}
				# Grouping per Contract
				if not per_partner[trans.partner_id].get(trans.contract_id, False):
					per_partner[trans.partner_id][trans.contract_id] = {}
				# Grouping per Src Location
				if not per_partner[trans.partner_id][trans.contract_id].get(trans.src_location_id, False):
					per_partner[trans.partner_id][trans.contract_id][trans.src_location_id] = {}
				# Grouping per Dest Location
				if not per_partner[trans.partner_id][trans.contract_id][trans.src_location_id].get(trans.dest_location_id, False):
					per_partner[trans.partner_id][trans.contract_id][trans.src_location_id][trans.dest_location_id] = {}
				# Grouping per Product
				product_spk = trans.product_spk_id
				if not per_partner[trans.partner_id][trans.contract_id][trans.src_location_id][trans.dest_location_id].get(trans.product_id, False):
					per_partner[trans.partner_id][trans.contract_id][trans.src_location_id][trans.dest_location_id][trans.product_id] = {}
				# Grouping per Product SPK
				if not per_partner[trans.partner_id][trans.contract_id][trans.src_location_id][trans.dest_location_id][trans.product_id].get(trans.product_spk_id, False):
					per_partner[trans.partner_id][trans.contract_id][trans.src_location_id][trans.dest_location_id][trans.product_id][trans.product_spk_id] = {}
				
				expense_account = product_spk.property_account_expense_id or product_spk.categ_id.property_account_expense_categ_id
				if not expense_account:
					raise Warning('Akun belum didefinisikan di product %s!'%product_spk.name)
				account_id = trans.accrued_account_id.id if (trans.accrued and trans.accrued_account_id) else expense_account.id
				# Grouping per Account
				if not per_partner[trans.partner_id][trans.contract_id][trans.src_location_id][trans.dest_location_id][trans.product_id][trans.product_spk_id].get(account_id, False):
					per_partner[trans.partner_id][trans.contract_id][trans.src_location_id][trans.dest_location_id][trans.product_id][trans.product_spk_id][account_id] = {
						'product_qty': 0.0,
						'price_unit': trans.price_unit,
					}
				if trans.rate_type=='by_weight':
					per_partner[trans.partner_id][trans.contract_id][trans.src_location_id][trans.dest_location_id][trans.product_id][trans.product_spk_id][account_id]['product_qty'] += trans.product_qty
				else:
					per_partner[trans.partner_id][trans.contract_id][trans.src_location_id][trans.dest_location_id][trans.product_id][trans.product_spk_id][account_id]['product_qty'] += 1

				trans.write({'invoiced': True})

			#set SPK
			spk_ids = []
			# Set invoice lines
			invoice_ids = []
			values_header = {
				'partner_id'            : record.partner_id.id,
				'doc_type_id'			: record.doc_type_id.id,
				'picking_type_id'       : record.doc_type_id.picking_type_id.id if record.doc_type_id.picking_type_id else False,
				'operating_unit_id'		: record.doc_type_id.picking_type_id.warehouse_id.operating_unit_id.id \
							if record.doc_type_id.picking_type_id
								and record.doc_type_id.picking_type_id and record.doc_type_id.picking_type_id.warehouse_id \
								and record.doc_type_id.picking_type_id.warehouse_id.operating_unit_id else False,
			}
			print ">>>>>>>>>>>>>>>>>>", values_header
			new_purchase_id = po_obj.create(values_header)
			record.purchase_id = new_purchase_id.id
			contract_ids = record.line_ids.mapped('contract_id')
			if new_purchase_id:
				for contract in contract_ids:
					lines_contract = record.line_ids.filtered(lambda x:x.contract_id == contract)
					list_asal = lines_contract.mapped('src_location_id')
					for asal in list_asal:
						lines_asal = lines_contract.filtered(lambda x:x.src_location_id == asal)
						list_tujuan = lines_asal.mapped('dest_location_id')
						for tujuan in list_tujuan:
							lines_tujuan = lines_asal.filtered(lambda x: x.dest_location_id == tujuan)
							list_product_spk = lines_tujuan.mapped('product_spk_id')
							for product_spk in list_product_spk:
								lines = lines_tujuan.filtered(lambda x: x.product_spk_id == product_spk)
								prices = list(set(lines.mapped('price_unit')))
								for price in prices:
									transport = lines.filtered(lambda x: x.price_unit == price)
									qty = 0.0
									for l in transport:
										if l.rate_type=='by_weight':
											qty += l.product_qty
										else:
											qty += 1
									values_line = {
										'order_id'          : new_purchase_id.id,
										'product_id'        : product_spk.id,
										'name'              : "Dari "+transport[0].src_location_id.name+" ke "+transport[0].dest_location_id.name+ ' Kontrak '+str(contract.name),
										'date_planned'      : datetime.now().strftime('%Y-%m-%d'),
										'product_qty'       : qty,
										'product_uom'       : product_spk.uom_id.id,
										'price_unit'        : price,
										'taxes_id'          : [(6, 0, record.taxes_ids.ids)],
										'state'             : 'draft',
									}
									label[product_spk]="Dari "+transport[0].src_location_id.name+" ke "+transport[0].dest_location_id.name+ ' Kontrak '+str(contract.name)
									po_line_obj.create(values_line)
					new_purchase_id.button_confirm()
					spk_ids.append(new_purchase_id.id)
					lines_contract.write({'purchase_id':new_purchase_id.id})
				# Invoice Lines
				invoice_lines = []
				for contract in per_partner.get(record.partner_id,{}).keys():
					for src_location in per_partner[record.partner_id][contract].keys():
						for dest_location in per_partner[record.partner_id][contract][src_location].keys():
							for product in per_partner[record.partner_id][contract][src_location][dest_location].keys():
								for product_spk in per_partner[record.partner_id][contract][src_location][dest_location][product].keys():
									for account_id in per_partner[record.partner_id][contract][src_location][dest_location][product][product_spk].keys():
										invoice_lines.append(
											[0,0,{
												'name': "Dari %s ke %s Kontrak %s"%(src_location.name, dest_location.name, contract.name),
												'product_id': product_spk.id,
												'quantity': per_partner[record.partner_id][contract][src_location][dest_location][product][product_spk][account_id]['product_qty'],
												'price_unit': per_partner[record.partner_id][contract][src_location][dest_location][product][product_spk][account_id]['price_unit'],
												'account_id': account_id,
												'invoice_line_tax_ids': [(6, 0, record.taxes_ids.ids)],
											}])
				invoice_vals = {
					'partner_id': record.partner_id.id,
					'date_invoice': fields.Date.context_today(self),
					'journal_id': record.journal_id.id,
					'account_id': record.partner_id.property_account_payable_id.id,
					'type': 'in_invoice',
					'invoice_line_ids': invoice_lines,
					'operating_unit_id': values_header['operating_unit_id'],
					'origin': new_purchase_id.name,
					}
				invoice = self.env['account.invoice'].sudo().create(invoice_vals)
				invoice_ids.append(invoice.id)

			new_purchase_id.order_line.write({'invoice_lines': [(6,0, invoice.invoice_line_ids.ids)]})

			record.write({
							'state': 'validate',
							'spk_ids': [(6,0, spk_ids)],
							'invoice_ids': [(6,0, invoice_ids)]
				})


			return {
				'domain': [('id', 'in', invoice_ids)],
				'name': 'Created Invoice Transport',
				'view_mode': 'tree,form',
				'res_model': 'account.invoice',
				'type': 'ir.actions.act_window',
				'target': 'current',
			}

	@api.multi
	def delete_all_lines(self):
		for res in self:
			for line in res.line_ids:
				line.transport_proceed_to_invoice = False
			res.line_ids = False
