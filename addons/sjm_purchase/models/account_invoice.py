from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare



class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	
	def _prepare_diff_invoice_line_from_po_line(self, line, diff_qty):
		if float_compare(diff_qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
			diff_qty = 0.0
		taxes = line.taxes_id
		invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes)
		invoice_line = self.env['account.invoice.line']
		data = {
			'purchase_line_id': line.id,
			'name': line.order_id.name+': '+line.name,
			'origin': line.order_id.origin,
			'uom_id': line.product_uom.id,
			'product_id': line.product_id.id,
			'account_id': invoice_line.with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
			'price_unit': line.order_id.currency_id.with_context(date=self.date_invoice).compute(line.price_unit, self.currency_id, round=False),
			'quantity': diff_qty,
			'discount': 0.0,
			'account_analytic_id': line.account_analytic_id.id,
			'analytic_tag_ids': line.analytic_tag_ids.ids,
			'invoice_line_tax_ids': invoice_line_tax_ids.ids
		}
		account = line.order_id.doc_type_id and line.order_id.doc_type_id.account_purchase_susut_id or False
		if account:
			data['account_id'] = account.id
		return data


	@api.onchange('invoice_line_ids')
	def _onchange_origin(self):
		purchase_ids = self.invoice_line_ids.mapped('purchase_id')
		# origins = [('%s(%s)'%(x.name,x.partner_ref) if x.partner_ref else x.name) for x in purchase_ids]
		origins = [(x.partner_ref or x.name) for x in purchase_ids]
		if purchase_ids:
			self.origin = ', '.join(origins)


	# Load all unsold PO lines
	@api.onchange('purchase_id')
	def purchase_order_change(self):
		if not self.purchase_id:
			return {}
		if not self.partner_id:
			self.partner_id = self.purchase_id.partner_id.id

		def_loc_type = self.env['account.location.type'].search([('code','=','-')], limit=1)

		new_lines = self.env['account.invoice.line']
		for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
			data = self._prepare_invoice_line_from_po_line(line)
			data.update({
				'account_location_type_id': def_loc_type.id,
				'account_account_location_ids': [(6,0,self.env['account.account'].search([]).ids)],
				})
			new_line = new_lines.new(data)
			new_line._set_additional_fields(self)
			new_lines += new_line
			
			if self.purchase_id.incoterm_id and self.purchase_id.incoterm_id.name=='LOCO':
				# CUSTOM CODE FOR SJIM
				invoicable_qty = line.product_qty - line.qty_invoiced
				if data['quantity'] < invoicable_qty:
					diff_qty = invoicable_qty - data['quantity']
					data2 = self._prepare_diff_invoice_line_from_po_line(line, diff_qty)
					data2.update({
						'account_location_type_id': def_loc_type.id,
						'account_account_location_ids': [(6,0,self.env['account.account'].search([]).ids)],
						})
					new_line = new_lines.new(data2)
					new_line._set_additional_fields(self)
					new_lines += new_line

		self.invoice_line_ids += new_lines
		# add purchase_id argument to parameter advance_outstanding() function 
		adv_lines, tax_lines = self.with_context(purchase_id=self.purchase_id.id, 
			execute_by='onchange', 
			inv_type='in_invoice', 
			partner_id=self.purchase_id.partner_id.id).advance_outstanding()
		new_adv_lines = self.env['account.invoice.register.advance']
		new_tax_lines = self.env['account.invoice.tax']
		if adv_lines:
			for val1 in adv_lines:
				new_adv_line = new_adv_lines.new(val1)
				new_adv_lines += new_adv_line
		if tax_lines:
			for val2 in tax_lines:
				new_tax_line = new_tax_lines.new(val2)
				new_tax_lines += new_tax_line
		self.register_advance_ids += new_adv_lines
		self.tax_line_ids += new_tax_lines
		# self.purchase_id = False
		return {}


	@api.multi
	def advance_outstanding(self):
		self.ensure_one()
		if self.env.context.get('inv_type',self.type)=='in_invoice':
			advance_type = 'in_advance'
		elif self.env.context.get('inv_type',self.type)=='out_invoice':
			advance_type = 'out_advance'
		else:
			return False

		purchase_id = self.env.context.get('purchase_id', self.purchase_id.id)
		advance_line = self.env['account.invoice.advance.line'].search([
			('invoice_id.partner_id','=',self.env.context.get('partner_id',self.partner_id.id)),('invoice_id.type','=',advance_type),
			('reconciled','=',False)])
		company_currency = self.journal_id.company_id.currency_id
		invoice_currenct = self.currency_id
		advance_lines = []
		for line in advance_line:
			# filter invoice_id == purchase_id
			if purchase_id:
				if line.invoice_id.purchase_id and line.invoice_id.purchase_id.id == purchase_id:
					vals = {
						'invoice_id': self.id,
						'advance_line_id': line.id,
						'amount_total': line.price_subtotal,
						'residual': line.residual,
						'amount': line.residual,
					}
					advance_lines.append(vals)
				else:
					continue
			else:
				vals = {
						'invoice_id': self.id,
						'advance_line_id': line.id,
						'amount_total': line.price_subtotal,
						'residual': line.residual,
						'amount': line.residual,
					}
				advance_lines.append(vals)
		if not self.env.context.get('execute_by'):
			self.register_advance_ids = advance_lines
		
		# Compute Taxes
		taxes_grouped = self.get_taxes_values()
		tax_lines = self.tax_line_ids.filtered('manual')
		for tax in taxes_grouped.values():
			tax_lines += tax_lines.new(tax)
		if not self.env.context.get('execute_by'):
			self.tax_line_ids = tax_lines

		return advance_lines, tax_lines