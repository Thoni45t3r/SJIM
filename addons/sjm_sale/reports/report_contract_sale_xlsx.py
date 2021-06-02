from odoo import api, fields, models

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.addons.c10i_amount_in_words.amount_in_words import amount_in_words as convert
from xlsxwriter.utility import xl_rowcol_to_cell
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT

class ReportSaleXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, objects):
        xlsx_style = {
            'arial': {'font_name': 'Arial', 'font_size': 10},
            'xlsx_title': {'bold': True, 'font_size':12, 'align': 'left'},
            'xlsx_cell': {'font_size':8},
            'borders_all': {'border':1},
            'border_top': {'top':1},
            'border_bottom': {'bottom':1},
            'bold': {'bold':True},
            'underline': {'underline': True},
            'italic': {'italic': True},

            'left': {'align': 'left'},
            'center': {'align': 'center'},
            'right': {'align': 'right'},
            'top': {'valign': 'top'},
            'vcenter': {'valign': 'center'},
            'bottom': {'valign': 'bottom'},
            'wrap': {'text_wrap':True},
            
            'fill_blue': {'pattern':1, 'fg_color':'#99fff0'},
            'fill_grey': {'pattern':1, 'fg_color':'#e0e0e0'},
            'fill': {'pattern': 1, 'fg_color': '#ffff99'},

            'decimal': {'num_format':'#,##0.00;-#,##0.00;-'},
            'decimal4': {'num_format':'#,##0.0000;-#,##0.0000;-'},
            'percentage': {'num_format': '0%'},
            'percentage2': {'num_format': '0.00%'},
            'integer': {'num_format':'#,##0;-#,##0;-'},
            'date': {'num_format': 'dd-mmm-yy'},
            'date2': {'num_format': 'dd/mm/yy'},
        }

        def get_kop_address(partner):
            address = ""
            if partner.street:
                address+= partner.street+". "
            if partner.street2:
                address+= partner.street2+". "
            if partner.city:
                if partner.state_id:
                    address+= partner.city + ", " + partner.state_id.name + ". "
                else:
                    address+= partner.city + ". "
            if partner.country_id:
                address+= partner.country_id.name + ". "
            return address

        def get_address(partner):
            address = ""
            if partner.street:
                address+= partner.street+". "
            if partner.street2:
                address+= partner.street2+". "
            if partner.city:
                if partner.state_id:
                    address+= partner.city + ", " + partner.state_id.name + ". "
                else:
                    address+= partner.city + ". "
            if partner.country_id:
                address+= partner.country_id.name + ". "
            return address

        months = {1: 'Januari',
            2: 'Februari',
            3: 'Maret',
            4: 'April',
            5: 'Mei',
            6: 'Juni',
            7: 'Juli',
            8: 'Agustus',
            9: 'September',
            10: 'Oktober',
            11: 'November',
            12: 'Desember'}

        for sale in objects:
            sheet_name = sale.name
            sheet = workbook.add_worksheet(sheet_name[:31])
            sheet.set_portrait()
            sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})
            row = 0

            column_width = [5, 25, 3,  10, 25, 30, 5]
            for col_pos in range(0,7):
                sheet.set_column(col_pos, col_pos, column_width[col_pos])
            # KOP SUART
            kop1_cell_format = {'font_name': 'Calisto MT', 'font_size': 18, 'bold': True, 'valign': 'top', 'align': 'centre'}
            kop1_style = workbook.add_format(kop1_cell_format)
            sheet.merge_range(row, 1, row, 5, sale.company_id.name.upper(), kop1_style)
            row += 1
            
            kop2_cell_format = {'font_name': 'Century Gothic', 'font_size': 8, 'italic': True, 'valign': 'top', 'align': 'centre'}
            kop2_style = workbook.add_format(kop2_cell_format)
            address_1 = ""
            if sale.company_id.street:
                address_1+= sale.company_id.street+". "
            if sale.company_id.street2:
                address_1+= sale.company_id.street2+". "
            #override address_1
            address_1 = "Jl. Dr. Susilo No. 83 Pahoman - Teluk Betung"
            sheet.merge_range(row, 1, row, 5, address_1 or " ", kop2_style)
            row += 1
            address_2 = ""
            if sale.company_id.city:
                if sale.company_id.state_id:
                    address_2+= sale.company_id.city + ", " + sale.company_id.state_id.name + ". "
                else:
                    address_2+= sale.company_id.city + ". "
            if sale.company_id.zip:
                address_2 += " " + sale.company_id.zip
            #override address_2
            address_2 = "Bandar Lampung 35213"
            sheet.merge_range(row, 1, row, 5, address_2 or " ", kop2_style)
            row += 1
            address_3 = ""
            if sale.company_id.phone:
                address_3 += "Phone " + sale.company_id.phone + ". "
            if sale.company_id.fax:
                address_3 += "Fax " + sale.company_id.fax + ". "
            if sale.company_id.email:
                address_3 += "Email: " + sale.company_id.email + "."
            kop3_cell_format = kop2_cell_format.copy()
            kop3_cell_format.update({'bottom': 6})
            kop3_style = workbook.add_format(kop3_cell_format)
            sheet.merge_range(row, 1, row, 5, address_3 or " ", kop3_style)
            row += 1
            
            # kop3_cell_format = {'bottom': 6}
            # kop3_style = workbook.add_format(kop3_cell_format)
            # sheet.merge_range(row, 1, row, 5, " ", kop3_style)
            # row += 1
            
            # HEADER
            header1_cell_format = {'font_name': 'Calisto MT', 'font_size': 10, 'italic': True, 'underline': 1, 'valign': 'top', 'align': 'centre'}
            header1_style = workbook.add_format(header1_cell_format)
            sheet.merge_range(row, 1, row, 5, "SURAT JUAL - BELI", header1_style)
            row += 1
            header2_cell_format = {'font_name': 'Calisto MT', 'font_size': 10, 'valign': 'top', 'align': 'centre'}
            header2_style = workbook.add_format(header2_cell_format)
            sheet.merge_range(row, 1, row, 5, "No. %s"%sale.name, header2_style)
            row += 2

            content_cell_format = {'font_name': 'Century Gothic', 'font_size': 9, 'valign': 'top', 'align': 'left'}
            contect_style = workbook.add_format(content_cell_format)
            content2_cell_format = content_cell_format.copy()
            content2_cell_format.update({'text_wrap': True})
            contect2_style = workbook.add_format(content2_cell_format)
            numeric_cell_format = content_cell_format.copy()
            numeric_cell_format.update({'align': 'right', 'num_format':'#,##0;-#,##0;-'})
            numeric_style = workbook.add_format(numeric_cell_format)
            # PEMBUKA
            sheet.merge_range(row, 1, row, 5, "Yang bertandatangan dibawah ini telah menetapkan surat jual beli sebagai berikut :", contect_style)
            row += 1
            # KONTEN KONTRAK
            sheet.write_string(row, 1, "PENJUAL", contect_style)
            sheet.write_string(row, 2, " : ", contect_style)
            sheet.write_string(row, 3, sale.company_id.name.upper(), contect_style)
            row += 1
            sheet.merge_range(row, 3, row, 5, get_address(sale.company_id.partner_id), contect2_style)
            row += 1
            sheet.write_string(row, 1, "NPWP", contect_style)
            sheet.write_string(row, 2, " : ", contect_style)
            sheet.write_string(row, 3, sale.company_id.vat or '', contect_style)
            row += 2

            sheet.write_string(row, 1, "PEMBELI", contect_style)
            sheet.write_string(row, 2, " : ", contect_style)
            sheet.write_string(row, 3, sale.partner_id.name.upper(), contect_style)
            row += 1
            sheet.merge_range(row, 3, row, 5, get_address(sale.partner_id), contect2_style)
            row += 1
            sheet.write_string(row, 1, "NPWP", contect_style)
            sheet.write_string(row, 2, " : ", contect_style)
            sheet.write_string(row, 3, sale.partner_id.npwp_number or '', contect_style)
            row += 2

            order_line = sale.order_line[-1]
            sheet.write_string(row, 1, "JENIS BARANG", contect_style)
            sheet.write_string(row, 2, " : ", contect_style)
            sheet.write_string(row, 3, order_line.product_id.name, contect_style)
            row += 1
            sheet.write_string(row, 1, "QUANTITY", contect_style)
            sheet.write_string(row, 2, " : ", contect_style)
            sheet.write_number(row, 3, order_line.product_uom_qty, numeric_style)
            sheet.write_string(row, 4, order_line.product_uom.name, contect_style)
            row += 1
            sheet.write_string(row, 1, "HARGA", contect_style)
            sheet.write_string(row, 2, " : ", contect_style)
            sheet.write_number(row, 3, order_line.price_unit, numeric_style)
            sheet.write_string(row, 4, "/%s (EXCLUDE PPN)"%order_line.product_uom.name, contect_style)
            row += 1
            sheet.write_string(row, 1, "JUMLAH", contect_style)
            sheet.write_string(row, 2, " : ", contect_style)
            sheet.write_number(row, 3, order_line.price_subtotal, numeric_style)
            sheet.write_string(row, 4, sale.currency_id.name, contect_style)
            row += 1
            
            amount_text = convert(order_line.price_subtotal) or "Nol"
            sheet.merge_range(row, 3, row, 5, "(%s)"%amount_text.upper(), contect2_style)
            row += 1
            if sale.delivery_of_goods:
                sheet.write_string(row, 1, "PENYERAHAN", contect_style)
                sheet.write_string(row, 2, " : ", contect_style)
                sheet.merge_range(row, 3, row, 5, sale.delivery_of_goods, contect2_style)
                row += 1
            if sale.source_warehouse_note:
                sheet.write_string(row, 1, "ASAL BARANG", contect_style)
                sheet.write_string(row, 2, " : ", contect_style)
                sheet.merge_range(row, 3, row, 5, sale.source_warehouse_note, contect2_style)
                row += 1
            if sale.quantity_note:
                sheet.write_string(row, 1, "KUANTITAS", contect_style)
                sheet.write_string(row, 2, " : ", contect_style)
                sheet.merge_range(row, 3, row, 5, sale.quantity_note, contect2_style)
                row += 1
            if sale.quality_ffa or sale.quality_mni or sale.quality_iv or sale.quality_note:
                sheet.write_string(row, 1, "KUALITAS", contect_style)
                sheet.write_string(row, 2, " : ", contect_style)
                if sale.quality_ffa:
                    sheet.write_string(row, 3, "FFA", contect_style)
                    sheet.write_string(row, 4, "= %s %%"%sale.quality_ffa, contect_style)
                    row += 1
                if sale.quality_mni:
                    sheet.write_string(row, 3, "M & I", contect_style)
                    sheet.write_string(row, 4, "= %s %%"%sale.quality_mni, contect_style)
                    row += 1
                if sale.quality_iv:
                    sheet.write_string(row, 3, "IV", contect_style)
                    sheet.write_string(row, 4, "= %s %%"%sale.quality_iv, contect_style)
                    row += 1
                if sale.quality_note:
                    sheet.merge_range(row, 3, row, 5, sale.quality_note, contect2_style)
                    row += 1
            if sale.quality_claim:
                sheet.write_string(row, 1, "PENALTY / DENDA MUTU", contect_style)
                sheet.write_string(row, 2, " : ", contect_style)
                sheet.merge_range(row, 3, row, 5, sale.quality_claim, contect2_style)
                row += 1
            if sale.payment_term_note:
                sheet.write_string(row, 1, "PEMBAYARAN", contect_style)
                sheet.write_string(row, 2, " : ", contect_style)
                sheet.merge_range(row, 3, row, 5, sale.payment_term_note, contect2_style)
                row += 1
            if sale.partner_bank_id:
                sheet.write_string(row, 1, "DITRANSFER KE REKENING", contect_style)
                sheet.write_string(row, 2, " : ", contect_style)
                sheet.merge_range(row, 3, row, 5, sale.partner_bank_id.bank_id.name, contect_style)
                row += 1
                sheet.merge_range(row, 3, row, 5, sale.partner_bank_id.acc_number, contect_style)
                row += 1
                sheet.merge_range(row, 3, row, 5, 'a.n %s'%sale.partner_bank_id.partner_id.name, contect_style)
                row += 1
            if sale.picking_location_note:
                sheet.write_string(row, 1, "LOKASI PEMUATAN", contect_style)
                sheet.write_string(row, 2, " : ", contect_style)
                sheet.merge_range(row, 3, row, 5, sale.picking_location_note, contect2_style)
                row += 1
            if sale.other_claim:
                sheet.write_string(row, 1, "LAIN - LAIN", contect_style)
                sheet.write_string(row, 2, " : ", contect_style)
                sheet.merge_range(row, 3, row, 5, sale.other_claim, contect2_style)
                row += 1

            # PENUTUP
            sheet.merge_range(row, 1, row, 5, "Demikian Surat Jual - Beli ini disepakati tanpa ada tekanan dari pihak manapun juga, dan dibuat dalam rangkap 2 (dua)  masing - masing bermaterai cukup dan mempunyai kekuatan hukum yang sama.", contect2_style)
            row += 2
            # KOLOM TANDA TANGAN
            date_order = datetime.strptime(sale.date_order, DT).strftime('%d %B %Y')
            date_order2 = datetime.strptime(sale.date_order, DT)
            day = str(date_order2.day)
            month = months.get(date_order2.month,'Unknown')
            year = str(date_order2.year)
            sheet.write_string(row, 5, "%s, %s %s %s"%(sale.sign_city or 'BANDAR LAMPUNG', str(int(day)), month, year), contect_style)
            row += 1
            sheet.write_string(row, 1, "PERSETUJUAN PEMBELI", contect_style)
            sheet.write_string(row, 5, "PERSETUJUAN PENJUAL", contect_style)
            row += 1
            sheet.write_string(row, 1, sale.partner_id.name.upper(), contect_style)
            sheet.write_string(row, 5, sale.company_id.name.upper(), contect_style)
            row += 5
            sheet.write_string(row, 1, sale.sign_buyer, contect_style)
            sheet.write_string(row, 5, sale.sign_seller, contect_style)
            row += 1
            if sale.sign_buyer_position or sale.sign_seller_position:
                content3_cell_format = content_cell_format.copy()
                content3_cell_format.update({'font_size': 8, 'bold': True})
                contect3_style = workbook.add_format(content3_cell_format)
                sheet.write_string(row, 1, sale.sign_buyer_position or '', contect3_style)
                sheet.write_string(row, 5, sale.sign_seller_position or '', contect3_style)
                row += 1

            content4_cell_format = content_cell_format.copy()
            content4_cell_format.update({'font_size': 7.5})
            contect4_style = workbook.add_format(content4_cell_format)
            sheet.write_string(row, 1, "NB. setelah ditandatangani mohon lembar copy dikirim kembali ke PT.SJIM", contect4_style)
            row += 1

            sheet.set_margins(0.5, 0.5, 0.5, 0.5)
            sheet.print_area(0, 0, row, 6) #print area of selected cell
            sheet.set_paper(9)  # set A4 as page format
            sheet.center_horizontally()
            pages_horz = 1 # wide
            pages_vert = 0 # as long as necessary
            sheet.fit_to_pages(pages_horz, pages_vert)
        pass

ReportSaleXlsx('report.report_contract_sale_xlsx_new', 'sale.order')