from odoo import api, fields, models

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from xlsxwriter.utility import xl_rowcol_to_cell
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT

class GenerateReportPenjualanCustomerXlsx(ReportXlsx):
	def generate_xlsx_report(self, workbook, data, objects):
		wiz = objects
		domain = [('order_id.state','in',['sale','done']),\
			('order_id.date_order','>=',wiz.start_date + ' 00:00:00'), ('order_id.date_order','<=',wiz.end_date + ' 23:59:59'),('product_id','=',wiz .product_id.id)]


		SaleOrderLine = self.env['sale.order.line'].search(domain)
		sheet_name = 'Penjualan Product PerCustomer'
		sheet = workbook.add_worksheet(sheet_name)
		sheet.set_landscape()
		sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})

		column_width = [4, 19, 25, 25, 7, 12, 12, 15, 20, 20, 10, 5, 10, 12, 5, 7, 7, 7, 7, 7, 15, 12, 8, 10, 12, 12, 15, 15, 8, 10, 12, 12, 15, 15, 8, 10]
		for col_pos in range(0,36):
			sheet.set_column(col_pos, col_pos, column_width[col_pos])

		# TITLE
		t_cell_format = {'font_name': 'Arial', 'font_size': 15, 'bold': True, 'valign': 'vcenter', 'align': 'left'}
		t_style = workbook.add_format(t_cell_format)
		sheet.write_string(0, 0, "PT", t_style)
		sheet.write_string(0, 1, "SINAR JAYA INTI MULYA", t_style)
		sheet.write_string(1, 0, "Divisi Marketing", t_style)
		sheet.write_string(3, 0, "REKAPITULASI  PENJUALAN PRODUK PER CUSTOMER", t_style)
		date_start = datetime.strptime(wiz.start_date, DF).strftime("%d %b %Y")
		date_end = datetime.strptime(wiz.end_date, DF).strftime("%d %b %Y")
		sheet.write_string(4, 0, "PERIODE " + date_start + ' - ' + date_end, t_style)

		# TABLE HEADER
		h_cell_format = {'font_name': 'Arial', 'font_size': 8, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'border': 1}
		h_style = workbook.add_format(h_cell_format)
		
		sheet.write_string(6, 0, "No.", h_style)
		sheet.write_string(6, 1, "Jenis Product.", h_style)
		sheet.write_string(6, 2, "Nama Customer", h_style)
	   
		sheet.write_string(6, 3, "No Kontrak Penjualan", h_style)
		sheet.write_string(6, 4, "SAT", h_style)
		sheet.write_string(6, 5, "Tonase Kontrak", h_style)
		sheet.write_string(6, 6, "Harga Satuan", h_style)
		sheet.write_string(6, 7, "Nilai Kontrak", h_style)
		sheet.write_string(6, 8, "Syarat Penyerahan", h_style)
		sheet.write_string(6, 9, "Keterangan", h_style)

		for col_pos in range(0, 10):
			sheet.write_number(7, col_pos, col_pos+1, h_style)

		# TABLE DETAIL
		c_cell_format = {'font_name': 'Arial', 'font_size': 8, 'valign': 'top', 'align': 'left', 'border': 1}
		c_style = workbook.add_format(c_cell_format)

		c_datetime_format = c_cell_format.copy()
		c_datetime_format.update({'align': 'center', 'num_format': 'd mmm yy'})
		c_datetime_style = workbook.add_format(c_datetime_format)
		c_cell_format2 = c_cell_format
		c_cell_format2.update({'align': 'center'})
		c_style2 = workbook.add_format(c_cell_format2)
		num_cell_format = c_cell_format.copy()
		num_cell_format.update({'align': 'right', 'num_format':'#,##0.##;-#,##0.##;-'})
		num_style = workbook.add_format(num_cell_format)

		seq = 0
		row = 8
		row_start = row_stop = row + 1
		for so in SaleOrderLine.sorted(lambda x: x.order_id.date_order):
			seq += 1
			price_unit = so.price_subtotal / so.product_uom_qty if so.product_uom_qty else 0.0
			sheet.write(row, 0, seq, c_style2)
			sheet.write_string(row, 1, so.product_id.name or '', c_style)
			sheet.write_string(row, 2, so.order_partner_id.name or '', c_style)
			sheet.write_string(row, 3, so.order_id.client_order_ref or '', c_style)
			sheet.write_string(row, 4, so.product_uom.name or '', c_style)
			sheet.write_number(row, 5, so.product_uom_qty or 0, num_style)
			sheet.write_number(row, 6, price_unit, num_style)
			sheet.write_number(row, 7, so.price_subtotal or 0, num_style)
			sheet.write_string(row, 8, so.order_id.incoterm and (so.order_id.incoterm.code or so.order_id.incoterm.name) or '', c_style2)
			sheet.write_string(row, 9, '', c_style2)
			row += 1
		row_stop = row
		# Grantotal
		sheet.write_string(row, 0, '', c_style2)
		sheet.write_string(row, 1, '', c_style)
		sheet.write_string(row, 2, '', c_style)
		sheet.write_string(row, 3, '', c_style)
		sheet.write_string(row, 4, '', c_style)
		sheet.write_formula(row, 5, row_start==row_stop and '=SUM(F%s)'%str(row_start) or '=SUM(F%s:F%s)'%(str(row_start), str(row_stop)), num_style)
		sheet.write_string(row, 6, '', c_style)
		sheet.write_formula(row, 7, row_start==row_stop and '=SUM(H%s)'%str(row_start) or '=SUM(H%s:H%s)'%(str(row_start), str(row_stop)), num_style)
		sheet.write_string(row, 8, '', c_style2)
		sheet.write_string(row, 9, '', c_style2)
		row += 1

		sheet.set_margins(0.5, 0.5, 0.5, 0.5)
		sheet.print_area(0, 0, row, 10) #print area of selected cell
		sheet.set_paper(9)  # set A4 as page format
		sheet.center_horizontally()
		pages_horz = 1 # wide
		pages_vert = 0 # as long as necessary
		sheet.fit_to_pages(pages_horz, pages_vert)
		pass
GenerateReportPenjualanCustomerXlsx('report.report_generate_penjualan_customer_xls', 'generate.report.sale.order')

class GenerateReportDetailPenjualanProductXlsx(ReportXlsx):
	def generate_xlsx_report(self, workbook, data, objects):
		wiz = objects
		domain = [('order_id.state','in',['sale','done']),\
			('order_id.date_order','>=',wiz.start_date + ' 00:00:00'), ('order_id.date_order','<=',wiz.end_date + ' 23:59:59'),('product_id','=',wiz .product_id.id)]


		OrderLine = self.env['sale.order.line'].search(domain)
		sheet_name = 'Detail Penjualan Product'
		sheet = workbook.add_worksheet(sheet_name)
		sheet.set_landscape()
		sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})

		column_width = [4, 18, 12, 19, 25, 7, 11, 14, 7, 15, 25, 25, 19, 12, 20, 15, 15, 15, 15, 15, 15, 12, 8, 10, 12, 12, 15, 15, 8, 10, 12, 12, 15, 15, 8, 10]
		for col_pos in range(0,36):
			sheet.set_column(col_pos, col_pos, column_width[col_pos])

		# TITLE
		t_cell_format = {'font_name': 'Arial', 'font_size': 15, 'bold': True, 'valign': 'vcenter', 'align': 'left'}
		t_style = workbook.add_format(t_cell_format)
		sheet.write_string(0, 0, "PT", t_style)
		sheet.write_string(0, 1, "SINAR JAYA INTI MULYA", t_style)
		sheet.merge_range(1, 0, 1, 2, "Divisi Marketing", t_style)
		sheet.write_string(3, 0, "LAPORAN DETAIL PENJUALAN PRODUK", t_style)
		date_start = datetime.strptime(wiz.start_date, DF).strftime("%d %b %Y")
		date_end = datetime.strptime(wiz.end_date, DF).strftime("%d %b %Y")
		sheet.write_string(4, 0, "PERIODE " + date_start + ' - ' + date_end, t_style)

		# TABLE HEADER
		h_cell_format = {'font_name': 'Arial', 'font_size': 8, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'border': 1}
		h_style = workbook.add_format(h_cell_format)
		
		sheet.write_string(6, 0, "No.", h_style)
		sheet.write_string(6, 1, "Jenis Product.", h_style)
		sheet.write_string(6, 2, "Tanggal Transaksi", h_style)
	   
		sheet.write_string(6, 3, "No Kontrak Penjualan", h_style)
		sheet.write_string(6, 4, "Nama Customer", h_style)
		sheet.write_string(6, 5, "SAT", h_style)
		sheet.write_string(6, 6, "Tonase Kontrak", h_style)
		sheet.write_string(6, 7, "Harga (Exclude PPN)", h_style)
		sheet.write_string(6, 8, "PPN", h_style)
		sheet.write_string(6, 9, "Nilai Kontrak (Rp.)", h_style)
		sheet.write_string(6, 10, "Syarat Penyerahan", h_style)
		sheet.write_string(6, 11, "Tgl Terima Pembayaran", h_style)
		sheet.write_string(6, 12, "No Invoice", h_style)
		sheet.write_string(6, 13, "Tonase Actual", h_style)
		sheet.write_string(6, 14, "Jumlah Penerimaan Pembayaran (Rp.)", h_style)
		sheet.write_string(6, 15, "Tgl Faktur Pajak", h_style)
		sheet.write_string(6, 16, "No Faktur Pajak", h_style)
		sheet.write_string(6, 17, "Nilai Faktur Pajak (Rp.)", h_style)
		sheet.write_string(6, 18, "Keterangan", h_style)

		for col_pos in range(0, 19):
			sheet.write_number(7, col_pos, col_pos+1, h_style)

		# TABLE DETAIL
		c_cell_format = {'font_name': 'Arial', 'font_size': 8, 'valign': 'top', 'align': 'left', 'border': 1}
		c_style = workbook.add_format(c_cell_format)
		c_datetime_format = c_cell_format.copy()
		c_datetime_format.update({'align': 'center', 'num_format': 'd mmm yy'})
		c_datetime_style = workbook.add_format(c_datetime_format)
		c_cell_format2 = c_cell_format
		c_cell_format2.update({'align': 'center'})
		c_style2 = workbook.add_format(c_cell_format2)
		num_cell_format = c_cell_format.copy()
		num_cell_format.update({'align': 'right', 'num_format':'#,##0.##;-#,##0.##;-'})
		num_style = workbook.add_format(num_cell_format)

		sub_cell_format = c_cell_format.copy()
		sub_cell_format.update({'bold': True})
		sub_style = workbook.add_format(sub_cell_format)
		sub_num_cell_format = num_cell_format.copy()
		sub_num_cell_format.update({'bold': True})
		sub_num_style = workbook.add_format(sub_num_cell_format)

		seq = 0
		row = 8
		grandtotal_row = []
		for so in OrderLine.sorted(lambda x: x.order_id.date_order):
			row_end = row
			SumInv = len(so.invoice_lines.mapped('invoice_id')) + len(so.order_id.advance_invoice_ids)
			seq += 1

			date_order = datetime.strptime(so.order_id.date_order, DT)

			if SumInv > 1:
				row_end = row + (SumInv - 1)
				sheet.merge_range(row, 0, row_end, 0, seq, c_style2)
				sheet.merge_range(row, 1, row_end, 1, so.product_id.name  or '', c_style)
				sheet.merge_range(row, 2, row_end, 2, date_order, c_datetime_style)
				sheet.merge_range(row, 3, row_end, 3, so.order_id.client_order_ref or '', c_style)
				sheet.merge_range(row, 4, row_end, 4, so.order_id.partner_id.name or '', c_style)
				sheet.merge_range(row, 5, row_end, 5, so.product_uom.name or '', c_style)

				sheet.merge_range(row, 6, row_end, 6, so.product_uom_qty or 0.0, num_style)
				sheet.merge_range(row, 7, row_end, 7, so.price_subtotal / so.product_uom_qty if so.product_uom_qty else 0.0, num_style)
				sheet.merge_range(row, 8, row_end, 8, 0 or '', c_style2)
				sheet.merge_range(row, 9, row_end, 9, so.price_subtotal or 0.0, num_style)
				sheet.merge_range(row, 10, row_end, 10, so.order_id.incoterm.name or '', c_style)

			else:
				sheet.write(row, 0, seq, c_style2)
				sheet.write_string(row, 1, so.product_id.name  or '', c_style)
				sheet.write_datetime(row, 2, date_order or '', c_datetime_style)
				sheet.write_string(row, 3, so.order_id.client_order_ref or '', c_style)
				sheet.write_string(row, 4, so.order_id.partner_id.name or '', c_style)
				sheet.write_string(row, 5, so.product_uom.name or '', c_style)

				sheet.write_number(row, 6, so.product_uom_qty or 0.0, num_style)
				sheet.write_number(row, 7, so.price_subtotal / so.product_uom_qty if so.product_uom_qty else 0.0, num_style)
				sheet.write_string(row, 8, 0 or '', c_style2)
				sheet.write_number(row, 9, so.price_subtotal or 0.0, num_style)
				sheet.write_string(row, 10, so.order_id.incoterm.name or '', c_style)

			rowinv = row
			tonase_inv = 0.0
			amount_inv = 0.0
			for adv in so.order_id.advance_invoice_ids:
				payment = self.env['account.payment']
				for mline in adv.move_id.line_ids:
					if mline.account_id.id!=adv.account_id.id:
						continue
					if mline.full_reconcile_id:
						for rl in mline.full_reconcile_id.reconciled_line_ids:
							if rl.id==mline.id:
								continue
							if rl.payment_id:
								payment |= rl.payment_id
				if payment:
					payment_date = datetime.strptime(payment[-1].payment_date, "%Y-%m-%d")
					sheet.write_datetime(rowinv, 11, payment_date, c_datetime_style)
				else:
					sheet.write_string(rowinv, 11, '', c_datetime_style)
				
				if adv.date_invoice:
					FakturDate = datetime.strptime(adv.date_invoice, "%Y-%m-%d")
				else:
					FakturDate = ''

				sheet.write_string(rowinv, 12, adv.number or '', c_style2)
				sheet.write_number(rowinv, 13, 0.0, num_style)
				sheet.write_number(rowinv, 14, adv.amount_total or 0.0, num_style)

				if FakturDate:
					sheet.write_datetime(rowinv, 15, FakturDate  or '', c_datetime_style)
				else:
					sheet.write_string(rowinv, 15, '', c_datetime_style)
				sheet.write_string(rowinv, 16, adv.faktur_keluaran_id and "%s%s.%s"%(str(adv.kode_transaksi), str(adv.kode_status_faktur), adv.faktur_keluaran_id.name) or '', c_style2)
				sheet.write_number(rowinv, 17, adv.amount_total or 0.0, num_style)
				sheet.write_string(rowinv, 18, '', c_style)
				amount_inv += adv.amount_total
				rowinv += 1

			invoices = so.invoice_lines.mapped('invoice_id').filtered(lambda x: x.state in ('open','paid'))
			for inv in invoices:
				# if Payment:
				# 	PaymentDate = datetime.strptime(Payment.date_maturity, "%Y-%m-%d")
				# else:
				# 	PaymentDate = False

				if inv.date_invoice:
					FakturDate = datetime.strptime(inv.date_invoice, "%Y-%m-%d")
				else:
					FakturDate = ''

				if inv.payment_ids:
					payment_date = datetime.strptime(inv.payment_ids[-1].payment_date, "%Y-%m-%d")
					sheet.write_datetime(rowinv, 11, payment_date, c_datetime_style)
				else:
					sheet.write_string(rowinv, 11, '', c_datetime_style)

				sheet.write_string(rowinv, 12, inv.number or '', c_style2)
				total_qty = sum(inv.invoice_line_ids.filtered(lambda x: x.product_id.id==so.product_id.id).mapped('quantity'))
				sheet.write_number(rowinv, 13, total_qty, num_style)
				sheet.write_number(rowinv, 14, inv.amount_total  or 0.0, num_style)

				if FakturDate:
					sheet.write_datetime(rowinv, 15, FakturDate  or '', c_datetime_style)
				else:
					sheet.write_string(rowinv, 15, '', c_datetime_style)

				sheet.write_string(rowinv, 16, inv.faktur_keluaran_id and "%s%s.%s"%(str(inv.kode_transaksi), str(inv.kode_status_faktur), inv.faktur_keluaran_id.name) or '', c_style2)
				sheet.write_number(rowinv, 17, inv.amount_total or 0.0, num_style)
				sheet.write_string(rowinv, 18, '', c_style)
				amount_inv += inv.amount_total
				tonase_inv += total_qty
				rowinv += 1

			if SumInv > 1:
				row_end += 1
				sheet.write_string(row_end, 0, '', sub_style)
				sheet.write_string(row_end, 1, '', sub_style)
				sheet.write_string(row_end, 2, '', sub_style)
				sheet.write_string(row_end, 3, '', sub_style)
				sheet.write_string(row_end, 4, '', sub_style)
				sheet.write_string(row_end, 5, '', sub_style)
				sheet.write_string(row_end, 6, '', sub_style)
				sheet.write_string(row_end, 7, '', sub_style)
				sheet.write_string(row_end, 8, '', sub_style)
				sheet.write_string(row_end, 9, '', sub_style)
				sheet.write_string(row_end, 10, '', sub_style)
				sheet.write_string(row_end, 11, '', sub_style)
				sheet.write_string(row_end, 12, '', sub_style)
				sheet.write_number(row_end, 13, tonase_inv  or 0.0, sub_num_style)
				sheet.write_number(row_end, 14, amount_inv  or 0.0, sub_num_style)
				sheet.write_string(row_end, 15, '', sub_style)
				sheet.write_string(row_end, 16, '', sub_style)
				sheet.write_string(row_end, 17, '', sub_style)
				sheet.write_string(row_end, 18, '', sub_style)
				grandtotal_row.append(row_end+1)
			else:
				grandtotal_row.append(row+1)
			row = row_end+1

		sheet.write_string(row, 0, '', sub_style)
		sheet.write_string(row, 1, '', sub_style)
		sheet.write_string(row, 2, '', sub_style)
		sheet.write_string(row, 3, '', sub_style)
		sheet.write_string(row, 4, '', sub_style)
		sheet.write_string(row, 5, '', sub_style)
		sheet.write_string(row, 6, '', sub_style)
		sheet.write_string(row, 7, '', sub_style)
		sheet.write_string(row, 8, '', sub_style)
		sheet.write_string(row, 9, '', sub_style)
		sheet.write_string(row, 10, '', sub_style)
		sheet.write_string(row, 11, '', sub_style)
		sheet.write_string(row, 12, '', sub_style)
		if grandtotal_row:
			sheet.write_formula(row, 13, '=SUM(%s)'%(",".join(['N%s'%str(x) for x in grandtotal_row])), sub_num_style)
			sheet.write_formula(row, 14, '=SUM(%s)'%(",".join(['O%s'%str(x) for x in grandtotal_row])), sub_num_style)
		else:
			sheet.write_string(row, 13, '', sub_style)
			sheet.write_string(row, 14, '', sub_style)
		sheet.write_string(row, 15, '', sub_style)
		sheet.write_string(row, 16, '', sub_style)
		sheet.write_string(row, 17, '', sub_style)
		sheet.write_string(row, 18, '', sub_style)

		sheet.set_margins(0.5, 0.5, 0.5, 0.5)
		sheet.print_area(0, 0, row, 20) #print area of selected cell
		sheet.set_paper(9)  # set A4 as page format
		sheet.center_horizontally()
		pages_horz = 1 # wide
		pages_vert = 0 # as long as necessary
		sheet.fit_to_pages(pages_horz, pages_vert)
		pass
GenerateReportDetailPenjualanProductXlsx('report.report_generate_detail_penjualan_barang_xls', 'generate.report.sale.order')

