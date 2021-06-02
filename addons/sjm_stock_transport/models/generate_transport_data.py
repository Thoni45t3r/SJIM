import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.addons import decimal_precision as dp
import time
import os, base64, xlrd
import logging
_logger = logging.getLogger(__name__)

class GenerateTransportDataSummary(models.Model):
	_name = "generate.transport.data.summary"
	
	relasi = fields.Char("Relasi")
	partner_id = fields.Many2one("res.partner", "Transportir")
	product_qty = fields.Float("Total Quantity")
	generate_transport_id = fields.Many2one("generate.transport.data")

class GenerateTransportData(models.Model):
	_name = "generate.transport.data"
	_description = "Generate Transport Data"

	name = fields.Char(string="Name", default="Draft")
	start_date = fields.Date("Start Date")
	end_date = fields.Date("End Date")
	transaction_type_id = fields.Many2one("weighbridge.picking.type", string="Tipe Transaksi")
	partner_id = fields.Many2one('res.partner', string='Relasi')
	contract_id = fields.Many2one("weighbridge.contract", string="Kontrak")
	delivery_order_id = fields.Many2one("delivery.order.weighbridge", string="Delivery Order")
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')], string='State', default='draft')
	line_ids = fields.One2many("stock.transport.move", "generate_transport_id", string="Details")
	summary_line_ids = fields.One2many("generate.transport.data.summary", "generate_transport_id", string="Summaries")
	source_data = fields.Selection([('timbangan', "Timbangan"), ('import_timbang', "Import Timbang"), ('rekap_timbang', "Rekap Timbang")])
	product_spk_id = fields.Many2one('product.product', string='Product OA', domain=[('type', '=', 'service')])

	@api.model
	def create(self, vals):
		new_name = self.env['ir.sequence'].next_by_code('generate.transport.sequence')
		vals['name'] = new_name
		result = super(GenerateTransportData, self).create(vals)
		return result

	@api.onchange('transaction_type_id')
	def onchange_tipe(self):
		values = {}
		if self.transaction_type_id:
			if self.transaction_type_id.trans_type=='purchase':
				partner_domain=[('supplier','=',True)]
				contract_domain=[('trans_type','=',self.transaction_type_id.trans_type)]
			elif self.transaction_type_id.trans_type=='sale':
				partner_domain=[('customer','=',True)]
				contract_domain=[('trans_type','=',self.transaction_type_id.trans_type)]
			else:
				partner_domain = []
				contract_domain = []
			
			values.update({
				'domain': {'partner_id': str(partner_domain),
					'contract_id': str(contract_domain)}
				})
		self.contract_id = False
		self.partner_id = False
		return values

	@api.onchange('partner_id')
	def onchange_tipe(self):
		values = {}
		if self.partner_id:
			if self.transaction_type_id.trans_type=='purchase':
				contract_domain=[('related_purchase_id.partner_id','=',self.partner_id.id)]
			elif self.transaction_type_id.trans_type=='sale':
				contract_domain=[('related_sale_id.partner_id','=',self.partner_id.id)]
			else:
				contract_domain = []
			
			values.update({
				'domain': {'contract_id': str(contract_domain)}
				})
		self.contract_id = False
		return values

	@api.multi
	def action_confirm(self):
		for res in self:
			for line in res.line_ids:
				if not line.generate_proceed_to_move:
					if line.timbang_metro_id:
						line.timbang_metro_id.transport_move_id = False
					elif line.timbang_sampit_id:
						line.timbang_sampit_id.transport_move_id = False
					elif line.import_dharmala_line_id:
						line.import_dharmala_line_id.transport_move_id = False
					elif line.rekap_timbang_line_id:
						line.rekap_timbang_line_id.transport_move_id = False
					line.unlink()
			
			if any(x.state == 'not_valid' for x in res.line_ids):
				raise ValidationError(_("Periksa kembali, ada detail lines yang tidak valid"))
			res.generate_summary()
			res.state = "confirmed"

	@api.multi
	def generate_summary(self):
		self.ensure_one()
		grouped_lines = {}
		for x in self.summary_line_ids:
			x.unlink()
		for line in self.line_ids:
			if not line.generate_proceed_to_move:
				continue

			if line.partner_id.id not in grouped_lines.keys():
				grouped_lines.update({line.partner_id.id: {}})
			if line.relasi not in grouped_lines[line.partner_id.id].keys():
				grouped_lines[line.partner_id.id].update({line.relasi: {
					'partner_id': line.partner_id.id,
					'relasi': line.relasi,
					'product_qty': 0.0,
					}})
			grouped_lines[line.partner_id.id][line.relasi]['product_qty'] += line.product_qty

		for partner_id in grouped_lines.keys():
			for value in grouped_lines[partner_id].values():
				self.summary_line_ids = [(0,0,value)]

	@api.multi
	def action_draft(self):
		for res in self:
			for line in res.line_ids:
				if line.accrued or line.invoiced:
					raise ValidationError(_("Tidak bisa set draft, data sudah ditagihkan"))
			res.state = "draft"

	def prepare_value_timbang(self, timbang, src):
		do = self.env['delivery.order.weighbridge'].search([('name', '=', timbang.TIMBANG_DO)], limit=1)
		# print ".............", timbang.name
		partner_id = self.env['weighbridge.partner'].search([('name', '=', timbang.TIMBANG_TRANSPORTER)],limit=1)
		if not partner_id:
			raise ValidationError(_("Transporer %s belum ada pada master data relasi") %(timbang.TIMBANG_TRANSPORTER))
		if do:
			price_rate = self.env['stock.transport.rate'].search([
																	('partner_id', '=', partner_id.related_partner_id.id),
																	('start_date', '<=', timbang.TIMBANG_IN_DATE),
																	('end_date', '>=', timbang.TIMBANG_IN_DATE),
																	('src_location_id', '=', do.asal.id),
																	('dest_location_id', '=', do.tujuan.id),
																	('rate_type', '=', 'by_weight'),
																	('product_id', '=', timbang.product_id.id)], limit=1)
			if price_rate:
				price_unit = price_rate.rate
			else:
				price_unit = 0
		else:
			price_unit = 0

		if src == "timbang_metro_id":
			kontrak = self.env['weighbridge.contract'].search([('name', '=', timbang.TIMBANG_KONTRAK)])
		elif src == "timbang_sampit_id":
			kontrak = self.env['weighbridge.contract'].search([('name', '=', timbang.TIMBANG_SO)])

		if kontrak and kontrak.related_sale_id:
			partner_order_id = kontrak.related_sale_id.partner_id.id
		elif kontrak and kontrak.related_purchase_id:
			partner_order_id = kontrak.related_purchase_id.partner_id.id
		else:
			partner_order_id = False
		value = { 
				'date': timbang.TIMBANG_IN_DATE,
				'no_tiket': timbang.name,
				'no_plat': timbang.TIMBANG_NOKENDARAAN,
				'driver_name': timbang.TIMBANG_SUPIR,
				'relasi': timbang.TIMBANG_RELASI,
				'contract_id' : kontrak if kontrak else False,
				'partner_order_id': partner_order_id,
				'wb_do' : timbang.TIMBANG_DO,
				
				'src_location_id' : do.asal.id if do else False,
				'asal' : do.asal.name if do else False,
				'src_bruto': timbang.bruto_pks,
				'src_tare': timbang.tarra_pks,
				'src_netto': timbang.TIMBANG_NETTOPKS,
				'dest_location_id' : do.tujuan.id if do else False,
				'tujuan' : do.tujuan.name if do else False,
				'dest_bruto': timbang.TIMBANG_IN_WEIGHT if timbang.wb_picking_type_id.trans_type=='purchase' else timbang.TIMBANG_OUT_WEIGHT,
				'dest_tare': timbang.TIMBANG_IN_WEIGHT if timbang.wb_picking_type_id.trans_type=='sale' else timbang.TIMBANG_OUT_WEIGHT,
				'product_qty': timbang.TIMBANG_TOTALBERAT,
				
				'partner_id': partner_id.related_partner_id.id,
				'product_id': timbang.product_id.id,
				'product_spk_id': self.product_spk_id.id,

				'rate_type': 'by_weight',
				'price_unit': price_unit,
				'generate_proceed_to_move': True,
			}
		return value

	@api.multi
	def delete_all_lines(self):
		for data in self:
			for line in data.line_ids:
				if line.timbang_metro_id:
					line.timbang_metro_id.transport_move_id = False
				elif line.timbang_sampit_id:
					line.timbang_sampit_id.transport_move_id = False
				elif line.import_dharmala_line_id:
					line.import_dharmala_line_id.transport_move_id = False
				elif line.rekap_timbang_line_id:
					line.rekap_timbang_line_id.transport_move_id = False
			data.line_ids.unlink()

	@api.multi
	def generate_transport(self):
		current_ticket = self._context.get('current_ticket',{})
		for data in self:
			domain_timbang = [('TIMBANG_IN_DATE', '>=', data.start_date), ('TIMBANG_IN_DATE', '<=', data.end_date), ('transport_move_id', '=', False)]
			domain_manual = [('picking_date','>=',data.start_date),('picking_date','<=',data.end_date),('transport_move_id', '=', False),('import_id.state','=','done')]
			domain_rekap = [('valid_date','>=',data.start_date),('valid_date','<=',data.end_date),('transport_move_id', '=', False),('import_id.state','not in',['draft','imported'])]
			value = []
			# SOURCE DATA TIMBANGAN
			if data.source_data == "timbangan":
				domain_timbang_metro = domain_timbang[:]
				domain_timbang_sampit = domain_timbang[:]
				if data.transaction_type_id:
					# domain_timbang_metro.append(('TIMBANG_TIPETRANS', '=', data.transaction_type_id.name))
					domain_timbang_metro.append(('wb_picking_type_id', '=', data.transaction_type_id.id))
					# domain_timbang_sampit.append(('TIMBANG_TIPETRANS', '=', data.transaction_type_id.name))
					domain_timbang_sampit.append(('wb_picking_type_id', '=', data.transaction_type_id.id))
				if data.partner_id:
					domain_timbang_metro.append(('partner_id', '=', data.partner_id.id))
					domain_timbang_sampit.append(('partner_id', '=', data.partner_id.id))
				if data.contract_id:
					domain_timbang_metro.append(('wb_contract_id', '=', data.contract_id.id))
					# domain_timbang_metro.append(('TIMBANG_KONTRAK', '=', data.contract_id.name))
					domain_timbang_sampit.append(('wb_contract_id', '=', data.contract_id.id))
					# domain_timbang_sampit.append(('TIMBANG_SO', '=', data.contract_id.name))
				if data.delivery_order_id:
					domain_timbang_metro.append(('TIMBANG_DO', '=', data.delivery_order_id.name))
					domain_timbang_sampit.append(('TIMBANG_DO', '=', data.delivery_order_id.name))
				if current_ticket.get('timbang_metro'):
					if len(current_ticket['timbang_metro'])>1:
						domain_timbang_metro.append(('id', 'not in', current_ticket['timbang_metro']))
					else:
						domain_timbang_metro.append(('id', '!=', current_ticket['timbang_metro'][-1]))
				if current_ticket.get('timbang_sampit'):
					if len(current_ticket['timbang_sampit'])>1:
						domain_timbang_sampit.append(('id', 'not in', current_ticket['timbang_sampit']))
					else:
						domain_timbang_sampit.append(('id', '!=', current_ticket['timbang_sampit'][-1]))

				# METRO
				result_metro = self.env['weighbridge.scale.metro'].search(domain_timbang_metro)
				print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>", domain_timbang_metro
				print ",,,,,,,,,,,,,,,,,,,,,,,", result_metro
				for res in result_metro:
					if not res.wb_contract_id:
						continue
					if res.wb_contract_id.related_sale_id:
						# if res.wb_contract_id.related_sale_id.incoterm and res.wb_contract_id.related_sale_id.incoterm.name!='FRANCO':
						if False:
							continue
					elif res.wb_contract_id.related_purchase_id:
						if res.wb_contract_id.related_purchase_id.incoterm_id and res.wb_contract_id.related_purchase_id.incoterm_id.name!='LOCO':
							continue
					line_vals = self.prepare_value_timbang(res, "timbang_metro_id")
					line_vals.update({'timbang_metro_id': res.id})
					value.append((0,0,line_vals))

				data['line_ids']= value
				for line in data['line_ids']:
					if line.timbang_metro_id:
						line.timbang_metro_id.transport_move_id = line.id
				value = []					
				# SAMPIT
				result_sampit = self.env['weighbridge.scale.sampit'].search(domain_timbang_sampit)
				for res in result_sampit:
					if not res.wb_contract_id:
						continue
					if res.wb_contract_id.related_sale_id:
						# if res.wb_contract_id.related_sale_id.incoterm and res.wb_contract_id.related_sale_id.incoterm.name!='FRANCO':
						if False:
							continue
					elif res.wb_contract_id.related_purchase_id:
						if res.wb_contract_id.related_purchase_id.incoterm_id and res.wb_contract_id.related_purchase_id.incoterm_id.name!='LOCO':
							continue
					line_vals = self.prepare_value_timbang(res, "timbang_sampit_id")
					line_vals.update({'timbang_sampit_id': res.id})
					value.append((0,0,line_vals))
				data['line_ids']= value
				for line in data['line_ids']:
					if line.timbang_sampit_id:
						line.timbang_sampit_id.transport_move_id = line.id
				value = []					
			# SOURCE DATA IMPORT TIMBANG DHARMALA
			elif data.source_data == "import_timbang":
				if data.contract_id:
					domain_manual.append(('wb_contract_id.name', '=', data.contract_id.name))
				if data.partner_id:
					domain_manual.append(('partner_id', '=', data.partner_id.id))
				if data.delivery_order_id:
					domain_manual.append(('wb_do', '=', data.delivery_order_id.name))
				if current_ticket.get('import_darmala'):
					if len(current_ticket['import_darmala'])>1:
						domain_manual.append(('id', 'not in', current_ticket['import_darmala']))
					else:
						domain_manual.append(('id', '!=', current_ticket['import_darmala'][-1]))
				result_dharmala = self.env['manual.import.dharmala.line'].search(domain_manual)
				for res in result_dharmala:
					if res.wb_contract_id.related_sale_id:
						# if res.wb_contract_id.related_sale_id.incoterm and res.wb_contract_id.related_sale_id.incoterm.name!='FRANCO':
						if False:
							continue
					elif res.wb_contract_id.related_purchase_id:
						if res.wb_contract_id.related_purchase_id.incoterm_id and res.wb_contract_id.related_purchase_id.incoterm_id.name!='LOCO':
							continue
					do = self.env['delivery.order.weighbridge'].search([('name', '=', res.wb_do)], limit=1)
					partner_id = self.env['weighbridge.partner'].search([('name', '=', res.transporter)],limit=1)
					product_id = self.env['product.product'].search([('product_tmpl_id.default_code', '=', res.product)], limit=1)
					if not partner_id:
						raise ValidationError(_("Transporer %s belum ada pada master data relasi") %(res.transporter))
					if do:
						price_rate = self.env['stock.transport.rate'].search([
																				('partner_id', '=', partner_id.related_partner_id.id),
																				('start_date', '<=', datetime.strptime(res.date, "%d/%m/%Y")),
																				('end_date', '>=', datetime.strptime(res.date, "%d/%m/%Y")),
																				('src_location_id', '=', do.asal.id),
																				('dest_location_id', '=', do.tujuan.id),
																				('rate_type', '=', 'by_weight'),
																				('product_id', '=', product_id.id)], limit=1)
						if price_rate:
							price_unit = price_rate.rate
						else:
							price_unit = 0
					else:
						price_unit = 0

					kontrak = self.env['weighbridge.contract'].search([('name', '=', res.kontrak)])
					if kontrak and kontrak.related_sale_id:
						partner_order_id = kontrak.related_sale_id.partner_id.id
					elif kontrak and kontrak.related_purchase_id:
						partner_order_id = kontrak.related_purchase_id.partner_id.id
					else:
						partner_order_id = False

					value.append((0,0,{
						'date': datetime.strptime(res.date, "%d/%m/%Y"),
						'no_tiket': res.no_timbang,
						'no_plat': res.no_pol,
						'driver_name': '',
						'relasi': res.partner_id.name,
						'partner_order_id' : partner_order_id,
						'contract_id' : kontrak if kontrak else False,
						'wb_do' : res.wb_do,
						
						'src_location_id' : do.asal.id if do else False,
						'asal' : do.asal.name if do else False,
						'src_bruto': 0.0,
						'src_tare': 0.0,
						'src_netto': 0.0,
						'dest_location_id' : do.tujuan.id if do else False,
						'tujuan' : do.tujuan.name if do else False,
						'dest_bruto': float(res.bruto or 0),
						'dest_tare': float(res.tarra or 0),
						'product_qty': float(res.netto or 0),

						'partner_id': partner_id.related_partner_id.id,
						'product_id': product_id.id,
						'product_spk_id': data.product_spk_id.id,
						'rate_type': 'by_weight',
						'price_unit': price_unit,
						'import_dharmala_line_id': res.id,
						'generate_proceed_to_move': True,
				}))
				data['line_ids']= value
				for line in data['line_ids']:
					if line.import_dharmala_line_id:
						line.import_dharmala_line_id.transport_move_id = line.id
				value = []					
			elif data.source_data == "rekap_timbang":
				if data.partner_id:
					domain_rekap.append(('wb_partner_id.related_partner_id', '=', data.partner_id.id))
				if data.contract_id:
					domain_rekap.append(('wb_contract_id', '=', data.contract_id.id))
				if data.delivery_order_id:
					domain_rekap.append(('wb_do', '=', data.delivery_order_id.name))
				if current_ticket.get('rekap_timbang'):
					if len(current_ticket['rekap_timbang'])>1:
						domain_rekap.append(('id', 'not in', current_ticket['rekap_timbang']))
					else:
						domain_rekap.append(('id', '!=', current_ticket['rekap_timbang'][-1]))
				result_rekap = self.env['import.rekap.timbang.line'].search(domain_rekap)
				for res in result_rekap:
					if res.wb_contract_id.related_sale_id:
						# if res.wb_contract_id.related_sale_id.incoterm and res.wb_contract_id.related_sale_id.incoterm.name!='FRANCO':
						if False:
							continue
					elif res.wb_contract_id.related_purchase_id:
						if res.wb_contract_id.related_purchase_id.incoterm_id and res.wb_contract_id.related_purchase_id.incoterm_id.name!='LOCO':
							continue
					do = self.env['delivery.order.weighbridge'].search([('name', '=', res.wb_do)], limit=1)
					partner_id = self.env['weighbridge.partner'].search([('name', '=', res.transporter)],limit=1)
					product_id = self.env['product.product'].search([('product_tmpl_id.default_code', '=', res.product_name)], limit=1)
					if not partner_id:
						raise ValidationError(_("Transporer %s belum ada pada master data relasi") %(res.transporter))
					if do:
						price_rate = self.env['stock.transport.rate'].search([
																				('partner_id', '=', partner_id.related_partner_id.id),
																				('start_date', '<=', datetime.strptime(res.date, "%Y-%m-%d")),
																				('end_date', '>=', datetime.strptime(res.date, "%Y-%m-%d")),
																				('src_location_id.name', '=', res.src_location),
																				('dest_location_id.name', '=', res.dest_location),
																				('rate_type', '=', 'by_weight'),
																				('product_id', '=', product_id.id)], limit=1)
						if price_rate:
							price_unit = price_rate.rate
						else:
							price_unit = 0
					else:
						price_unit = 0

					kontrak = self.env['weighbridge.contract'].search([('name', '=', res.contract_number)])
					if kontrak and kontrak.related_sale_id:
						partner_order_id = kontrak.related_sale_id.partner_id.id
					elif kontrak and kontrak.related_purchase_id:
						partner_order_id = kontrak.related_purchase_id.partner_id.id
					else:
						partner_order_id = False

					value.append((0,0,{
						'date': datetime.strptime(res.date, "%Y-%m-%d"),
						'no_tiket': res.name,
						'no_plat': res.vehicle_number,
						'driver_name': '',
						'relasi': res.partner_name,
						'partner_order_id': partner_order_id,
						'contract_id' : kontrak if kontrak else False,
						'wb_do' : res.wb_do,
						
						'src_location_id' : self.env['stock.transport.location'].search([('name', '=', res.src_location)]) or False,
						'asal': res.src_location,
						'src_bruto': res.src_bruto,
						'src_tare': res.src_tarre,
						'src_netto': res.src_netto,
						'dest_location_id' : self.env['stock.transport.location'].search([('name', '=', res.dest_location)]) or False,
						'tujuan': res.dest_location,
						'dest_bruto': res.dest_bruto,
						'dest_tare': res.dest_tarre,
						'product_qty': res.dest_netto,

						'partner_id': partner_id.related_partner_id.id,
						'product_id': product_id.id,
						'product_spk_id': data.product_spk_id.id,
						'rate_type': 'by_weight',
						'price_unit': price_unit,

						'rekap_timbang_line_id': res.id,
						'generate_proceed_to_move': True,
				}))
				data['line_ids']= value
				for line in data['line_ids']:
					if line.rekap_timbang_line_id:
						line.rekap_timbang_line_id.transport_move_id = line.id

			data.generate_summary()

	@api.multi
	def update_line_value(self):
		for data in self:
			current_ticket = {'timbang_sampit': [], 'timbang_metro': [], 'import_darmala': [], 'rekap_timbang': []}
			for line in data.line_ids:
				print "................", line.timbang_metro_id
				if line.timbang_metro_id:
					current_ticket['timbang_metro'].append(line.timbang_metro_id.id)
				elif line.timbang_sampit_id:
					current_ticket['timbang_sampit'].append(line.timbang_sampit_id.id)
				elif line.import_dharmala_line_id:
					current_ticket['import_darmala'].append(line.import_dharmala_line_id.id)
				elif line.rekap_timbang_line_id:
					current_ticket['rekap_timbang'].append(line.rekap_timbang_line_id.id)
				else:
					continue
			print ">>>>>>>>>>>>>>>>>>>>>", current_ticket
			data.with_context(current_ticket=current_ticket).generate_transport()
			for line in data.line_ids:
				if line.timbang_metro_id:
					do = self.env['delivery.order.weighbridge'].search([('name', '=', line.wb_do)], limit=1)
					partner_id = self.env['weighbridge.partner'].search([('name', '=', line.timbang_metro_id.TIMBANG_TRANSPORTER)],limit=1)
					if not partner_id:
						raise ValidationError(_("Transporer %s belum ada pada master data relasi") %(line.timbang_metro_id.TIMBANG_TRANSPORTER))
					if do:
						price_rate = self.env['stock.transport.rate'].search([
																				('partner_id', '=', partner_id.related_partner_id.id),
																				('start_date', '<=', line.date),
																				('end_date', '>=', line.date),
																				('src_location_id', '=', do.asal.id),
																				('dest_location_id', '=', do.tujuan.id),
																				('rate_type', '=', 'by_weight'),
																				('product_id', '=', line.product_id.id)], limit=1)
						if price_rate:
							price_unit = price_rate.rate
						else:
							price_unit = 0
					else:
						price_unit = 0
					line.write({ 
						'partner_id': partner_id.related_partner_id.id,
						'product_id': line.timbang_metro_id.product_id.id,
						'product_spk_id': data.product_spk_id.id,
						'asal' : do.asal.name if do else False,
						'src_location_id' : do.asal.id if do else False,
						'tujuan' : do.tujuan.name if do else False,
						'dest_location_id' : do.tujuan.id if do else False,
						'wb_do' : line.timbang_metro_id.TIMBANG_DO,
						'product_qty': line.timbang_metro_id.TIMBANG_TOTALBERAT,
						'rate_type': 'by_weight',
						'price_unit': price_unit,
						'date': line.timbang_metro_id.TIMBANG_IN_DATE,
					})
				if line.timbang_sampit_id:
					do = self.env['delivery.order.weighbridge'].search([('name', '=', line.wb_do)], limit=1)
					partner_id = self.env['weighbridge.partner'].search([('name', '=', line.timbang_sampit_id.TIMBANG_TRANSPORTER)],limit=1)
					if not partner_id:
						raise ValidationError(_("Transporer %s belum ada pada master data relasi") %(line.timbang_sampit_id.TIMBANG_TRANSPORTER))
					if do:
						price_rate = self.env['stock.transport.rate'].search([
																				('partner_id', '=', partner_id.related_partner_id.id),
																				('start_date', '<=', line.timbang_sampit_id.TIMBANG_IN_DATE),
																				('end_date', '>=', line.timbang_sampit_id.TIMBANG_IN_DATE),
																				('src_location_id', '=', do.asal.id),
																				('dest_location_id', '=', do.tujuan.id),
																				('rate_type', '=', 'by_weight'),
																				('product_id', '=', line.product_id.id)], limit=1)
						if price_rate:
							price_unit = price_rate.rate
						else:
							price_unit = 0
					else:
						price_unit = 0
					line.write({ 
						'partner_id': partner_id.related_partner_id.id,
						'product_id': line.timbang_sampit_id.product_id.id,
						'product_spk_id': data.product_spk_id.id,
						'asal' : do.asal.name if do else False,
						'src_location_id' : do.asal.id if do else False,
						'tujuan' : do.tujuan.name if do else False,
						'dest_location_id' : do.tujuan.id if do else False,
						'wb_do' : line.timbang_sampit_id.TIMBANG_DO,
						'product_qty': line.timbang_sampit_id.TIMBANG_TOTALBERAT,
						'rate_type': 'by_weight',
						'price_unit': price_unit,
						'date': line.timbang_sampit_id.TIMBANG_IN_DATE,
					})
				if line.import_dharmala_line_id:
					do = self.env['delivery.order.weighbridge'].search([('name', '=', line.import_dharmala_line_id.wb_do)], limit=1)
					partner_id = self.env['weighbridge.partner'].search([('name', '=', line.import_dharmala_line_id.transporter)],limit=1)
					product_id = self.env['product.product'].search([('product_tmpl_id.default_code', '=', line.import_dharmala_line_id.product)], limit=1)
					if not partner_id:
						raise ValidationError(_("Transporer %s belum ada pada master data relasi") %(line.import_dharmala_line_id.transporter))
					if do:
						price_rate = self.env['stock.transport.rate'].search([
																				('partner_id', '=', partner_id.related_partner_id.id),
																				('start_date', '<=', datetime.strptime(line.import_dharmala_line_id.date, "%d/%m/%Y")),
																				('end_date', '>=', datetime.strptime(line.import_dharmala_line_id.date, "%d/%m/%Y")),
																				('src_location_id', '=', do.asal.id),
																				('dest_location_id', '=', do.tujuan.id),
																				('rate_type', '=', 'by_weight'),
																				('product_id', '=', product_id.id)], limit=1)
						if price_rate:
							price_unit = price_rate.rate
						else:
							price_unit = 0
					else:
						price_unit = 0

					line.write({
							'partner_id': partner_id.related_partner_id.id,
							'product_id': product_id.id,
							'product_spk_id': data.product_spk_id.id,
							'asal' : do.asal.name if do else False,
							'src_location_id' : do.asal.id if do else False,
							'tujuan' : do.tujuan.name if do else False,
							'dest_location_id' : do.tujuan.id if do else False,
							'wb_do' : line.import_dharmala_line_id.wb_do,
							'product_qty': line.import_dharmala_line_id.netto,
							'rate_type': 'by_weight',
							'price_unit': price_unit,
							'date': datetime.strptime(line.import_dharmala_line_id.date, "%d/%m/%Y"),
				})
				if line.rekap_timbang_line_id:
					do = self.env['delivery.order.weighbridge'].search([('name', '=', line.rekap_timbang_line_id.wb_do)], limit=1)
					partner_id = self.env['weighbridge.partner'].search([('name', '=', line.rekap_timbang_line_id.transporter)],limit=1)
					product_id = self.env['product.product'].search([('product_tmpl_id.default_code', '=', line.rekap_timbang_line_id.product)], limit=1)
					if not partner_id:
						raise ValidationError(_("Transporer %s belum ada pada master data relasi") %(line.rekap_timbang_line_id.transporter))
					if do:
						price_rate = self.env['stock.transport.rate'].search([
																				('partner_id', '=', partner_id.related_partner_id.id),
																				('start_date', '<=', datetime.strptime(line.rekap_timbang_line_id.date, "%Y-%m-%d")),
																				('end_date', '>=', datetime.strptime(line.rekap_timbang_line_id.date, "%Y-%m-%d")),
																				('src_location_id.name', '=', line.rekap_timbang_line_id.src_location),
																				('dest_location_id.name', '=', line.rekap_timbang_line_id.dest_location),
																				('rate_type', '=', 'by_weight'),
																				('product_id', '=', product_id.id)], limit=1)
						if price_rate:
							price_unit = price_rate.rate
						else:
							price_unit = 0
					else:
						price_unit = 0

					line.write({
							'partner_id': partner_id.related_partner_id.id,
							'product_id': product_id.id,
							'product_spk_id': data.product_spk_id.id,
							'asal': line.rekap_timbang_line_id.src_location,
							'src_location_id' : self.env['stock.transport.location'].search([('name', '=', line.rekap_timbang_line_id.src_location)]) or False,
							'tujuan': line.rekap_timbang_line_id.dest_location,
							'dest_location_id' : self.env['stock.transport.location'].search([('name', '=', line.rekap_timbang_line_id.dest_location)]) or False,
							'product_qty': line.rekap_timbang_line_id.dest_netto,
							'rate_type': 'by_weight',
							'price_unit': price_unit,
							'date': datetime.strptime(line.rekap_timbang_line_id.date, "%Y-%m-%d"),
				})

			data.generate_summary()