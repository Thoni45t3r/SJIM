# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2020  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Anggar Bagus Kurniawan <anggar.bagus@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.addons import decimal_precision as dp
import time

class StockTransportMove(models.Model):
	_name = "stock.transport.move"
	_description = "Transport Move"

	generate_transport_id = fields.Many2one("generate.transport.data")
	rate_type = fields.Selection([('by_weight','By Weight'),('by_delivery','By Delivery'),('by_distance','By Distance')], string='Rate Type', required=True, default='by_delivery')
	date = fields.Date('Date', required=True)
	partner_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier','=',True)], required=True)
	product_id = fields.Many2one('product.product', string='Product', required=True)

	no_tiket = fields.Char('No. Tiket')
	no_plat = fields.Char('No. Plat')
	driver_name = fields.Char('Nama Supir')
	relasi = fields.Char('Relasi')
	partner_order_id = fields.Many2one('res.partner', string='Relasi')
	contract_id = fields.Many2one('weighbridge.contract', string="Kontrak")
	wb_do = fields.Char(string="Delivery Order")
	
	src_location_id = fields.Many2one('stock.transport.location', string='Source')
	asal = fields.Char(string="Asal Barang")
	src_bruto = fields.Float(string='Bruto Asal')
	src_tare = fields.Float(string='Tare Asal')
	src_netto = fields.Float(string='Netto Asal')
	
	dest_location_id = fields.Many2one('stock.transport.location', string='Dest.')
	tujuan = fields.Char(string="Tujuan Akhir")
	dest_bruto = fields.Float(string='Bruto Akhir')
	dest_tare = fields.Float(string='Tare Akhir')
	product_qty = fields.Float(required=True, string='Netto Akhir')

	difference_qty = fields.Float('Susut', compute='_compute_diff_qty')

	price_unit = fields.Float('Price Unit', digits=dp.get_precision('Product Price'))
	timbang_metro_id = fields.Many2one("weighbridge.scale.metro", string="Timbangan Metro")
	timbang_sampit_id = fields.Many2one("weighbridge.scale.sampit", string="Timbangan Sampit")
	rekap_timbang_line_id = fields.Many2one("import.rekap.timbang.line", string="Import Rekap Timbang Line")
	import_dharmala_line_id = fields.Many2one("manual.import.dharmala.line", string="Import Darmala Line")
	
	error_note = fields.Text(string="Error Note", compute="_get_state")
	state = fields.Selection([('valid', 'Valid'), ('not_valid', 'Not Valid')], string="Status", compute="_get_state", store=True)
	
	accrued = fields.Boolean('Accrue')
	move_id = fields.Many2one('account.move', string='Journal Entry')
	accrued_account_id = fields.Many2one('account.account', 'Accrued Account')
	invoiced = fields.Boolean('Invoice')
	invoice_id = fields.Many2one('account.invoice', string='Invoice')
	
	transport_accrue_id = fields.Many2one("stock.transport.accrue", "Stock Transport Accrue", ondelete='restrict')
	transport_invoice_id = fields.Many2one("stock.transport.invoice", "Stock Transport Invoice", ondelete='restrict')
	product_spk_id = fields.Many2one('product.product', string='Product OA', ondelete='restrict')
	purchase_id = fields.Many2one('purchase.order', string="SPK", ondelete='restrict')
	
	notes = fields.Text(string="Note")
	generate_proceed_to_move = fields.Boolean(string='Proceed?')
	transport_proceed_to_invoice = fields.Boolean(string='Proceed?')

	@api.depends('src_location_id', 'dest_location_id', 'price_unit')
	def _get_state(self):
		for data in self:
			data.state = "valid" if data.src_location_id and data.dest_location_id and data.price_unit else 'not_valid'
			error_note = []
			if not data.src_location_id:
				error_note.append("Asal Lokasi tidak ditemukan di Master Data Lokasi")
			if not data.dest_location_id:
				error_note.append("Tujuan Lokasi tidak ditemukan di Master Data Lokasi")
			if not data.price_unit:
				error_note.append("Price Unit tidak ditemukan di Master Data Rate")
			data.error_note = "\n".join(error_note) if error_note else ""

	@api.depends('src_netto', 'product_qty')
	def _compute_diff_qty(self):
		for data in self:
			data.difference_qty = data.src_netto - data.product_qty

	# @api.multi
	# def action_unlink(self):
	# 	for record in self:
	# 		record.write({'transport_invoice_id' : False})