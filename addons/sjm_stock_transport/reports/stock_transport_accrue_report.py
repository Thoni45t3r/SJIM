from odoo import api, models, fields
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from calendar import monthrange
import itertools
import string

class ReportTransportAccrue(ReportXlsx):

	def generate_xlsx_report(self, workbook, data, objects):
		print("objects", objects)

		sheet = workbook.add_worksheet('Transport Accrue Report')
		sheet.set_column(1,1,5)
		sheet.set_column(2,11,30)
		bold = workbook.add_format({'bold': True})
		number_format = workbook.add_format({'num_format':'#,##0.00', 'border': 1})
		number_format_bold = workbook.add_format({'num_format':'#,##0.00', 'bold': True, 'bg_color': '#909191'})
		border = workbook.add_format({'border':1})
		border_bold = workbook.add_format({'border':1, 'bold':True})
		border2 = workbook.add_format({'border':1,'bold':True,'num_format':'#,##0.00'})
		format1 = workbook.add_format({'font_size': 16, 'bold': True})
		format2 = workbook.add_format({'bg_color': '#3aed2d', 'bold': True,'border':1, 'num_format':'#,##0.00'})
		format3 = workbook.add_format({'font_color': '#0c4dad', 'bold': True, 'font_size': 14})
		format4 = workbook.add_format({'bold': True, 'bg_color': '#8f8989', 'align':'center','valign':'vcenter', 'border':1, 'font_color': '#ffffff'})
		sheet.write(0, 1, objects.company_id.name, format1)
		sheet.write(1, 1, "TRANSPORT ACCRUE "+objects.name, format1)
		sheet.write(2, 1, 'PERIODE '+datetime.strptime(objects.date_start,'%Y-%m-%d').strftime('%d/%m/%Y')+' sampai '+datetime.strptime(objects.date_end,'%Y-%m-%d').strftime('%d/%m/%Y'), format3)
		sheet.write(1, 10, 'Print Date: '+datetime.now().strftime('%d/%m/%Y %H:%M:%S'), format3)

		row = 4
		sheet.write(row,1, "No.", format4)
		sheet.write(row,2, "Date", format4)
		sheet.write(row,3, "Vendor", format4)
		sheet.write(row,4, "Product", format4)
		sheet.write(row,5, "No. Kontrak", format4)
		sheet.write(row,6, "Asal Lokasi", format4)
		sheet.write(row,7, "Tujuan Lokasi", format4)
		sheet.write(row,8, "Rate Type", format4)
		sheet.write(row,9, "Product Qty (Akhir)", format4)
		sheet.write(row,10, "Price Unit", format4)
		sheet.write(row,11, "Total", format4)
		row+=1
		no=1
		# grand_total = 0
		for vendor in objects.partner_ids.sorted(lambda x: x.name):
			data_ids = objects.line_ids.filtered(lambda x: x.partner_id == vendor)
			total_vendor=0
			total_qty_vendor=0
			for data in data_ids.sorted(lambda x: x.date):
				subtotal = (data.product_qty if data.rate_type=='by_weight' else 1)*data.price_unit
				total_vendor+=subtotal
				total_qty_vendor+=data.product_qty
				sheet.write(row,1, no, border)
				sheet.write(row,2, datetime.strptime(data.date,'%Y-%m-%d').strftime('%d/%m/%Y'), number_format)
				sheet.write(row,3, data.partner_id.name, number_format)
				sheet.write(row,4, data.product_id.name, number_format)
				sheet.write(row,5, data.contract_id.name, number_format)
				sheet.write(row,6, data.src_location_id.name, number_format)
				sheet.write(row,7, data.dest_location_id.name, number_format)
				sheet.write(row,8, data.rate_type, number_format)
				sheet.write(row,9, (data.product_qty if data.rate_type=='by_weight' else 1), number_format)
				sheet.write(row,10, data.price_unit, number_format)
				sheet.write(row,11, subtotal, number_format)	
				row+=1
			if data_ids:
				sheet.merge_range(row,1,row,8, "Total per Vendor %s"%vendor.name, number_format_bold)
				sheet.write(row,9, total_qty_vendor, number_format_bold)
				sheet.write(row,10, ' ', number_format_bold)
				sheet.write(row,11, total_vendor, number_format_bold)
				row+=1

ReportTransportAccrue('report.report_transport_accrue_xlsx',
				 'stock.transport.accrue')
