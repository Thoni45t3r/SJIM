from odoo import api, models, fields
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from calendar import monthrange
import itertools
import string

class ReportTransportData(ReportXlsx):

	def get_data(self, objects):
		domain = [('date', '>=', objects.date_start), ('date', '<=', objects.date_end)]
		if objects.product_id:
			domain.append(('product_id','=',objects.product_id.id))
		result = self.env['stock.transport.move'].search(domain)
		print "::::::::::::", result
		return result

	def generate_xlsx_report(self, workbook, data, objects):
		print("objects", objects)

		sheet = workbook.add_worksheet('Transport Report')
		sheet.set_column(0,0,5)
		sheet.set_column(1,4,30)
		bold = workbook.add_format({'bold': True})
		number_format = workbook.add_format({'num_format':'#,##0.00'})
		number_format_bold = workbook.add_format({'num_format':'#,##0.00', 'bold': True, 'bg_color': '#909191'})
		border = workbook.add_format({'border':1})
		border_bold = workbook.add_format({'border':1, 'bold':True})
		border2 = workbook.add_format({'border':1,'bold':True,'num_format':'#,##0.00'})
		format1 = workbook.add_format({'font_size': 16, 'bold': True})
		format2 = workbook.add_format({'bg_color': '#3aed2d', 'bold': True,'border':1, 'num_format':'#,##0.00'})
		format3 = workbook.add_format({'font_color': '#0c4dad', 'bold': True, 'font_size': 14})
		format4 = workbook.add_format({'bold': True, 'bg_color': '#8f8989', 'align':'center','valign':'vcenter', 'border':1, 'font_color': '#ffffff'})
		sheet.write(0, 0, objects.company_id.name, format1)
		sheet.write(1, 0, "ESTIMASI ONGKOS ANGKUT", format1)
		sheet.write(2, 0, 'PERIODE '+datetime.strptime(objects.date_start,'%Y-%m-%d').strftime('%d/%m/%Y')+' sampai '+datetime.strptime(objects.date_end,'%Y-%m-%d').strftime('%d/%m/%Y'), format3)
		sheet.write(1, 6, 'Print Date: '+datetime.now().strftime('%d/%m/%Y %H:%M:%S'), format3)

		data = self.get_data(objects)
		taxes_ids = data.mapped('partner_id').mapped('default_invoice_taxes_ids')
		for x in data.mapped('purchase_id').mapped('order_line').mapped('taxes_id'):
			if x not in taxes_ids:
				taxes_ids |= x
		product_ids = data.mapped('product_id')
		row = 4
		list_col = list(itertools.chain(string.ascii_uppercase, (''.join(pair) for pair in itertools.product(string.ascii_uppercase, repeat=2))))
		print ".............product", product_ids
		for product in product_ids:
			number = 1
			sheet.write(row,0, product.name, bold)
			row+=1
			sheet.write(row,0, "NO", format4)
			sheet.write(row,1, "NAMA EKSPEDISI", format4)
			sheet.write(row,2, "DITERIMA DARI", format4)
			sheet.write(row,3, "NO PO", format4)
			sheet.write(row,4, "NO KONTRAK", format4)
			sheet.write(row,5, "TONASE", format4)
			sheet.write(row,6, "HARGA", format4)
			sheet.write(row,7, "JUMLAH", format4)
			colunm = 8
			for tax in taxes_ids:
				sheet.write(row,colunm, tax.name, format4)
				colunm+=1
			sheet.write(row,colunm, "TOTAL", format4)
			sheet.set_column(5,colunm,20)

			# KLAIM
			colunm+=2
			sheet.write(row,colunm, "TONASE MUAT", format4)
			sheet.write(row,colunm+1, "TONASE BONGKAR", format4)
			sheet.write(row,colunm+2, "SUSUT", format4)
			sheet.write(row,colunm+3, "TOLERANSI SUSUT", format4)
			sheet.write(row,colunm+4, "TONASE KLAIM", format4)
			sheet.write(row,colunm+5, "HARGA", format4)
			sheet.write(row,colunm+6, "TOTAL KLAIM", format4)
			row+=1


			# contract_ids = data.filtered(lambda x: x.product_id == product).mapped('contract_id')
			data_filtered_product = data.filtered(lambda x: x.product_id==product)
			# print ".............product2", product.name, data_filtered_product
			for trans_type in ['sale', 'purchase']:
				grand_total = 0
				grand_total_akhir = 0
				total_tonase = 0
				tonase_muat_total = 0
				susut_total = 0
				toleransi_susut_total = 0
				tonase_klaim_total = 0
				grand_total_klaim = 0
				jenis = "PENJUALAN" if trans_type == 'sale' else "PEMBELIAN"
				# contract_olah = contract_ids.filtered(lambda x: x.trans_type == trans_type)
				# partner_ids = contract_olah.mapped('related_partner_id')
				data_filtered_trans = data_filtered_product.filtered(lambda x: x.contract_id.trans_type == trans_type)
				# print ".............filter trans", data_filtered_trans
				partner_ids = data_filtered_trans.mapped('partner_order_id')
				# print ".............get relasi", partner_ids
				if partner_ids:
					sheet.write(row, 1, jenis, border)
					row+=1
					for partner in partner_ids.sorted(lambda x: x.name):
						# print ":::::LOOP RELASI", partner.name
						sheet.write(row, 0, number, border_bold)
						sheet.write(row, 1, partner.name, border_bold)
						row+=1
						number+=1
						# data_partner = data.filtered(lambda x: x.product_id == product and x.contract_id.related_partner_id == partner)
						# transporter_ids = data_partner.mapped('partner_id')
						data_filter_partner_order = data_filtered_trans.filtered(lambda x: x.partner_order_id == partner)
						# print ".............fultered relasi", data_filter_partner_order
						transporter_ids = data_filter_partner_order.mapped('partner_id')
						# print ".............get transportir", transporter_ids
						for transporter in transporter_ids.sorted(lambda x: x.name):
							# print "::::::::::::::::::::LOOP Transportir", transporter.name
							sheet.write(row,1, transporter.name)
							data_filtered_transporter = data_filter_partner_order.filtered(lambda x: x.partner_id == transporter)
							# print ".............fultered transportir", data_filtered_transporter
							asal_ids = data_filtered_transporter.mapped('src_location_id')
							# print ".............get asal", asal_ids
							for asal in asal_ids.sorted(lambda x: x.name):
								# print ":::::::::::::::LOOP ASAL", asal.name
								sheet.write(row,2, asal.name)
								data_filtered_asal = data_filtered_transporter.filtered(lambda x: x.src_location_id == asal)
								# print ".............filtered asal", data_filtered_asal
								spk_ids = data_filtered_asal.mapped('purchase_id')
								# print ".............get spk", spk_ids
								if spk_ids:
									for spk in spk_ids.sorted(lambda x: x.name):
										# print "::::::::::LOOP SPK", spk.name
										data_filtered_spk = data_filtered_asal.filtered(lambda x: x.purchase_id == spk)
										spk_taxes_ids = spk.mapped('order_line').mapped('taxes_id')
										for contract in data_filtered_spk.mapped('contract_id'):
											sheet.write(row, 3, spk.name)
											sheet.write(row, 4, contract.name)
											data_filtered_contract = data_filtered_spk.filtered(lambda x: x.contract_id == contract)
											prices = list(set(data_filtered_contract.mapped('price_unit')))
											for price in prices:
												transport = data_filtered_contract.filtered(lambda x: x.price_unit == price)
												# tonase = sum(transport.mapped('product_qty'))
												tonase = tonase_muat = susut = 0.0
												for l in transport:
													if l.rate_type=='by_weight':
														tonase += l.product_qty
														tonase_muat += l.src_netto
														susut += l.difference_qty
													else:
														tonase += 1
														tonase_muat += 1
												total_price = tonase * price
												total_tonase += tonase
												grand_total += total_price
												sheet.write(row, 5, tonase, number_format)
												sheet.write(row, 6, price, number_format)
												sheet.write(row, 7, total_price, number_format)
												colunm = 8
												total_tax = 0
												for tax in taxes_ids:
													tax_transport = spk_taxes_ids.filtered(lambda x: x.id == tax.id)
													if tax_transport:
														tax_price = tax_transport._compute_amount(total_price, price, tonase)
														total_tax+=tax_price
														sheet.write(row, colunm, tax_price, number_format)
														colunm+=1
													else:
														sheet.write(row, colunm, ' ', number_format)
														colunm+=1
												grand_total_akhir += (total_price+total_tax)
												sheet.write(row, colunm, total_tax, number_format)
												sheet.write(row, colunm, total_price+total_tax, number_format)

												# KLAIM
												colunm+=2
												# tonase_muat=sum(transport.mapped('src_netto'))
												# susut = sum(transport.mapped('difference_qty'))
												toleransi_susut = 0.003*tonase_muat
												klaim = susut - toleransi_susut
												if klaim<0:
													klaim = 0
												harga = 0
												if trans_type == 'sale':
													harga = contract.related_sale_id.order_line.filtered(lambda x: x.product_id == product).price_unit
												elif trans_type == 'purchase':
													harga = contract.related_purchase_id.order_line.filtered(lambda x: x.product_id == product).price_unit
												total_klaim = klaim * harga

												tonase_muat_total += tonase_muat
												susut_total += susut
												toleransi_susut_total += toleransi_susut
												tonase_klaim_total += klaim
												grand_total_klaim += total_klaim
												
												sheet.write(row, colunm, tonase_muat, number_format)
												sheet.write(row, colunm+1, tonase, number_format)
												sheet.write(row, colunm+2, susut, number_format)
												sheet.write(row, colunm+3, toleransi_susut, number_format)
												sheet.write(row, colunm+4, klaim, number_format)
												sheet.write(row, colunm+5, harga, number_format)
												sheet.write(row, colunm+6, total_klaim, number_format)

												row+=1
								# belum ada SPK
								for contract in data_filtered_asal.filtered(lambda x: not x.purchase_id).mapped('contract_id').sorted(lambda x: x.name):
									sheet.write(row, 3, "")
									sheet.write(row, 4, contract.name)
									data_filtered_contract = data_filtered_asal.filtered(lambda x: not x.purchase_id and x.contract_id == contract)
									prices = list(set(data_filtered_contract.mapped('price_unit')))
									for price in prices:
										transport = data_filtered_contract.filtered(lambda x: x.price_unit == price)
										# tonase = sum(transport.mapped('product_qty'))
										tonase = tonase_muat = susut = 0.0
										for l in transport:
											if l.rate_type=='by_weight':
												tonase += l.product_qty
												tonase_muat += l.src_netto
												susut += l.difference_qty
											else:
												tonase += 1
												tonase_muat += 1
										total_price = tonase * price
										total_tonase += tonase
										grand_total += total_price
										sheet.write(row, 5, tonase, number_format)
										sheet.write(row, 6, price, number_format)
										sheet.write(row, 7, total_price, number_format)
										colunm = 8
										total_tax = 0
										for tax in taxes_ids:
											tax_transport = transporter.default_invoice_taxes_ids.filtered(lambda x: x.id == tax.id)
											if tax_transport:
												tax_price = tax_transport._compute_amount(total_price, price, tonase)
												total_tax+=tax_price
												sheet.write(row, colunm, tax_price, number_format)
												colunm+=1
											else:
												sheet.write(row, colunm, ' ', number_format)
												colunm+=1
										grand_total_akhir += (total_price+total_tax)
										sheet.write(row, colunm, total_tax, number_format)
										sheet.write(row, colunm, total_price+total_tax, number_format)
										
										# KLAIM
										colunm+=2
										# tonase_muat=sum(transport.mapped('src_netto'))
										# susut = sum(transport.mapped('difference_qty'))
										toleransi_susut = 0.003*tonase_muat
										klaim = susut - toleransi_susut
										if klaim<0:
											klaim = 0
										harga = 0
										if trans_type == 'sale':
											harga = contract.related_sale_id.order_line.filtered(lambda x: x.product_id == product).price_unit
										elif trans_type == 'purchase':
											harga = contract.related_purchase_id.order_line.filtered(lambda x: x.product_id == product).price_unit
										total_klaim = klaim * harga

										tonase_muat_total += tonase_muat
										susut_total += susut
										toleransi_susut_total += toleransi_susut
										tonase_klaim_total += klaim
										grand_total_klaim += total_klaim

										sheet.write(row, colunm, tonase_muat, number_format)
										sheet.write(row, colunm+1, tonase, number_format)
										sheet.write(row, colunm+2, susut, number_format)
										sheet.write(row, colunm+3, toleransi_susut, number_format)
										sheet.write(row, colunm+4, klaim, number_format)
										sheet.write(row, colunm+5, harga, number_format)
										sheet.write(row, colunm+6, total_klaim, number_format)

										row+=1
						row+=1
					sheet.write(row, 5, total_tonase, number_format_bold)
					sheet.write(row, 7, grand_total, number_format_bold)
					sheet.write(row, colunm-2, grand_total_akhir, number_format_bold)
					sheet.write(row, colunm, tonase_muat_total, number_format_bold)
					sheet.write(row, colunm+1, total_tonase, number_format_bold)
					sheet.write(row, colunm+2, susut_total, number_format_bold)
					sheet.write(row, colunm+3, toleransi_susut_total, number_format_bold)
					sheet.write(row, colunm+4, tonase_klaim_total, number_format_bold)
					sheet.write(row, colunm+5, ' ', number_format_bold)
					sheet.write(row, colunm+6, grand_total_klaim, number_format_bold)
					row+=2
			posisi = "A6"+':'+str(list_col[colunm])+str(row-1)
			posisi2 = str(list_col[colunm])+'6:'+str(list_col[colunm+6])+str(row-1)
			sheet.conditional_format(posisi , { 'type' : 'blanks' , 'format' : border})
			sheet.conditional_format(posisi , { 'type' : 'no_blanks' , 'format' : border})
			sheet.conditional_format(posisi2 , { 'type' : 'blanks' , 'format' : border})
			sheet.conditional_format(posisi2 , { 'type' : 'no_blanks' , 'format' : border})
			sheet.set_column(colunm,colunm+6,30)

ReportTransportData('report.report_transport_data_xlsx',
				 'stock.transport.report.wizard')
