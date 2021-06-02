from odoo import api, fields, models

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from xlsxwriter.utility import xl_rowcol_to_cell
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT

class GenerateReportRekapPembelianXlsx(ReportXlsx):
	def generate_xlsx_report(self, workbook, data, objects):
		wiz = objects
		domain = [('state','in',['purchase','done', 'draft']),\
			('order_id.date_order','>=',wiz.start_date + ' 00:00:00'), ('order_id.date_order','<=',wiz.end_date + ' 23:59:59'),('product_id','=',wiz .product_id.id)]


		purchases = self.env['purchase.order.line'].search(domain)
		sheet_name = 'Rekap Pembelian'
		sheet = workbook.add_worksheet(sheet_name)
		sheet.set_landscape()
		sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})

		column_width = [4, 12, 12, 20, 15, 12, 15, 10, 20, 20, 10, 5, 10, 12, 5, 7, 7, 7, 7, 7, 15, 12, 8, 10, 12, 12, 15, 15, 8, 10, 12, 12, 15, 15, 8, 10]
		for col_pos in range(0,36):
			sheet.set_column(col_pos, col_pos, column_width[col_pos])

		# TITLE
		t_cell_format = {'font_name': 'Arial', 'font_size': 15, 'bold': True, 'valign': 'vcenter', 'align': 'left'}
		t_style = workbook.add_format(t_cell_format)
		sheet.write_string(0, 0, "PT", t_style)
		sheet.write_string(0, 1, "SINAR JAYA INTI MULYA", t_style)
		sheet.write_string(1, 0, "Divisi Marketing", t_style)
		sheet.write_string(4, 0, "REKAPITULASI PEMBELIAN PRODUCT", t_style)
		date_start = datetime.strptime(wiz.start_date, DF).strftime("%d %b %Y")
		date_end = datetime.strptime(wiz.end_date, DF).strftime("%d %b %Y")
		sheet.write_string(5, 0, "PERIODE " + date_start + ' - ' + date_end, t_style)

		# TABLE HEADER
		h_cell_format = {'font_name': 'Arial', 'font_size': 8, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'border': 1}
		h_style = workbook.add_format(h_cell_format)
		
		sheet.write_string(8, 0, "No.", h_style)
		sheet.write_string(8, 1, "Jenis Product.", h_style)
		sheet.write_string(8, 2, "Tanggal Transaksi", h_style)
	   
		sheet.write_string(8, 3, "Nama Supplier / Relasi", h_style)
		sheet.write_string(8, 4, "No. Kontrak Pembelian", h_style)
		sheet.write_string(8, 5, "Tonase Kontrak", h_style)
		sheet.write_string(8, 6, "Harga Satuan Exclude PPN", h_style)
		sheet.write_string(8, 7, "Nilai Kontrak", h_style)
		sheet.write_string(8, 8, "Syarat Penyerahan", h_style)
		sheet.write_string(8, 9, "Keterangan", h_style)
	  

		for col_pos in range(0, 10):
			sheet.write_number(9, col_pos, col_pos+1, h_style)

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
		row = 10
		row_start = row_stop = row
		for po in purchases:
			# Part 1: Detail PO
			seq += 1
			sheet.write(row, 0, seq, c_style2)
			sheet.write_string(row, 1, po.product_id.name or '', c_style)

			date_order = datetime.strptime(po.date_order, DT)

			sheet.write_datetime(row, 2, date_order or '', c_datetime_style)
			sheet.write_string(row, 3, po.partner_id.name or '', c_style)
			sheet.write_string(row, 4, po.order_id.partner_ref or '', c_style)
			sheet.write_number(row, 5, po.product_qty or 0.0, num_style)
			sheet.write_number(row, 6, po.price_subtotal / po.product_qty if po.product_qty else 0.0, num_style)
			sheet.write_number(row, 7, po.price_subtotal, num_style)
			sheet.write_string(row, 8, po.order_id.incoterm_id.name or '', c_style2)
			sheet.write_string(row, 9, po.state.upper(), c_style2)
			row_stop = row
			row += 1
		sheet.write_string(row, 0, '', sub_style)
		sheet.write_string(row, 1, '', sub_style)
		sheet.write_string(row, 2, '', sub_style)
		sheet.write_string(row, 3, '', sub_style)
		sheet.write_string(row, 4, '', sub_style)
		sheet.write_formula(row, 5, row_start!=row_stop and '=SUM(F%s:F%s)'%(str(row_start+1),str(row_stop+1)) or '=SUM(F%s)'%str(row_start+1), sub_num_style)
		sheet.write_string(row, 6, '', sub_style)
		sheet.write_formula(row, 7, row_start!=row_stop and '=SUM(H%s:H%s)'%(str(row_start+1),str(row_stop+1)) or '=SUM(H%s)'%str(row_start+1), sub_num_style)
		sheet.write_string(row, 8, '', sub_style)
		sheet.write_string(row, 9, '', sub_style)

		sheet.set_margins(0.5, 0.5, 0.5, 0.5)
		sheet.print_area(0, 0, row, 10) #print area of selected cell
		sheet.set_paper(9)  # set A4 as page format
		sheet.center_horizontally()
		pages_horz = 1 # wide
		pages_vert = 0 # as long as necessary
		sheet.fit_to_pages(pages_horz, pages_vert)
		pass
GenerateReportRekapPembelianXlsx('report.report_generate_rekap_pembelian_xls', 'wizard.generate.report.purchase.order')



class GenerateReportDetailPembelianProductXlsx(ReportXlsx):
	def generate_xlsx_report(self, workbook, data, objects):
		wiz = objects
		domain = [('state','in',['purchase','done','draft']),\
			('date_order','>=',wiz.start_date + ' 00:00:00'), ('date_order','<=',wiz.end_date + ' 23:59:59'),('product_id','=',wiz .product_id.id)]

		purchasesline = self.env['purchase.order.line'].search(domain)
		sheet_name = 'Detail Pembelian Product'
		sheet = workbook.add_worksheet(sheet_name)
		sheet.set_landscape()
		sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})

		column_width = [4, 12, 12, 15, 25, 13, 15, 10, 20, 20, 10, 5, 10, 12, 20, 15, 15, 15, 15, 15, 15, 12, 8, 10, 12, 12, 15, 15, 8, 10, 12, 12, 15, 15, 8, 10]
		for col_pos in range(0,36):
			sheet.set_column(col_pos, col_pos, column_width[col_pos])

		# TITLE
		t_cell_format = {'font_name': 'Arial', 'font_size': 15, 'bold': True, 'valign': 'vcenter', 'align': 'left'}
		t_style = workbook.add_format(t_cell_format)
		sheet.write_string(0, 0, "PT", t_style)
		sheet.write_string(0, 1, "SINAR JAYA INTI MULYA", t_style)
		sheet.merge_range(1, 0, 1, 2, "Divisi Marketing", t_style)
		sheet.write_string(4, 0, "LAPORAN DETAIL PEMBELIAN PRODUCT", t_style)
		date_start = datetime.strptime(wiz.start_date, DF).strftime("%d %b %Y")
		date_end = datetime.strptime(wiz.end_date, DF).strftime("%d %b %Y")
		sheet.write_string(5, 0, "PERIODE " + date_start + ' - ' + date_end, t_style)

		# TABLE HEADER
		h_cell_format = {'font_name': 'Arial', 'font_size': 8, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'border': 1}
		h_style = workbook.add_format(h_cell_format)
		
		sheet.merge_range(7, 0, 8, 0, "No.", h_style)
		sheet.merge_range(7, 1, 8, 1, "Jenis Product.", h_style)
		sheet.merge_range(7, 2, 8, 2, "Tanggal Transaksi.", h_style)
		sheet.merge_range(7, 3, 8, 3, "No Kontrak Pembelian.", h_style)
		sheet.merge_range(7, 4, 8, 4, "Nama Supplier / Relasi.", h_style)
		sheet.merge_range(7, 5, 8, 5, "Tonase Kontrak.", h_style)
		sheet.merge_range(7, 6, 8, 6, "Harga Exclude PPN.", h_style)
		sheet.merge_range(7, 7, 8, 7, "PPN.", h_style)
		sheet.merge_range(7, 8, 8, 8, "Nilai Kontrak (Rp.)", h_style)
		sheet.merge_range(7, 9, 8, 9, "Syarat Penyerahan.", h_style)
		sheet.merge_range(7, 10, 7, 12, "Standar Mutu.", h_style)
		sheet.write_string(8, 10, "FFA.", h_style)
		sheet.write_string(8, 11, "KK.", h_style)
		sheet.write_string(8, 12, "KA.", h_style)
		sheet.merge_range(7, 13, 8, 13, "Tgl Bayar.", h_style)
		sheet.merge_range(7, 14, 8, 14, "No Invoice.", h_style)
		sheet.merge_range(7, 15, 8, 15, "Tonase Actual/Bayar.", h_style)
		sheet.merge_range(7, 16, 8, 16, "Jumlah Pembayaran (Rp.).", h_style)
		sheet.merge_range(7, 17, 8, 17, "Tgl Faktur Pajak.", h_style)
		sheet.merge_range(7, 18, 8, 18, "No Faktur Pajak.", h_style)
		sheet.merge_range(7, 19, 8, 19, "Nilai FP (Rp.).", h_style)
		sheet.merge_range(7, 20, 8, 20, "Keterangan.", h_style)
	  

		for col_pos in range(0, 21):
			sheet.write_number(9, col_pos, col_pos+1, h_style)

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
		row = 10
		grandtotal_row = []
		for po in purchasesline:
			seq += 1
			row_end = row
			# Part 1: Detail PO
			SumInv = len(po.invoice_lines.mapped('invoice_id')) + len(po.order_id.advance_invoice_ids)

			date_order = datetime.strptime(po.date_order, DT)
			SumPick = len(po.move_ids)
			ffa = 0
			kk = 0
			ka = 0
			for l in po.move_ids:
				ffa += l.picking_id.vendor_quality_ffa
				kk += l.picking_id.vendor_quality_kk
				ka += l.picking_id.vendor_quality_ka

			# RangeFFA = ffa / SumPick if SumPick else 0.0
			try:
				RangeFFA = float(po.order_id.quality_ffa) or 0.0
			except:
				RangeFFA = 0.0
			# RangeKK = kk / SumPick if SumPick else 0.0
			try:
				RangeKK = float(po.order_id.quality_mni) or 0.0
			except:
				RangeKK = 0.0
			# RangeKA = ka /SumPick if SumPick else 0.0
			try:
				RangeKA = float(po.order_id.quality_iv) or 0.0
			except:
				RangeKA = 0.0

			if SumInv > 1:
				row_end = row + (SumInv - 1)
				sheet.merge_range(row, 0, row_end, 0, seq, c_style2)
				sheet.merge_range(row, 1, row_end, 1, po.product_id.name  or '', c_style)
				sheet.merge_range(row, 2, row_end, 2, date_order, c_datetime_style)
				sheet.merge_range(row, 3, row_end, 3, po.order_id.partner_ref or '', c_style)
				sheet.merge_range(row, 4, row_end, 4, po.order_id.partner_id.name or '', c_style)
				sheet.merge_range(row, 5, row_end, 5, po.product_qty or 0.0, num_style)
				sheet.merge_range(row, 6, row_end, 6, po.price_subtotal / po.product_qty if po.product_qty else 0.0, num_style)
				sheet.merge_range(row, 7, row_end, 7, '-', c_style2)
				sheet.merge_range(row, 8, row_end, 8, po.price_subtotal or 0.0, num_style)
				sheet.merge_range(row, 9, row_end, 9, po.order_id.incoterm_id.name or '', c_style2)
				sheet.merge_range(row, 10, row_end, 10, RangeFFA, num_style)
				sheet.merge_range(row, 11, row_end, 11, RangeKK, num_style)
				sheet.merge_range(row, 12, row_end, 12, RangeKA, num_style)
			else:
				sheet.write(row, 0, seq, c_style2)
				sheet.write_string(row, 1, po.product_id.name  or '', c_style)
				sheet.write_datetime(row, 2, date_order or '', c_datetime_style)
				sheet.write_string(row, 3, po.order_id.partner_ref or '', c_style)
				sheet.write_string(row, 4, po.order_id.partner_id.name or '', c_style)
				sheet.write_number(row, 5, po.product_qty or 0.0, num_style)
				sheet.write_number(row, 6, po.price_subtotal / po.product_qty if po.product_qty else 0.0, num_style)
				sheet.write_string(row, 7, '-', c_style2)
				sheet.write_number(row, 8, po.price_subtotal or 0.0, num_style)
				sheet.write_string(row, 9, po.order_id.incoterm_id.name or '', c_style2)
				sheet.write_number(row, 10, RangeFFA, num_style)
				sheet.write_number(row, 11, RangeKK, num_style)
				sheet.write_number(row, 12, RangeKA, num_style)

			rowinv = row
			tonase_inv = 0.0
			amount_inv = 0.0
			for adv in po.order_id.advance_invoice_ids:
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
					sheet.write_datetime(rowinv, 13, payment_date, c_datetime_style)
				else:
					sheet.write_string(rowinv, 13, '', c_datetime_style)

				if adv.date_faktur_pajak_bill:
					FakturDate = datetime.strptime(adv.date_faktur_pajak_bill, "%Y-%m-%d")
				else:
					FakturDate = False
				
				sheet.write_string(rowinv, 14, adv.reference or adv.number or '', c_style2)
				sheet.write_number(rowinv, 15, 0.0, num_style)
				sheet.write_number(rowinv, 16, adv.amount_total, num_style)
				amount_inv += adv.amount_total
				if FakturDate:
					sheet.write_datetime(rowinv, 17, FakturDate  or '', c_datetime_style)
				else:
					sheet.write_string(rowinv, 17, '', c_datetime_style)
				sheet.write_string(rowinv, 18, adv.nomer_seri_faktur_pajak_bill or '', c_style2)
				if adv.nomer_seri_faktur_pajak_bill:
					if adv.amount_untaxed:
						sheet.write_number(rowinv, 19, adv.amount_untaxed, num_style)
					else:
						sheet.write_number(rowinv, 19, adv.amount_total, num_style)
				else:
					sheet.write_number(rowinv, 19, 0.0, num_style)
				sheet.write_string(rowinv, 20, '', c_style)
				rowinv += 1

			invoices = po.invoice_lines.mapped('invoice_id').filtered(lambda x: x.state in ('open','paid'))
			for inv in invoices:
				# total_qty = sum(inv.invoice_line_ids.filtered(lambda x: x.product_id.id==po.product_id.id).mapped('quantity'))
				total_qty = sum(inv.invoice_line_ids.mapped('quantity'))

				if inv.date_faktur_pajak_bill:
					FakturDate = datetime.strptime(inv.date_faktur_pajak_bill, "%Y-%m-%d")
				else:
					FakturDate = False

				if inv.payment_ids:
					payment_date = datetime.strptime(inv.payment_ids[-1].payment_date, "%Y-%m-%d")
					sheet.write_datetime(rowinv, 13, payment_date, c_datetime_style)
				else:
					sheet.write_string(rowinv, 13, '', c_datetime_style)

				sheet.write_string(rowinv, 14, inv.reference or inv.number or '', c_style2)
				sheet.write_number(rowinv, 15, total_qty, num_style)
				sheet.write_number(rowinv, 16, inv.amount_total, num_style)
				if FakturDate:
					sheet.write_datetime(rowinv, 17, FakturDate  or '', c_datetime_style)
				else:
					sheet.write_string(rowinv, 17, '', c_datetime_style)

				sheet.write_string(rowinv, 18, inv.nomer_seri_faktur_pajak_bill or '', c_style2)
				if inv.nomer_seri_faktur_pajak_bill:
					if inv.amount_total:
						sheet.write_number(rowinv, 19, inv.amount_untaxed, num_style)
					else:
						sheet.write_number(rowinv, 19, sum(inv.invoice_line_ids.mapped('price_subtotal')), num_style)
				else:
					sheet.write_number(rowinv, 19, 0.0, num_style)
				sheet.write_string(rowinv, 20, '', c_style)

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
				sheet.write_string(row_end, 13, '', sub_style)
				sheet.write_string(row_end, 14, '', sub_style)
				sheet.write_number(row_end, 15, tonase_inv  or 0.0, sub_num_style)
				sheet.write_number(row_end, 16, amount_inv  or 0.0, sub_num_style)
				sheet.write_string(row_end, 17, '', sub_style)
				sheet.write_string(row_end, 18, '', sub_style)
				sheet.write_string(row_end, 19, '', sub_style)
				sheet.write_string(row_end, 20, '', sub_style)
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
		sheet.write_string(row, 13, '', sub_style)
		sheet.write_string(row, 14, '', sub_style)
		if grandtotal_row:
			sheet.write_formula(row, 15, '=SUM(%s)'%(",".join(['P%s'%str(x) for x in grandtotal_row])), sub_num_style)
			sheet.write_formula(row, 16, '=SUM(%s)'%(",".join(['Q%s'%str(x) for x in grandtotal_row])), sub_num_style)
		else:
			sheet.write_string(row, 15, '', sub_style)
			sheet.write_string(row, 16, '', sub_style)
		sheet.write_string(row, 17, '', sub_style)
		sheet.write_string(row, 18, '', sub_style)
		sheet.write_string(row, 19, '', sub_style)
		sheet.write_string(row, 20, '', sub_style)

		sheet.set_margins(0.5, 0.5, 0.5, 0.5)
		sheet.print_area(0, 0, row, 21) #print area of selected cell
		sheet.set_paper(9)  # set A4 as page format
		sheet.center_horizontally()
		pages_horz = 1 # wide
		pages_vert = 0 # as long as necessary
		sheet.fit_to_pages(pages_horz, pages_vert)
		pass
GenerateReportDetailPembelianProductXlsx('report.report_generate_detail_pembelian_product_xls', 'wizard.generate.report.purchase.order')




class GenerateReporPerincianPemenuhanPembelianBarangXlsx(ReportXlsx):
	def generate_xlsx_report(self, workbook, data, objects):
		wiz = objects
		domain = [('state','in',['purchase','done', 'draft']),\
			('date_order','>=',wiz.start_date + ' 00:00:00'), ('date_order','<=',wiz.end_date + ' 23:59:59'),('product_id','=',wiz .product_id.id)]

		# if wiz.doc_type_ids.filtered(lambda x: x.purchase):
		#     domain.append(('doc_type_id','in',wiz.doc_type_ids.filtered(lambda x: x.purchase).ids))

		purchasesline = self.env['purchase.order.line'].search(domain)
		sheet_name = 'Perincian Pembembelian Barang'
		sheet = workbook.add_worksheet(sheet_name)
		sheet.set_landscape()
		sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})

		column_width = [4, 12, 15, 18, 15, 20, 12, 10, 20, 20, 10, 10, 10, 10, 5, 7, 7, 7, 7, 7, 15, 12, 8, 10, 12, 12, 15, 15, 8, 10, 12, 12, 15, 15, 8, 10]
		for col_pos in range(0,36):
			sheet.set_column(col_pos, col_pos, column_width[col_pos])

		# TITLE
		t_cell_format = {'font_name': 'Arial', 'font_size': 15, 'bold': True, 'valign': 'vcenter', 'align': 'left'}
		t_style = workbook.add_format(t_cell_format)
		sheet.write_string(0, 0, "PT", t_style)
		sheet.write_string(0, 1, "SINAR JAYA INTI MULYA", t_style)
		sheet.write_string(1, 0, "Divisi", t_style)
		sheet.write_string(1, 1, "Marketing", t_style)
		sheet.write_string(4, 0, "PERINCIAN PEMENUHAN PEMBELIAN PRODUCT", t_style)
		date_start = datetime.strptime(wiz.start_date, DF).strftime("%d %b %Y")
		date_end = datetime.strptime(wiz.end_date, DF).strftime("%d %b %Y")
		sheet.write_string(5, 0, "PERIODE " + date_start + ' - ' + date_end, t_style)

		# TABLE HEADER
		h_cell_format = {'font_name': 'Arial', 'font_size': 8, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'border': 1}
		h_style = workbook.add_format(h_cell_format)
		
		
		sheet.merge_range(8, 0, 9, 0, "No.", h_style)
		sheet.merge_range(8, 1, 9, 1, "Jenis Product.", h_style)
		sheet.merge_range(8, 2, 9, 2, "Tanggal Transaksi/ Kontrak", h_style)
		sheet.merge_range(8, 3, 9, 3, "No Kontrak Pembembelian", h_style)
		sheet.merge_range(8, 4, 9, 4, "Nama Supplier / Relasi.", h_style)
		sheet.merge_range(8, 5, 9, 5, "Tonase Kontrak.", h_style)
		sheet.merge_range(8, 6, 9, 6, "Syarat Penyerahan", h_style)
		sheet.merge_range(8, 7, 9, 7, "Tonase Bayar.", h_style)
		sheet.merge_range(8, 8, 9, 8, "Transporter", h_style)
		sheet.merge_range(8, 9, 8, 10, "DO Besar Transporter", h_style)
		sheet.write_string(9, 9, "Nomor", h_style)
		sheet.write_string(9, 10, "Tonase", h_style)
		sheet.merge_range(8, 11, 9, 11, "Tgl.Trakhir Pengiriman", h_style)
		sheet.merge_range(8, 12, 8, 14, "Timbangan Pabrik (Total)", h_style)
		sheet.write_string(9, 12, "Brutto", h_style)
		sheet.write_string(9, 13, "Terra", h_style)
		sheet.write_string(9, 14, "Netto", h_style)
		sheet.merge_range(8, 15, 8, 17, "Timbangan Supplier (Total)", h_style)
		sheet.write_string(9, 15, "Brutto", h_style)
		sheet.write_string(9, 16, "Terra", h_style)
		sheet.write_string(9, 17, "Netto", h_style)
		sheet.merge_range(8, 18, 9, 18, "Susut", h_style)
		sheet.merge_range(8, 19, 8, 21, "Outstanding", h_style)
		sheet.write_string(9, 19, "Kontrak", h_style)
		sheet.write_string(9, 20, "DO Transporter", h_style)
		sheet.write_string(9, 21, "Bayar", h_style)
		sheet.merge_range(8, 22, 9, 22, "Keterangan", h_style)

		for col_pos in range(0, 23):
			sheet.write_number(10, col_pos, col_pos+1, h_style)

		# TABLE DETAIL
		c_cell_format = {'font_name': 'Arial', 'font_size': 8, 'valign': 'top', 'align': 'left', 'border': 1}
		c_style = workbook.add_format(c_cell_format)
		c_datetime_format = c_cell_format.copy()
		c_datetime_format.update({'align': 'center', 'num_format': 'd mmm yy'})
		c_datetime_style = workbook.add_format(c_datetime_format)
		c_cell_format2 = c_cell_format
		c_cell_format2.update({'align': 'center','align':'vcenter'})
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
		row = 11
		ScaleMetro = self.env['weighbridge.scale.metro']
		for po in purchasesline:
			row_end = 0
			# Part 1: Detail PO
			seq += 1
			SumInv = len(po.move_ids)

			date_order = datetime.strptime(po.date_order, DT)

			SumPick = len(po.move_ids)

			TonaseBayar = 0

			if po.invoice_lines:
				TonaseBayar = sum(l.quantity for l in po.invoice_lines)
			
			sheet.write(row, 0, seq, c_style2)
			sheet.write_string(row, 1, po.product_id.name  or '', c_style)
			sheet.write_datetime(row, 2, date_order or '', c_datetime_style)
			sheet.write_string(row, 3, po.order_id.partner_ref or '', c_style)
			sheet.write_string(row, 4, po.order_id.partner_id.name, c_style)
			sheet.write_number(row, 5, po.product_qty, num_style)

			sheet.write_string(row, 6, po.order_id.incoterm_id.name or '', c_style2)
			sheet.write_number(row, 7, TonaseBayar, num_style)

			NoDo = Transporter = PickingDone = False
			QtyBrutto = QtyTarra = QtyNetto = TotalTonase = 0
			VQtyBrutto = VQtyTarra = VQtyNetto = VTotalTonase = 0
			for x in po.move_ids:
				self.env.cr.execute("""
					SELECT weighbridge_id
					FROM weighbridge_metro_picking_rel
					WHERE picking_id = %s """, (x.picking_id.id,))
				result = self.env.cr.fetchall()

				if x.picking_id.date_done:
					PickingDone = datetime.strptime(x.picking_id.date_done, DT)

				for i in result:
					DataTimbanganMetro = ScaleMetro.search([('id', '=', i[0])])

					# Transporter = DataTimbanganMetro.transporter_id.name
					Transporter = DataTimbanganMetro.TIMBANG_TRANSPORTER
					NoDo = DataTimbanganMetro.TIMBANG_DO
					QtyBrutto += DataTimbanganMetro.TIMBANG_IN_WEIGHT
					QtyTarra += DataTimbanganMetro.TIMBANG_OUT_WEIGHT
					QtyNetto += DataTimbanganMetro.TIMBANG_TOTALBERAT
					TotalTonase += x.product_uom_qty
					VQtyBrutto += DataTimbanganMetro.bruto_pks
					VQtyTarra += DataTimbanganMetro.tarra_pks
					VQtyNetto += DataTimbanganMetro.TIMBANG_NETTOPKS
					VTotalTonase += DataTimbanganMetro.TIMBANG_NETTOPKS
				
			sheet.write_string(row, 8, Transporter  or '', c_style2)
			sheet.write_string(row, 9, NoDo  or '', c_style2)
			sheet.write_number(row, 10, po.product_qty, num_style)
			if PickingDone:
				sheet.write_datetime(row, 11, PickingDone  or '', c_datetime_style)
			else:
				sheet.write_string(row, 11, '', c_datetime_style)
			sheet.write_number(row, 12, QtyBrutto, num_style)
			sheet.write_number(row, 13, QtyTarra, num_style)
			sheet.write_number(row, 14, QtyNetto, num_style)
			sheet.write_number(row, 15, VQtyBrutto, num_style)
			sheet.write_number(row, 16, VQtyTarra, num_style)
			sheet.write_number(row, 17, VQtyNetto, num_style)
			sheet.write_formula(row, 18, '=R%s-O%s'%(str(row+1),str(row+1)), num_style)
			# sheet.write_formula(row, 19, """=IF(G%s="LOCO";F%s-R%s;F%s-O%s)"""%(str(row+1),str(row+1),str(row+1),str(row+1),str(row+1)), num_style)
			sheet.write_number(row, 19, (po.product_qty-VQtyNetto) if (po.order_id.incoterm_id.name or '')=='LOCO' else (po.product_qty-QtyNetto), num_style)
			sheet.write_formula(row, 20, '=K%s-O%s'%(str(row+1),str(row+1)), num_style)
			sheet.write_formula(row, 21, '=F%s-H%s'%(str(row+1),str(row+1)), num_style)
			sheet.write_string(row, 22, '', c_style)
			row += 1

		sheet.set_margins(0.5, 0.5, 0.5, 0.5)
		sheet.print_area(0, 0, row, 23) #print area of selected cell
		sheet.set_paper(9)  # set A4 as page format
		sheet.center_horizontally()
		pages_horz = 1 # wide
		pages_vert = 0 # as long as necessary
		sheet.fit_to_pages(pages_horz, pages_vert)
		pass
GenerateReporPerincianPemenuhanPembelianBarangXlsx('report.report_generate_perincian_pemenuhan_pembelian_barang_xls', 'wizard.generate.report.purchase.order')




