from odoo import api, models, fields
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from calendar import monthrange
import itertools
import string

class ReportTransportDataSPK(ReportXlsx):

	def get_data(self, objects):
		domain = [('date', '>=', objects.date_start), ('date', '<=', objects.date_end), ('purchase_id', '!=', False)]
		if objects.product_id:
			domain.append(('product_id','=',objects.product_id.id))
		result = self.env['stock.transport.move'].search(domain)
		return result

	def generate_xlsx_report(self, workbook, data, objects):
		print("objects", objects)

		sheet = workbook.add_worksheet('Transport Report SPK')
		# sheet.set_column(0,0,5)
		sheet.set_column(0,6,30)
		sheet.set_column(7,7,50)
		sheet.set_column(8,30,30)
		bold = workbook.add_format({'bold': True})
		number_format = workbook.add_format({'num_format':'#,##0.00'})
		number_format_bold = workbook.add_format({'num_format':'#,##0.00', 'bold': True, 'bg_color': '#909191'})
		border = workbook.add_format({'border':1})
		border_num = workbook.add_format({'border':1,'num_format':'#,##0.00'})
		border2 = workbook.add_format({'border':1,'bold':True,'num_format':'#,##0.00'})
		format1 = workbook.add_format({'font_size': 16, 'bold': True})
		format2 = workbook.add_format({'bg_color': '#8f8989', 'bold': True,'border':1, 'num_format':'#,##0.00'})
		format3 = workbook.add_format({'font_color': '#0c4dad', 'bold': True, 'font_size': 14})
		format4 = workbook.add_format({'bold': True, 'bg_color': '#8f8989', 'align':'center','valign':'vcenter', 'border':1, 'font_color': '#ffffff'})
		sheet.write(0, 0, objects.company_id.name, format1)
		sheet.write(1, 0, "REKAPITULASI SPK ONGKOS ANGKUT", format1)
		sheet.write(2, 0, 'PERIODE '+datetime.strptime(objects.date_start,'%Y-%m-%d').strftime('%d/%m/%Y')+' sampai '+datetime.strptime(objects.date_end,'%Y-%m-%d').strftime('%d/%m/%Y'), format3)
		sheet.write(1, 6, 'Print Date: '+datetime.now().strftime('%d/%m/%Y'), format3)

		data_ids = self.get_data(objects)
		# taxes_ids = data_ids.mapped('transport_invoice_id').mapped('taxes_ids')
		taxes_ids = data_ids.mapped('purchase_id').mapped('order_line').mapped('taxes_id')
		metro_ids = data_ids.filtered(lambda x: x.timbang_metro_id)
		sampit_ids = data_ids.filtered(lambda x: x.timbang_sampit_id)
		dharmala_ids = data_ids.filtered(lambda x: x.import_dharmala_line_id)
		rekap_ids = data_ids.filtered(lambda x: x.rekap_timbang_line_id)
		spk_ids = data_ids.mapped('purchase_id')

		row = 4

		number = 1
		sheet.write(row,0, "NO. SPK", format4)
		sheet.write(row,1, "TANGGAL SPK", format4)
		sheet.write(row,2, "VENDOR REFERENCE", format4)
		sheet.write(row,3, "NO. ITEM", format4)
		sheet.write(row,4, " ", format4)
		sheet.write(row,5, "NAMA BARANG", format4)
		sheet.write(row,6, "KODE BARANG", format4)
		sheet.write(row,7, "KETERANGAN / SPESIFIKASI BARANG", format4)
		sheet.write(row,8, "JUMLAH BARANG", format4)
		sheet.write(row,9, "SATUAN", format4)
		sheet.write(row,10, "MATA UANG", format4)
		sheet.write(row,11, "HARGA / UNIT", format4)
		sheet.write(row,12, "TOTAL HARGA", format4)
		sheet.write(row,13, "SUPPLIER", format4)
		sheet.write(row,14, "SYARAT PEMBAYARAN", format4)
		sheet.write(row,15, "KETERANGAN", format4)
		column = 16
		for tax in taxes_ids:
			sheet.write(row,column, tax.name, format4)
			column+=1
		sheet.write(row,column, "TOTAL PRICE", format4)
		sheet.write(row,column+1, "KLAIM", format4)
		sheet.write(row,column+2, "NO. FP", format4)
		sheet.write(row,column+3, "TANGGAL", format4)
		sheet.write(row,column+4, "PRICE FP", format4)
		sheet.write(row,column+5, "TOTAL PRICE - KLAIM", format4)
		sheet.write(row,column+6, "TANGGAL BAYAR", format4)
		row+=1
		
		# # Report Filling

		for spk in spk_ids.sorted(lambda x: x.date_order):
			for line in spk.order_line:
				sheet.write(row, 0, spk.name, border)
				sheet.write(row, 1, datetime.strptime(spk.date_order,'%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y'), border)
				sheet.write(row, 2, spk.partner_ref or '', border)
				sheet.write(row, 3, ' ', border)
				sheet.write(row, 4, spk.name, border)
				sheet.write(row, 5, line.product_id.name, border)
				sheet.write(row, 6, line.product_id.product_tmpl_id.default_code, border)
				sheet.write(row, 7, line.name, border)
				sheet.write(row, 8, line.product_qty, border_num)
				sheet.write(row, 9, line.product_uom.name, border)
				sheet.write(row, 10, spk.currency_id.name, border)
				sheet.write(row, 11, line.price_unit, border_num)
				sheet.write(row, 12, line.product_qty*line.price_unit, border_num)
				sheet.write(row, 13, spk.partner_id.name, border)
				sheet.write(row, 14, ' ', border)
				sheet.write(row, 15, ' ', border)
				column = 16
				total_tax = 0
				for tax in taxes_ids:
					line_tax = line.taxes_id.filtered(lambda x: x.id == tax.id)
					if line_tax:
						tax_price = line_tax._compute_amount(line.price_unit*line.product_qty, line.price_unit, line.product_qty)
						total_tax+=tax_price
						sheet.write(row,column,tax_price, border_num)
						column+=1
					else:
						sheet.write(row,column,0, border_num)
						column+=1

				total_harga = (line.price_unit*line.product_qty)+total_tax
				sheet.write(row, column, total_harga, border_num)
				sheet.write(row, column+1, ' ', border_num)
				sheet.write(row, column+2, " ", border)
				sheet.write(row, column+3, " ", border)
				sheet.write(row, column+4, " ", border)
				sheet.write(row, column+5, total_harga, border)
				sheet.write(row, column+6, " ", border)
				row+=1


ReportTransportDataSPK('report.report_transport_data_spk_xlsx',
				 'stock.transport.report.spk.wizard')
