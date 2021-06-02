from itertools import groupby
from datetime import datetime, timedelta
from collections import namedtuple
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, ValidationError
import time
import odoo.addons.decimal_precision as dp
import socket

from odoo.addons.mail.tests.common import TestMail
from odoo.tools import mute_logger


class GenerateReportSaleOrder(models.TransientModel):
	_name = "generate.report.sale.order"
	_description = "Generate Report Sale Order"

	type_report = fields.Selection([
				(1, 'Penjualan Per Customer'),
				(2, 'Detail Penjualan Product'),
				], string='Type Report')
	start_date  = fields.Date(string='Start Date')
	end_date  	= fields.Date(string='End Date')
	product_id	= fields.Many2one('product.product', string="Product")


	@api.multi
	def generatereport(self):
		
		data = self.read()[-1]
		if self.type_report == 1:
			name = 'report_generate_penjualan_customer_xls'
		else:
			name = 'report_generate_detail_penjualan_barang_xls'

		res = self.env['report'].get_action(self, name)
		return res



	def get_report_lines(self):
		lines = []

		POLine = self.env['purchase.order.line'].search([
			('date_order','>=',self.start_date),
			('date_order','<=',self.end_date),
			('product_id', '=', self.product_id.id)
		], order="date_order ASC")

		no = 1
		for x in POLine:

			lines.append({
				'no':no,
				'product':x.name
				})

			no +=1

		return lines