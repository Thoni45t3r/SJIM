from odoo import api, models, fields
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from calendar import monthrange
import itertools
import string

class ReportTransportDataPurchase(ReportXlsx):

	def get_data(self, objects):
		domain = [('date', '>=', objects.date_start), ('date', '<=', objects.date_end), ('contract_id.trans_type', '=', 'purchase')]
		if objects.product_id:
			domain.append(('product_id','=',objects.product_id.id))
		result = self.env['stock.transport.move'].search(domain)
		return result

	def generate_xlsx_report(self, workbook, data, objects):
		print("objects", objects)

		sheet = workbook.add_worksheet('Transport Report Pembelian')
		sheet.set_column(0,0,5)
		sheet.set_column(1,30,30)
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
		sheet.write(1, 0, "REKAPITULASI PENIMBANGAN PEMBELIAN", format1)
		sheet.write(2, 0, 'PERIODE '+datetime.strptime(objects.date_start,'%Y-%m-%d').strftime('%d/%m/%Y')+' sampai '+datetime.strptime(objects.date_end,'%Y-%m-%d').strftime('%d/%m/%Y'), format3)
		sheet.write(1, 6, 'Print Date: '+datetime.now().strftime('%d/%m/%Y'), format3)

		data_ids = self.get_data(objects)
		# taxes_ids = data_ids.mapped('transport_invoice_id').mapped('taxes_ids')
		taxes_ids = data_ids.mapped('partner_id').mapped('default_invoice_taxes_ids')
		for x in data_ids.mapped('purchase_id').mapped('order_line').mapped('taxes_id'):
			if x not in taxes_ids:
				taxes_ids |= x
		# metro_ids = data_ids.filtered(lambda x: x.timbang_metro_id)
		# sampit_ids = data_ids.filtered(lambda x: x.timbang_sampit_id)
		# dharmala_ids = data_ids.filtered(lambda x: x.import_dharmala_line_id)
		# rekap_ids = data_ids.filtered(lambda x: x.rekap_timbang_line_id)

		row = 4

		number = 1
		sheet.merge_range(row,0,row+1,0, "NO.", format4)
		sheet.merge_range(row,1,row+1,1, "JENIS PRODUK", format4)
		sheet.merge_range(row,2,row+1,2, "TANGGAL MUAT", format4)
		sheet.merge_range(row,3,row+1,3, "NO. TIMBANG", format4)
		sheet.merge_range(row,4,row+1,4, "TANGGAL BONGKAR", format4)
		sheet.merge_range(row,5,row+1,5, "ASAL", format4)
		sheet.merge_range(row,6,row+1,6, "TUJUAN", format4)
		sheet.merge_range(row,7,row+1,7, "RELASI", format4)
		sheet.merge_range(row,8,row+1,8, "NO. KONTRAK", format4)
		sheet.merge_range(row,9,row+1,9, "NAMA TRANSPORTER", format4)
		sheet.merge_range(row,10,row+1,10, "NO. PLAT", format4)
		sheet.merge_range(row,11,row+1,11, "NAMA SUPIR", format4)
		sheet.merge_range(row,12,row+1,12, "NO. DO BESAR", format4)
		sheet.merge_range(row,13,row+1,13, "TONASE DO BESAR", format4)
		sheet.merge_range(row,14,row,16, "TIMBANGAN SUPPLIER", format4)
		sheet.write(row+1,14, "BRUTO", format4)
		sheet.write(row+1,15, "TARRA", format4)
		sheet.write(row+1,16, "NETTO", format4)
		sheet.merge_range(row,17,row,19, "TIMBANGAN TERIMA SJIM", format4)
		sheet.write(row+1,17, "BRUTO", format4)
		sheet.write(row+1,18, "TARRA", format4)
		sheet.write(row+1,19, "NETTO", format4)
		sheet.merge_range(row,20,row+1,20, "SELISIH", format4)
		sheet.merge_range(row,21,row+1,21, "HARGA", format4)
		sheet.merge_range(row,22,row+1,22, "TOTAL", format4)
		column = 23
		for tax in taxes_ids:
			sheet.merge_range(row,column,row+1,column, tax.name, format4)
			column+=1

		sheet.merge_range(row,column,row+1,column, "TOTAL BAYAR", format4)
		sheet.merge_range(row,column+1,row+1,column+1, "NO. PO", format4)
		sheet.merge_range(row,column+2,row+1,column+2, "INCOTERM", format4)
		row+=2
		
		# Report Filling
		total_sjim_bruto = 0
		total_sjim_tarra = 0
		total_sjim_netto = 0
		total_supp_bruto = 0
		total_supp_tarra = 0
		total_supp_netto = 0
		total_selisih = 0
		total_harga = 0

		no = 1
		for data in data_ids.sorted(lambda x: x.date):
			in_date = datetime.strptime(data.date,'%Y-%m-%d').strftime('%d/%m/%Y') if data.date else '-'
			out_date = datetime.strptime(data.date,'%Y-%m-%d').strftime('%d/%m/%Y') if data.date else '-'
			sheet.write(row, 0, no, border)
			sheet.write(row, 1, data.product_id.name, border)
			sheet.write(row, 2, in_date, border)
			sheet.write(row, 3, data.no_tiket, border)
			sheet.write(row, 4, out_date, border)
			sheet.write(row, 5, data.src_location_id.name, border)
			sheet.write(row, 6, data.dest_location_id.name, border)
			sheet.write(row, 7, data.relasi, border)
			sheet.write(row, 8, data.contract_id.name, border)
			sheet.write(row, 9, data.partner_id.name, border)
			sheet.write(row, 10, data.no_plat, border)
			sheet.write(row, 11, data.driver_name, border)
			sheet.write(row, 12, data.wb_do, border)
			sheet.write(row, 13, '-', border)
			sheet.write(row, 14, data.src_bruto, border_num)
			sheet.write(row, 15, data.src_tare, border_num)
			sheet.write(row, 16, data.src_netto, border_num)
			sheet.write(row, 17, data.dest_bruto, border_num)
			sheet.write(row, 18, data.dest_tare, border_num)
			sheet.write(row, 19, data.product_qty, border_num)
			sheet.write(row, 20, data.src_netto-data.product_qty, border_num)
			sheet.write(row, 21, data.price_unit, border_num)
			sheet.write(row, 22, data.price_unit*(data.product_qty if data.rate_type=='by_weight' else 1), border_num)

			total_sjim_bruto += data.src_bruto
			total_sjim_tarra += data.src_tare
			total_sjim_netto += data.src_netto
			total_supp_bruto += data.dest_bruto
			total_supp_tarra += data.dest_tare
			total_supp_netto += data.product_qty
			total_selisih += (data.src_netto-data.product_qty)
			total_harga += data.price_unit*(data.product_qty if data.rate_type=='by_weight' else 1)

			column = 23
			total_tax = 0
			for tax in taxes_ids:
				data_tax = False
				if data.purchase_id:
					spk_taxes_ids = data.purchase_id.mapped('order_line').mapped('taxes_id')
					if spk_taxes_ids:
						data_tax = spk_taxes_ids.filtered(lambda x: x.id == tax.id)
				else:
					transporter_tax_ids = data.partner_id.default_invoice_taxes_ids
					if transporter_tax_ids:
						data_tax = transporter_tax_ids.filtered(lambda x: x.id == tax.id)
				if data_tax:
					tax_price = data_tax._compute_amount(data.price_unit*(data.product_qty if data.rate_type=='by_weight' else 1), data.price_unit, data.product_qty)
					total_tax+=tax_price
					sheet.write(row,column,tax_price, border_num)
					column+=1
				else:
					sheet.write(row,column,0, border_num)
					column+=1
			total_bayar = (data.price_unit*(data.product_qty if data.rate_type=='by_weight' else 1))+total_tax
			sheet.write(row, column, total_bayar, border_num)
			spk = data.purchase_id.name if data.purchase_id else '-'
			incoterm = data.contract_id.related_purchase_id.incoterm_id.name if data.contract_id.related_purchase_id else '-'
			sheet.write(row, column+1, spk, border_num)
			sheet.write(row, column+2, incoterm, border_num)

			row+=1
			no+=1

		sheet.merge_range(row,0,row,13, "TOTAL", format4)
		sheet.write(row, 14, total_sjim_bruto, format2)
		sheet.write(row, 15, total_sjim_tarra, format2)
		sheet.write(row, 16, total_sjim_netto, format2)
		sheet.write(row, 17, total_supp_bruto, format2)
		sheet.write(row, 18, total_supp_tarra, format2)
		sheet.write(row, 19, total_supp_netto, format2)
		sheet.write(row, 20, total_selisih, format2)
		sheet.write(row, 21, '', format2)
		sheet.write(row, 22, total_harga, format2)
		column = 23
		list_col = list(itertools.chain(string.ascii_uppercase, (''.join(pair) for pair in itertools.product(string.ascii_uppercase, repeat=2))))
		for tax in taxes_ids:
			formula = '=SUM('+str(list_col[column])+'5:'+str(list_col[column])+str(row)+')'
			sheet.write_formula(row,column,formula, format2)
			column+=1
		formula = '=SUM('+str(list_col[column])+'5:'+str(list_col[column])+str(row)+')'
		sheet.write(row, column, formula, format2)
		sheet.write(row, column+1, '', format2)
		sheet.write(row, column+2, '', format2)


ReportTransportDataPurchase('report.report_transport_data_purchase_xlsx',
				 'stock.transport.report.purchase.wizard')
