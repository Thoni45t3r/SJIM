from odoo import api, fields, models

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from xlsxwriter.utility import xl_rowcol_to_cell
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT

class ReportRekapPurchaseXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, objects):
        wiz = objects
        domain = [('company_id','=',wiz.company_id.id),('state','in',['purchase','done','draft']),\
            ('date_order','>=',wiz.date_start + ' 00:00:00'), ('date_order','<=',wiz.date_stop + ' 23:59:59')]
        if wiz.doc_type_ids.filtered(lambda x: x.purchase):
            domain.append(('doc_type_id','in',wiz.doc_type_ids.filtered(lambda x: x.purchase).ids))
        purchases = self.env['purchase.order'].search(domain)
        sheet_name = 'Rekap Purchase'
        sheet = workbook.add_worksheet(sheet_name)
        sheet.set_landscape()
        sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})

        column_width = [4, 12, 12, 8, 5, 20, 12, 10, 20, 20, 10, 5, 10, 12, 5, 7, 7, 7, 7, 7, 15, 12, 8, 10, 12, 12, 15, 15, 8, 10, 12, 12, 15, 15, 8, 10]
        for col_pos in range(0,36):
            sheet.set_column(col_pos, col_pos, column_width[col_pos])

        # TITLE
        t_cell_format = {'font_name': 'Arial', 'font_size': 15, 'bold': True, 'valign': 'vcenter', 'align': 'left'}
        t_style = workbook.add_format(t_cell_format)
        sheet.write_string(0, 0, wiz.company_id.name.upper(), t_style)
        sheet.write_string(1, 0, "REKAP PURCHASE ORDER", t_style)
        # TABLE HEADER
        h_cell_format = {'font_name': 'Arial', 'font_size': 8, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'border': 1}
        h_style = workbook.add_format(h_cell_format)
        sheet.merge_range(3, 0, 4, 0, "No.", h_style)
        sheet.merge_range(3, 1, 3, 3, "Purchase", h_style)
        sheet.write_string(4, 1, "Order No.", h_style)
        sheet.write_string(4, 2, "Vendor Ref.", h_style)
        sheet.write_string(4, 3, "Tanggal", h_style)
        sheet.merge_range(3, 4, 3, 5, "Vendor", h_style)
        sheet.write_string(4, 4, "Kode", h_style)
        sheet.write_string(4, 5, "Nama", h_style)
        sheet.merge_range(3, 6, 4, 6, "No. PR", h_style)
        sheet.merge_range(3, 7, 3, 11, "Barang", h_style)
        sheet.write_string(4, 7, "Kode", h_style)
        sheet.write_string(4, 8, "Nama", h_style)
        sheet.write_string(4, 9, "Deskripsi", h_style)
        sheet.write_string(4, 10, "Jumlah", h_style)
        sheet.write_string(4, 11, "Satuan", h_style)
        sheet.merge_range(3, 12, 4, 12, "Harga\nSatuan", h_style)
        sheet.merge_range(3, 13, 4, 13, "Total\nHarga", h_style)
        sheet.merge_range(3, 14, 4, 14, "Mata\nUang", h_style)
        sheet.merge_range(3, 15, 3, 19, "Pajak", h_style)
        sheet.write_string(4, 15, "PPN", h_style)
        sheet.write_string(4, 16, "PBBKB", h_style)
        sheet.write_string(4, 17, "PPH PSL 23 (2%)", h_style)
        sheet.write_string(4, 18, "PPH PSL 22 (-2%)", h_style)
        sheet.write_string(4, 19, "PPH PSL 22 (-4%)", h_style)
        sheet.merge_range(3, 20, 4, 20, "Total\nHarga PO", h_style)
        sheet.merge_range(3, 21, 3, 23, "Detail Penerimaan", h_style)
        sheet.write_string(4, 21, "Referensi", h_style)
        sheet.write_string(4, 22, "Tanggal", h_style)
        sheet.write_string(4, 23, "Jumlah", h_style)
        sheet.merge_range(3, 24, 3, 29, "Detail Uang Muka", h_style)
        sheet.write_string(4, 24, "Invioce", h_style)
        sheet.write_string(4, 25, "Ref", h_style)
        sheet.write_string(4, 26, "Faktur Pajak", h_style)
        sheet.write_string(4, 27, "Amount", h_style)
        sheet.write_string(4, 28, "Tanggal", h_style)
        sheet.write_string(4, 29, "Pembayaran", h_style)
        sheet.merge_range(3, 30, 3, 35, "Detail Tagihan", h_style)
        sheet.write_string(4, 30, "Invioce", h_style)
        sheet.write_string(4, 31, "Ref", h_style)
        sheet.write_string(4, 32, "Faktur Pajak", h_style)
        sheet.write_string(4, 33, "Amount", h_style)
        sheet.write_string(4, 34, "Tanggal", h_style)
        sheet.write_string(4, 35, "Pembayaran", h_style)

        for col_pos in range(0, 36):
            sheet.write_number(5, col_pos, col_pos+1, h_style)

        # TABLE DETAIL
        c_cell_format = {'font_name': 'Arial', 'font_size': 8, 'valign': 'top', 'align': 'left'}
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
        row = 6
        for po in purchases:
            row_start = row_stop = row
            # Part 1: Detail PO
            seq += 1
            sheet.write(row, 0, seq, c_style2)
            for line in po.order_line:
                sheet.write_string(row, 1, po.name or '', c_style)
                sheet.write_string(row, 2, po.partner_ref or '', c_style)
                # date_order = datetime.strptime(po.date_order, DT).strftime('%d/%m/%y')
                date_order = datetime.strptime(po.date_order, DT)
                sheet.write_datetime(row, 3, date_order, c_datetime_style)
                sheet.write_string(row, 4, '', c_style)
                sheet.write_string(row, 5, po.partner_id.name, c_style)
                sheet.write_string(row, 6, line.request_id and line.request_id.name or '', c_style)
                sheet.write_string(row, 7, line.product_id and line.product_id.default_code or '', c_style)
                sheet.write_string(row, 8, line.product_id and line.product_id.name or '', c_style)
                l_desc = line.name
                sheet.write_string(row, 9, l_desc, c_style)
                sheet.write_number(row, 10, line.product_qty or 0.0, num_style)
                col_qty = xl_rowcol_to_cell(row, 10)
                sheet.write_string(row, 11, line.product_uom and line.product_uom.name or '', c_style)
                price_unit = line._get_stock_move_price_unit()
                sheet.write_number(row, 12, price_unit, num_style)
                col_price = xl_rowcol_to_cell(row, 12)
                sheet.write_formula(row, 13, "=%s*%s"%(col_qty,col_price), num_style)
                col_subtotal = xl_rowcol_to_cell(row, 13)
                sheet.write_string(row, 14, po.currency_id.name, c_style)
                taxes = line.taxes_id.with_context(round=False).compute_all(
                    price_unit*line.product_qty, currency=po.currency_id, quantity=1.0, product=line.product_id, partner=po.partner_id
                    )['taxes']
                ppn = sum(x['amount'] for x in taxes if 'PPN' in x['name'])
                pbbkb = sum(x['amount'] for x in taxes if 'PBBKB' in x['name'])
                pph22_3 = sum(x['amount'] for x in taxes if 'PPH PSL 22 (0,3%)' in x['name'])
                pph23_2 = sum(x['amount'] for x in taxes if 'WITHOLDING PSL 23 (-2%)' in x['name'])
                pph23_4 = sum(x['amount'] for x in taxes if 'WITHOLDING PSL 23 (-4%)' in x['name'])
                sheet.write_number(row, 15, ppn or 0.0, num_style)
                col_ppn = xl_rowcol_to_cell(row, 15)
                sheet.write_number(row, 16, pbbkb or 0.0, num_style)
                col_pbbkb = xl_rowcol_to_cell(row, 16)
                sheet.write_number(row, 17, pph22_3 or 0.0, num_style)
                col_pph22_3 = xl_rowcol_to_cell(row, 17)
                sheet.write_number(row, 18, pph23_2 or 0.0, num_style)
                col_pph23_2 = xl_rowcol_to_cell(row, 18)
                sheet.write_number(row, 19, pph23_4 or 0.0, num_style)
                col_pph23_4 = xl_rowcol_to_cell(row, 19)
                sheet.write_formula(row, 20, "=%s+%s+%s+%s+%s+%s"%(col_subtotal,col_ppn,col_pbbkb,col_pph22_3,col_pph23_2,col_pph23_4), num_style)

                # Receipt Status
                if line.move_ids.filtered(lambda x: x.state=='done'):
                    for move in line.move_ids.filtered(lambda x: x.state=='done'):
                        sheet.write_string(row, 21, move.picking_id.name, c_style)
                        date_picking = datetime.strptime(move.date, DT)
                        sheet.write_datetime(row, 22, date_picking, c_datetime_style)
                        sheet.write_number(row, 23, move.product_uom_qty or 0.0, num_style)
                        row += 1
                else:
                    row += 1
            row_stop = row-1 if (row-1)>row_stop else row_stop
            # Part 2: Uang Muka
            row = row_start
            for adv in po.advance_invoice_ids.filtered(lambda x: x.state in ('open','paid')):
                sheet.write_string(row, 24, adv.number or '', c_style)
                sheet.write_string(row, 25, adv.reference or '', c_style)
                sheet.write_string(row, 26, adv.nomer_seri_faktur_pajak_bill or '', c_style)
                sheet.write_number(row, 27, adv.amount_total, num_style)
                date_invoice = datetime.strptime(adv.date_invoice, DF)
                sheet.write_datetime(row, 28, date_invoice, c_datetime_style)
                sheet.write_string(row, 29, "", c_style)
                row += 1 
            row_stop = (row-1) if (row-1)>row_stop else row_stop

            row = row_start
            for inv in po.invoice_ids.filtered(lambda x: x.state in ('open','paid')):
                sheet.write_string(row, 30, inv.number or '', c_style)
                sheet.write_string(row, 31, inv.reference or '', c_style)
                sheet.write_string(row, 32, inv.nomer_seri_faktur_pajak_bill or '', c_style)
                sheet.write_number(row, 33, inv.amount_total, num_style)
                date_invoice = datetime.strptime(inv.date_invoice, DF)
                sheet.write_datetime(row, 34, date_invoice, c_datetime_style)
                if inv.payment_move_line_ids:
                    date_paymnet = False
                    for pay in inv.payment_move_line_ids:
                        date_payment = datetime.strptime(pay.date, DF)
                    sheet.write_datetime(row, 35, date_payment, c_datetime_style)
                else:
                    sheet.write_string(row, 35, "", c_style)

                row += 1
            row_stop = (row-1) if (row-1)>row_stop else row_stop
            row = row_stop + 1

        sheet.set_margins(0.5, 0.5, 0.5, 0.5)
        sheet.print_area(0, 0, row, 23) #print area of selected cell
        sheet.set_paper(9)  # set A4 as page format
        sheet.center_horizontally()
        pages_horz = 1 # wide
        pages_vert = 0 # as long as necessary
        sheet.fit_to_pages(pages_horz, pages_vert)
        pass
ReportRekapPurchaseXlsx('report.report_purchase_report_rekap_xlsx2', 'wizard.purchase.report')

class ReportRekapPurchaseSPKXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, objects):
        wiz = objects
        domain = [('company_id','=',wiz.company_id.id),('state','in',['purchase','done','draft']),\
            ('date_order','>=',wiz.date_start + ' 00:00:00'), ('date_order','<=',wiz.date_stop + ' 23:59:59')]
        if wiz.doc_type_ids.filtered(lambda x : x.spk):
            domain.append(('doc_type_id','in',wiz.doc_type_ids.filtered(lambda x : x.spk).ids))
        purchases = self.env['purchase.order'].search(domain)
        sheet_name = 'Rekap Purchase'
        sheet = workbook.add_worksheet(sheet_name)
        sheet.set_landscape()
        sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})

        column_width = [4, 12, 12, 8, 5, 20, 12, 10, 20, 20, 10, 5, 10, 12, 5, 7, 7, 7, 15, 12, 12, 15, 15, 8, 10, 12, 12, 15, 15, 8, 10]
        for col_pos in range(0,31):
            sheet.set_column(col_pos, col_pos, column_width[col_pos])

        # TITLE
        t_cell_format = {'font_name': 'Arial', 'font_size': 15, 'bold': True, 'valign': 'vcenter', 'align': 'left'}
        t_style = workbook.add_format(t_cell_format)
        sheet.write_string(0, 0, wiz.company_id.name.upper(), t_style)
        sheet.write_string(1, 0, "REKAP SERVICE ORDER (SPK)", t_style)
        # TABLE HEADER
        h_cell_format = {'font_name': 'Arial', 'font_size': 8, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'border': 1}
        h_style = workbook.add_format(h_cell_format)
        sheet.merge_range(3, 0, 4, 0, "No.", h_style)
        sheet.merge_range(3, 1, 3, 3, "Purchase", h_style)
        sheet.write_string(4, 1, "Order No.", h_style)
        sheet.write_string(4, 2, "Vendor Ref.", h_style)
        sheet.write_string(4, 3, "Tanggal", h_style)
        sheet.merge_range(3, 4, 3, 5, "Vendor", h_style)
        sheet.write_string(4, 4, "Kode", h_style)
        sheet.write_string(4, 5, "Nama", h_style)
        sheet.merge_range(3, 6, 4, 6, "No. PR", h_style)
        sheet.merge_range(3, 7, 3, 11, "Jasa", h_style)
        sheet.write_string(4, 7, "Kode", h_style)
        sheet.write_string(4, 8, "Nama", h_style)
        sheet.write_string(4, 9, "Deskripsi", h_style)
        sheet.write_string(4, 10, "Jumlah", h_style)
        sheet.write_string(4, 11, "Satuan", h_style)
        sheet.merge_range(3, 12, 4, 12, "Harga\nSatuan", h_style)
        sheet.merge_range(3, 13, 4, 13, "Total\nHarga", h_style)
        sheet.merge_range(3, 14, 4, 14, "Mata\nUang", h_style)
        sheet.merge_range(3, 15, 3, 17, "Pajak", h_style)
        sheet.write_string(4, 15, "PPN", h_style)
        sheet.write_string(4, 16, "PPH PSL 22 (-2%)", h_style)
        sheet.write_string(4, 17, "PPH PSL 22 (-4%)", h_style)
        sheet.merge_range(3, 18, 4, 18, "Total\nHarga PO", h_style)
        sheet.merge_range(3, 19, 3, 24, "Detail Uang Muka", h_style)
        sheet.write_string(4, 19, "Invioce", h_style)
        sheet.write_string(4, 20, "Ref", h_style)
        sheet.write_string(4, 21, "Faktur Pajak", h_style)
        sheet.write_string(4, 22, "Amount", h_style)
        sheet.write_string(4, 23, "Tanggal", h_style)
        sheet.write_string(4, 24, "Pembayaran", h_style)
        sheet.merge_range(3, 25, 3, 30, "Detail Tagihan", h_style)
        sheet.write_string(4, 25, "Invioce", h_style)
        sheet.write_string(4, 26, "Ref", h_style)
        sheet.write_string(4, 27, "Faktur Pajak", h_style)
        sheet.write_string(4, 28, "Amount", h_style)
        sheet.write_string(4, 29, "Tanggal", h_style)
        sheet.write_string(4, 30, "Pembayaran", h_style)

        for col_pos in range(0, 31):
            sheet.write_number(5, col_pos, col_pos+1, h_style)

        # TABLE DETAIL
        c_cell_format = {'font_name': 'Arial', 'font_size': 8, 'valign': 'top', 'align': 'left'}
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
        row = 6
        for po in purchases:
            row_start = row_stop = row
            # Part 1: Detail PO
            seq += 1
            sheet.write(row, 0, seq, c_style2)
            for line in po.order_line:
                sheet.write_string(row, 1, po.name or '', c_style)
                sheet.write_string(row, 2, po.partner_ref or '', c_style)
                # date_order = datetime.strptime(po.date_order, DT).strftime('%d/%m/%y')
                date_order = datetime.strptime(po.date_order, DT)
                sheet.write_datetime(row, 3, date_order, c_datetime_style)
                sheet.write_string(row, 4, '', c_style)
                sheet.write_string(row, 5, po.partner_id.name, c_style)
                sheet.write_string(row, 6, line.request_id and line.request_id.name or '', c_style)
                sheet.write_string(row, 7, line.product_id and line.product_id.default_code or '', c_style)
                sheet.write_string(row, 8, line.product_id and line.product_id.name or '', c_style)
                l_desc = line.name
                sheet.write_string(row, 9, l_desc, c_style)
                sheet.write_number(row, 10, line.product_qty or 0.0, num_style)
                col_qty = xl_rowcol_to_cell(row, 10)
                sheet.write_string(row, 11, line.product_uom and line.product_uom.name or '', c_style)
                price_unit = line._get_stock_move_price_unit()
                sheet.write_number(row, 12, price_unit, num_style)
                col_price = xl_rowcol_to_cell(row, 12)
                sheet.write_formula(row, 13, "=%s*%s"%(col_qty,col_price), num_style)
                col_subtotal = xl_rowcol_to_cell(row, 13)
                sheet.write_string(row, 14, po.currency_id.name, c_style)
                taxes = line.taxes_id.with_context(round=False).compute_all(
                    price_unit*line.product_qty, currency=po.currency_id, quantity=1.0, product=line.product_id, partner=po.partner_id
                    )['taxes']
                ppn = sum(x['amount'] for x in taxes if 'PPN' in x['name'])
                pph23_2 = sum(x['amount'] for x in taxes if 'WITHOLDING PSL 23 (-2%)' in x['name'])
                pph23_4 = sum(x['amount'] for x in taxes if 'WITHOLDING PSL 23 (-4%)' in x['name'])
                sheet.write_number(row, 15, ppn or 0.0, num_style)
                col_ppn = xl_rowcol_to_cell(row, 15)
                sheet.write_number(row, 16, pph23_2 or 0.0, num_style)
                col_pph23_2 = xl_rowcol_to_cell(row, 16)
                sheet.write_number(row, 17, pph23_4 or 0.0, num_style)
                col_pph23_4 = xl_rowcol_to_cell(row, 17)
                sheet.write_formula(row, 18, "=%s+%s+%s+%s"%(col_subtotal,col_ppn,col_pph23_2,col_pph23_4), num_style)
                row += 1
            row_stop = row-1 if (row-1)>row_stop else row_stop
            # Part 2: Uang Muka
            row = row_start
            for adv in po.advance_invoice_ids.filtered(lambda x: x.state in ('open','paid')):
                sheet.write_string(row, 19, adv.number or '', c_style)
                sheet.write_string(row, 20, adv.reference or '', c_style)
                sheet.write_string(row, 21, adv.nomer_seri_faktur_pajak_bill or '', c_style)
                sheet.write_number(row, 22, adv.amount_total, num_style)
                date_invoice = datetime.strptime(adv.date_invoice, DF)
                sheet.write_datetime(row, 23, date_invoice, c_datetime_style)
                sheet.write_string(row, 24, "", c_style)
                row += 1 
            row_stop = (row-1) if (row-1)>row_stop else row_stop

            row = row_start
            for inv in po.invoice_ids.filtered(lambda x: x.state in ('open','paid')):
                sheet.write_string(row, 25, inv.number or '', c_style)
                sheet.write_string(row, 26, inv.reference or '', c_style)
                sheet.write_string(row, 27, inv.nomer_seri_faktur_pajak_bill or '', c_style)
                sheet.write_number(row, 28, inv.amount_total, num_style)
                date_invoice = datetime.strptime(inv.date_invoice, DF)
                sheet.write_datetime(row, 29, date_invoice, c_datetime_style)
                if inv.payment_move_line_ids:
                    date_paymnet = False
                    for pay in inv.payment_move_line_ids:
                        date_payment = datetime.strptime(pay.date, DF)
                    sheet.write_datetime(row, 30, date_payment, c_datetime_style)
                else:
                    sheet.write_string(row, 30, "", c_style)

                row += 1
            row_stop = (row-1) if (row-1)>row_stop else row_stop
            row = row_stop + 1

        sheet.set_margins(0.5, 0.5, 0.5, 0.5)
        sheet.print_area(0, 0, row, 30) #print area of selected cell
        sheet.set_paper(9)  # set A4 as page format
        sheet.center_horizontally()
        pages_horz = 1 # wide
        pages_vert = 0 # as long as necessary
        sheet.fit_to_pages(pages_horz, pages_vert)
        pass
ReportRekapPurchaseSPKXlsx('report.report_purchase_report_rekap_spk_xlsx2', 'wizard.purchase.report')

class ReportRekapPurchaseSPBXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, objects):
        hari_ind = {'Sunday': 'Minggu', 'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu', 'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu'}
        wiz = objects
        domain = [('company_id','=',wiz.company_id.id),('state','in',['purchase','done','draft']),\
            ('date_order','>=',wiz.date_start + ' 00:00:00'), ('date_order','<=',wiz.date_stop + ' 23:59:59')]
        if wiz.doc_type_ids:
            domain.append(('doc_type_id','in',wiz.doc_type_ids.ids))
        purchases = self.env['purchase.order'].search(domain)
        sheet_name = 'Rekap Purchase'
        sheet = workbook.add_worksheet(sheet_name)
        sheet.set_landscape()
        sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})

        column_width = [4, 12, 12, 8, 5, 20, 12, 10, 20, 20, 10, 5, 10, 12, 5, 7, 7, 7, 7, 7, 15, 12, 8, 10, 10, 12, 8, 10, 10]
        for col_pos in range(0,29):
            sheet.set_column(col_pos, col_pos, column_width[col_pos])

        # TITLE
        t_cell_format = {'font_name': 'Arial', 'font_size': 15, 'bold': True, 'valign': 'vcenter', 'align': 'left'}
        t_style = workbook.add_format(t_cell_format)
        sheet.write_string(0, 0, wiz.company_id.name.upper(), t_style)
        sheet.write_string(1, 0, "REKAP PURCHASE - STATUS PENGIRIMAN INTERNAL", t_style)
        # TABLE HEADER
        h_cell_format = {'font_name': 'Arial', 'font_size': 8, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'border': 1}
        h_style = workbook.add_format(h_cell_format)
        sheet.merge_range(3, 0, 4, 0, "No.", h_style)
        sheet.merge_range(3, 1, 3, 3, "Purchase", h_style)
        sheet.write_string(4, 1, "Order No.", h_style)
        sheet.write_string(4, 2, "Vendor Ref.", h_style)
        sheet.write_string(4, 3, "Tanggal", h_style)
        sheet.merge_range(3, 4, 3, 5, "Vendor", h_style)
        sheet.write_string(4, 4, "Kode", h_style)
        sheet.write_string(4, 5, "Nama", h_style)
        sheet.merge_range(3, 6, 4, 6, "No. PR", h_style)
        sheet.merge_range(3, 7, 3, 11, "Barang", h_style)
        sheet.write_string(4, 7, "Kode", h_style)
        sheet.write_string(4, 8, "Nama", h_style)
        sheet.write_string(4, 9, "Deskripsi", h_style)
        sheet.write_string(4, 10, "Jumlah", h_style)
        sheet.write_string(4, 11, "Satuan", h_style)
        sheet.merge_range(3, 12, 4, 12, "Harga\nSatuan", h_style)
        sheet.merge_range(3, 13, 4, 13, "Total\nHarga", h_style)
        sheet.merge_range(3, 14, 4, 14, "Mata\nUang", h_style)
        sheet.merge_range(3, 15, 3, 19, "Pajak", h_style)
        sheet.write_string(4, 15, "PPN", h_style)
        sheet.write_string(4, 16, "PBBKB", h_style)
        sheet.write_string(4, 17, "PPH PSL 23 (2%)", h_style)
        sheet.write_string(4, 18, "PPH PSL 22 (-2%)", h_style)
        sheet.write_string(4, 19, "PPH PSL 22 (-4%)", h_style)
        sheet.merge_range(3, 20, 4, 20, "Total\nHarga PO", h_style)
        sheet.merge_range(3, 21, 3, 24, "Detail Penerimaan", h_style)
        sheet.write_string(4, 21, "Referensi", h_style)
        sheet.write_string(4, 22, "Tanggal", h_style)
        sheet.write_string(4, 23, "Jumlah", h_style)
        sheet.write_string(4, 24, "Lokasi", h_style)
        sheet.merge_range(3, 25, 3, 28, "Detail Pengiriman (Intern)", h_style)
        sheet.write_string(4, 25, "Referensi", h_style)
        sheet.write_string(4, 26, "Tanggal", h_style)
        sheet.write_string(4, 27, "Jumlah", h_style)
        sheet.write_string(4, 28, "Lokasi", h_style)

        for col_pos in range(0, 29):
            sheet.write_number(5, col_pos, col_pos+1, h_style)

        # TABLE DETAIL
        c_cell_format = {'font_name': 'Arial', 'font_size': 8, 'valign': 'top', 'align': 'left'}
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
        row = 6
        for po in purchases:
            row_start = row_stop = row
            # Part 1: Detail PO
            seq += 1
            sheet.write(row, 0, seq, c_style2)
            for line in po.order_line:
                sheet.write_string(row, 1, po.name or '', c_style)
                sheet.write_string(row, 2, po.partner_ref or '', c_style)
                # date_order = datetime.strptime(po.date_order, DT).strftime('%d/%m/%y')
                date_order = datetime.strptime(po.date_order, DT)
                sheet.write_datetime(row, 3, date_order, c_datetime_style)
                sheet.write_string(row, 4, '', c_style)
                sheet.write_string(row, 5, po.partner_id.name, c_style)
                sheet.write_string(row, 6, line.request_id and line.request_id.name or '', c_style)
                sheet.write_string(row, 7, line.product_id and line.product_id.default_code or '', c_style)
                sheet.write_string(row, 8, line.product_id and line.product_id.name or '', c_style)
                l_desc = line.name
                sheet.write_string(row, 9, l_desc, c_style)
                sheet.write_number(row, 10, line.product_qty or 0.0, num_style)
                col_qty = xl_rowcol_to_cell(row, 10)
                sheet.write_string(row, 11, line.product_uom and line.product_uom.name or '', c_style)
                price_unit = line._get_stock_move_price_unit()
                sheet.write_number(row, 12, price_unit, num_style)
                col_price = xl_rowcol_to_cell(row, 12)
                sheet.write_formula(row, 13, "=%s*%s"%(col_qty,col_price), num_style)
                col_subtotal = xl_rowcol_to_cell(row, 13)
                sheet.write_string(row, 14, po.currency_id.name, c_style)
                taxes = line.taxes_id.with_context(round=False).compute_all(
                    price_unit*line.product_qty, currency=po.currency_id, quantity=1.0, product=line.product_id, partner=po.partner_id
                    )['taxes']
                ppn = sum(x['amount'] for x in taxes if 'PPN' in x['name'])
                pbbkb = sum(x['amount'] for x in taxes if 'PBBKB' in x['name'])
                pph22_3 = sum(x['amount'] for x in taxes if 'PPH PSL 22 (0,3%)' in x['name'])
                pph23_2 = sum(x['amount'] for x in taxes if 'WITHOLDING PSL 23 (-2%)' in x['name'])
                pph23_4 = sum(x['amount'] for x in taxes if 'WITHOLDING PSL 23 (-4%)' in x['name'])
                sheet.write_number(row, 15, ppn or 0.0, num_style)
                col_ppn = xl_rowcol_to_cell(row, 15)
                sheet.write_number(row, 16, pbbkb or 0.0, num_style)
                col_pbbkb = xl_rowcol_to_cell(row, 16)
                sheet.write_number(row, 17, pph22_3 or 0.0, num_style)
                col_pph22_3 = xl_rowcol_to_cell(row, 17)
                sheet.write_number(row, 18, pph23_2 or 0.0, num_style)
                col_pph23_2 = xl_rowcol_to_cell(row, 18)
                sheet.write_number(row, 19, pph23_4 or 0.0, num_style)
                col_pph23_4 = xl_rowcol_to_cell(row, 19)
                sheet.write_formula(row, 20, "=%s+%s+%s+%s+%s+%s"%(col_subtotal,col_ppn,col_pbbkb,col_pph22_3,col_pph23_2,col_pph23_4), num_style)

                # Receipt Status
                x_start = x_stop = row
                if line.move_ids.filtered(lambda x: x.state=='done'):
                    for move in line.move_ids.filtered(lambda x: x.state=='done'):
                        sheet.write_string(row, 21, move.picking_id.name, c_style)
                        date_picking = datetime.strptime(move.date, DT)
                        sheet.write_datetime(row, 22, date_picking, c_datetime_style)
                        sheet.write_number(row, 23, move.product_uom_qty or 0.0, num_style)
                        sheet.write_string(row, 24, move.location_dest_id.name, c_style)
                        row += 1
                x_stop = (row-1) if (row-1)>x_stop else x_stop
                row = x_start
                spb_datas = self.env['stock.move'].search([('purchase_line_id2','=',line.id),('state','=','done')])
                if spb_datas:
                    for move2 in spb_datas:
                        sheet.write_string(row, 25, move2.picking_id.name, c_style)
                        date_picking = datetime.strptime(move2.date, DT)
                        sheet.write_datetime(row, 26, date_picking, c_datetime_style)
                        sheet.write_number(row, 27, move2.product_uom_qty or 0.0, num_style)
                        sheet.write_string(row, 28, move2.location_dest_id.name, c_style)
                        row += 1
                x_stop = (row-1) if (row-1)>x_stop else x_stop
                row = x_stop + 1
            row_stop = row-1 if (row-1)>row_stop else row_stop
            row = row_stop + 1

        sheet.set_margins(0.5, 0.5, 0.5, 0.5)
        sheet.print_area(0, 0, row, 28) #print area of selected cell
        sheet.set_paper(9)  # set A4 as page format
        sheet.center_horizontally()
        pages_horz = 1 # wide
        pages_vert = 0 # as long as necessary
        sheet.fit_to_pages(pages_horz, pages_vert)
        pass
ReportRekapPurchaseSPBXlsx('report.report_purchase_report_rekap_spb_xlsx2', 'wizard.purchase.report')