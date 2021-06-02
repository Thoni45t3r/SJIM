from odoo import api, fields, models

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.addons.c10i_amount_in_words.amount_in_words import amount_in_words as convert
from xlsxwriter.utility import xl_rowcol_to_cell
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT

class ReportHPPXlsx(ReportXlsx):
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

        for valuation in objects:
            # SHEET HPP
            sheet_name = "HPP"
            sheet = workbook.add_worksheet(sheet_name[:31])
            sheet.set_portrait()
            sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})

            column_width = [2, 5, 10,  10, 10, 10, 10, 15, 8, 10, 15, 5, 10, 10, 10, 5, 18, 15]
            for col_pos in range(0,18):
                sheet.set_column(col_pos, col_pos, column_width[col_pos])
            
            # TITLE
            t_cell_format = {'font_name': 'Calibri', 'font_size': 11, 'valign': 'vcenter', 'align': 'left'}
            t_style = workbook.add_format(t_cell_format)
            t2_cell_format = {'font_name': 'Calibri', 'font_size': 12, 'bold': True, 'valign': 'vcenter', 'align': 'left'}
            t2_style = workbook.add_format(t2_cell_format)
            t3_cell_format = {'font_name': 'Calibri', 'font_size': 12, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'top': 2}
            t3_style = workbook.add_format(t3_cell_format)
            sheet.write_string(0, 1, "PT SINAR JAYA INTI MULYA", t_style)
            sheet.write_string(2, 1, "LAPORAN HARGA POKOK PENJUALAN", t2_style)
            date = datetime.strptime(valuation.date_stop, DF).strftime('%d %m %Y')
            sheet.write_string(3, 1, "UNTUK PERIODE s.d %s"%date, t_style)
            for col in range(1, 17):
                sheet.write_string(4, col, "", t3_style)
            sheet.write_string(4, 16, "JUMLAH", t3_style)
            sheet.write_string(4, 17, "PER KG", t3_style)

            # DETAIL
            c_cell_format = {'font_name': 'Calibri', 'font_size': 11, 'valign': 'top', 'align': 'left'}
            c_style = workbook.add_format(c_cell_format)
            c2_cell_format = c_cell_format.copy()
            c2_cell_format.update({'bold': True})
            c2_style = workbook.add_format(c2_cell_format)
            c3_cell_format = c_cell_format.copy()
            c3_cell_format.update({'bottom': 1, 'align': 'center'})
            c3_style = workbook.add_format(c3_cell_format)

            c_datetime_format = c_cell_format.copy()
            c_datetime_format.update({'align': 'center', 'num_format': 'd mmm yy'})
            c_datetime_style = workbook.add_format(c_datetime_format)
            
            num_cell_format = c_cell_format.copy()
            num_cell_format.update({'align': 'right', 'num_format':'#,##0;-#,##0;-'})
            num_style = workbook.add_format(num_cell_format)
            num2_cell_format = num_cell_format.copy()
            num2_cell_format.update({'bold': True})
            num2_style = workbook.add_format(num2_cell_format)
            num3_cell_format = num_cell_format.copy()
            num3_cell_format.update({'top': 1})
            num3_style = workbook.add_format(num3_cell_format)
            
            row = 5
            # ========= BAHAN BAKU
            consume_line = valuation.consume_product_lines
            sheet.write_string(row, 1, "PEMAKAIAN BAHAN BAKU", c2_style)
            sheet.write_number(row, 16, consume_line.consume_value, num3_style)
            sheet.write_number(row, 17, consume_line.average_cost_price, num3_style)
            row += 1
            sheet.write_string(row, 7, "Qty", c3_style)
            sheet.write_string(row, 8, "", c3_style)
            sheet.write_string(row, 9, "Rp/Kg", c3_style)
            sheet.write_string(row, 10, "Jumlah", c3_style)
            row += 1
            sheet.write_string(row, 2, "Saldo awal Kernel", c_style)
            sheet.write_number(row, 7, consume_line.opening_qty, num_style)
            sheet.write_number(row, 9, consume_line.opening_value/consume_line.opening_qty if consume_line.opening_qty else 0.0, num_style)
            sheet.write_number(row, 10, consume_line.opening_value, num_style)
            row += 1
            sheet.write_string(row, 2, "Pembelian Kernel", c_style)
            sheet.write_number(row, 7, consume_line.purchase_qty, num_style)
            sheet.write_number(row, 9, consume_line.purchase_value/consume_line.purchase_qty if consume_line.purchase_qty else 0.0, num_style)
            sheet.write_number(row, 10, consume_line.purchase_value, num_style)
            row += 1
            other_cost_accounts = consume_line.cost_account_move_ids.mapped('account_id').sorted(lambda x: x.code)
            for cacc in other_cost_accounts:
                lines = consume_line.cost_account_move_ids.filtered(lambda x: x.account_id.id==cacc.id)
                amount = sum(lines.mapped('debit')) - sum(lines.mapped('credit'))
                sheet.write_string(row, 2, cacc.name, c_style)
                sheet.write_string(row, 6, cacc.code, c_style)
                sheet.write_number(row, 7, 0.0, num_style)
                sheet.write_number(row, 9, 0.0, num_style)
                sheet.write_number(row, 10, amount, num_style)
                row += 1
            sheet.write_string(row, 2, "Total Pembelian Bahan Baku", c2_style)
            sheet.write_number(row, 7, consume_line.purchase_qty, num3_style)
            sheet.write_number(row, 9, 0.0, num3_style)
            sheet.write_number(row, 10, consume_line.purchase_value + consume_line.other_cost_value, num3_style)
            row += 1
            sheet.write_string(row, 2, "Bahan Baku Tersedia untuk Diproses", c_style)
            sheet.write_number(row, 7, consume_line.onhand_qty, num_style)
            sheet.write_number(row, 9, consume_line.average_cost_price, num_style)
            sheet.write_number(row, 10, consume_line.onhand_value, num_style)
            row += 1
            sheet.write_string(row, 2, "Persediaan Akhir Bahan Baku", c_style)
            sheet.write_number(row, 7, consume_line.closing_qty, num_style)
            sheet.write_number(row, 9, consume_line.average_cost_price, num_style)
            sheet.write_number(row, 10, consume_line.closing_value, num_style)
            row += 1
            sheet.write_string(row, 2, "Biaya Bahan Baku", c2_style)
            sheet.write_number(row, 7, consume_line.consume_qty, num3_style)
            sheet.write_number(row, 9, consume_line.average_cost_price, num3_style)
            sheet.write_number(row, 10, consume_line.consume_value, num3_style)
            row += 1
            row += 1

            # ========= BIAYA PRODUKSI
            produce_lines = valuation.produce_product_lines
            cost_move_line = produce_lines[-1].cost_account_move_ids
            cost_accounts = cost_move_line.mapped('account_id')
            cost_account_parents = cost_accounts.mapped('parent_id')
            for parent in cost_account_parents:
                total_camount = 0.0
                for cost_acc in cost_accounts.filtered(lambda x: x.parent_id.id==parent.id):
                    clines = cost_move_line.filtered(lambda y: y.account_id.id==cost_acc.id)
                    camount = sum(clines.mapped('debit')) - sum(clines.mapped('credit'))
                    total_camount += camount

                sheet.write_string(row, 1, parent.name, c2_style)
                sheet.write_number(row, 16, total_camount, num3_style)
                sheet.write_number(row, 17, 0.0, num3_style)
                row += 1
                for cost_acc in cost_accounts.filtered(lambda x: x.parent_id.id==parent.id):
                    clines = cost_move_line.filtered(lambda y: y.account_id.id==cost_acc.id)
                    camount = sum(clines.mapped('debit')) - sum(clines.mapped('credit'))
                    sheet.write_string(row, 2, cost_acc.name, c_style)
                    sheet.write_string(row, 6, cost_acc.code, c_style)
                    sheet.write_number(row, 10, camount, num_style)
                    row += 1
                    
                    temp_sum_per_station = {}
                    for mline in clines:
                        if mline.account_location_type_id and mline.account_location_id and mline.account_location_type_id.code=='ST':
                            station = self.env['mrp.workcenter'].search([('resource_id.code','=',mline.account_location_id.code)], limit=1)
                            if station:
                                code = station.sub_workcenter and station.parent_id.code or station.code or ''
                                name = station.sub_workcenter and station.parent_id.name or station.name or ''
                                if code not in temp_sum_per_station.keys():
                                    temp_sum_per_station.update({code: {'code': code, 'name': name, 'amount': 0.0}})
                                temp_sum_per_station[code]['amount'] += mline.debit-mline.credit
                            else:
                                # if 'OTH' not in temp_sum_per_station.keys():
                                #     temp_sum_per_station.update({'OTH': {'code': 'OTH', 'name': 'LAINNYA', 'amount': 0.0}})
                                # temp_sum_per_station['OTH']['amount'] += mline.debit-mline.credit
                                code = mline.account_location_type_id.code or ''
                                name = mline.account_location_type_id.name or ''
                                if code not in temp_sum_per_station.keys():
                                    temp_sum_per_station.update({code: {'code': code, 'name': name, 'amount': 0.0}})
                                temp_sum_per_station[code]['amount'] += mline.debit-mline.credit
                        else:
                            # if 'OTH' not in temp_sum_per_station.keys():
                            #     temp_sum_per_station.update({'OTH': {'code': 'OTH', 'name': 'LAINNYA', 'amount': 0.0}})
                            # temp_sum_per_station['OTH']['amount'] += mline.debit-mline.credit
                            code = mline.account_location_type_id.code if mline.account_location_type_id else '.'
                            name = mline.account_location_type_id.name if mline.account_location_type_id else '.'
                            if code not in temp_sum_per_station.keys():
                                temp_sum_per_station.update({code: {'code': code, 'name': name, 'amount': 0.0}})
                            temp_sum_per_station[code]['amount'] += mline.debit-mline.credit
                    if temp_sum_per_station:
                        for code, values in temp_sum_per_station.items():
                            sheet.write_string(row, 2, "     %s"%values.get('name','-'), c_style)
                            sheet.write_string(row, 6, code, c_style)
                            sheet.write_number(row, 10, values.get('amount',0.0), num_style)
                            row += 1

                sheet.write_number(row, 10, total_camount, num3_style)
                row += 1
            if cost_accounts.filtered(lambda y2: not y2.parent_id):
                total_camount = 0.0
                for cost_acc in cost_accounts.filtered(lambda y2: not y2.parent_id):
                    clines = cost_move_line.filtered(lambda y: y.account_id.id==cost_acc.id)
                    camount = sum(clines.mapped('debit')) - sum(clines.mapped('credit'))
                    total_camount += camount
                sheet.write_string(row, 1, "Biaya Lainnya", c2_style)
                sheet.write_number(row, 16, total_camount, num3_style)
                sheet.write_number(row, 17, 0.0, num3_style)
                row += 1
                for cost_acc in cost_accounts.filtered(lambda y2: not y2.parent_id):
                    clines = cost_move_line.filtered(lambda y: y.account_id.id==cost_acc.id)
                    camount = sum(clines.mapped('debit')) - sum(clines.mapped('credit'))
                    sheet.write_string(row, 2, cost_acc.name, c_style)
                    sheet.write_string(row, 6, cost_acc.code, c_style)
                    sheet.write_number(row, 10, camount, num_style)
                    row += 1

                    temp_sum_per_station = {}
                    for mline in clines:
                        if mline.account_location_type_id and mline.account_location_id and mline.account_location_type_id.code=='ST':
                            station = self.env['mrp.workcenter'].search([('resource_id.code','=',mline.account_location_id.code)], limit=1)
                            if station:
                                code = station.sub_workcenter and station.parent_id.code or station.code or ''
                                name = station.sub_workcenter and station.parent_id.name or station.name or ''
                                if code not in temp_sum_per_station.keys():
                                    temp_sum_per_station.update({code: {'code': code, 'name': name, 'amount': 0.0}})
                                temp_sum_per_station[code]['amount'] += mline.debit-mline.credit
                            else:
                                # if 'OTH' not in temp_sum_per_station.keys():
                                #     temp_sum_per_station.update({'OTH': {'code': 'OTH', 'name': 'LAINNYA', 'amount': 0.0}})
                                # temp_sum_per_station['OTH']['amount'] += mline.debit-mline.credit
                                code = mline.account_location_type_id.code or ''
                                name = mline.account_location_type_id.name or ''
                                if code not in temp_sum_per_station.keys():
                                    temp_sum_per_station.update({code: {'code': code, 'name': name, 'amount': 0.0}})
                                temp_sum_per_station[code]['amount'] += mline.debit-mline.credit
                        else:
                            # if 'OTH' not in temp_sum_per_station.keys():
                            #     temp_sum_per_station.update({'OTH': {'code': 'OTH', 'name': 'LAINNYA', 'amount': 0.0}})
                            # temp_sum_per_station['OTH']['amount'] += mline.debit-mline.credit
                            code = mline.account_location_type_id.code if mline.account_location_type_id else '.'
                            name = mline.account_location_type_id.name if mline.account_location_type_id else '.'
                            if code not in temp_sum_per_station.keys():
                                temp_sum_per_station.update({code: {'code': code, 'name': name, 'amount': 0.0}})
                            temp_sum_per_station[code]['amount'] += mline.debit-mline.credit
                    if temp_sum_per_station:
                        for code, values in temp_sum_per_station.items():
                            sheet.write_string(row, 2, "     %s"%values.get('name','-'), c_style)
                            sheet.write_string(row, 6, code, c_style)
                            sheet.write_number(row, 10, values.get('amount',0.0), num_style)
                            row += 1
                sheet.write_number(row, 10, total_camount, num3_style)
                row += 1

            # ========== HARGA POKOK PRODUKSI
            total_persediaan_awal = sum(produce_lines.mapped('opening_value')) + sum(produce_lines.mapped('purchase_value')) + sum(produce_lines.mapped('other_cost_value'))
            total_persediaan_akhir = sum(produce_lines.mapped('closing_value')) + sum(produce_lines.mapped('delivery_intransit_value'))
            total_cogm = sum(produce_lines.mapped('cogm_value'))
            sheet.write_string(row, 1, "HARGA POKOK PRODUKSI", c2_style)
            sheet.write_number(row, 16, total_cogm, num3_style)
            sheet.write_number(row, 17, 0.0, num3_style)
            row += 1
            sheet.write_string(row, 7, "Qty", c3_style)
            sheet.write_string(row, 8, "", c3_style)
            sheet.write_string(row, 9, "Rp/Kg", c3_style)
            sheet.write_string(row, 10, "Jumlah", c3_style)
            row += 1
            sheet.write_string(row, 2, "Persediaan Barang Jadi Awal", c_style)
            sheet.write_number(row, 16, total_persediaan_awal, num3_style)
            sheet.write_number(row, 17, 0.0, num3_style)
            row += 1
            for pline in produce_lines:
                sheet.write_string(row, 2, pline.product_id.code, c_style)
                sheet.write_number(row, 7, pline.opening_qty, num_style)
                sheet.write_number(row, 9, pline.opening_value/pline.opening_qty if pline.opening_qty else 0.0, num_style)
                sheet.write_number(row, 10, pline.opening_value, num_style)
                row += 1
                if pline.purchase_qty:
                    sheet.write_string(row, 2, "Pembelian %s"%pline.product_id.code, c_style)
                    sheet.write_number(row, 7, pline.purchase_qty, num_style)
                    sheet.write_number(row, 9, (pline.purchase_value + pline.other_cost_value)/pline.purchase_qty if pline.purchase_qty else 0.0, num_style)
                    sheet.write_number(row, 10, (pline.purchase_value + pline.other_cost_value), num_style)
                    row += 1
            sheet.write_string(row, 2, "Persediaan Barang Jadi Akhir", c_style)
            sheet.write_number(row, 16, total_persediaan_akhir, num3_style)
            sheet.write_number(row, 17, 0.0, num3_style)
            row += 1
            for pline in produce_lines:
                sheet.write_string(row, 2, pline.product_id.code, c_style)
                sheet.write_number(row, 7, (pline.closing_qty + pline.delivery_intransit_qty), num_style)
                sheet.write_number(row, 9, pline.average_cost_price, num_style)
                sheet.write_number(row, 10, (pline.closing_value + pline.delivery_intransit_value), num_style)
                row += 1

            # ========== HARGA POKOK PENJUALAN
            sheet.write_string(row, 1, "HARGA POKOK PENJUALAN", c2_style)
            # cogs_value = sum(produce_lines.mapped('cogs_value'))
            cogs_value = total_persediaan_awal + total_cogm - total_persediaan_akhir
            sheet.write_number(row, 16, cogs_value, num3_style)
            sheet.write_number(row, 17, 0.0, num3_style)
            row += 1


            sheet.set_margins(0.5, 0.5, 0.5, 0.5)
            sheet.print_area(0, 0, row, 18) #print area of selected cell
            sheet.set_paper(9)  # set A4 as page format
            sheet.center_horizontally()
            pages_horz = 1 # wide
            pages_vert = 0 # as long as necessary
            sheet.fit_to_pages(pages_horz, pages_vert)

            # SHEET MUTASI
            sheet_name = "Laporan Mutasi"
            sheet = workbook.add_worksheet(sheet_name[:31])
            sheet.set_portrait()
            sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})

            column_width = [10, 15, 15, 8, 15, 15, 15, 15, 15, 15]
            for col_pos in range(0,10):
                sheet.set_column(col_pos, col_pos, column_width[col_pos])

            sheet.write_string(0, 0, "PT SINAR JAYA INTI MULYA", t_style)
            row = 2
            sheet.write_string(row, 0, "LAPORAN MUTASI PERSEDIAAN KERNEL", t2_style)
            date_start = datetime.strptime(valuation.date_start, DF).strftime('%d %m %Y')
            date_stop = datetime.strptime(valuation.date_stop, DF).strftime('%d %m %Y')
            row += 1
            sheet.write_string(row, 0, "UNTUK PERIODE %s s.d %s"%(date_start, date_stop), t_style)
            row += 1

            sheet.write_string(row, 0, "Keterangan", c3_style)
            sheet.write_string(row, 1, "Saldo awal", c3_style)
            sheet.write_string(row, 2, "Pembelian", c3_style)
            sheet.write_string(row, 3, "", c3_style)
            sheet.write_string(row, 4, "Tersedian u/ proses", c3_style)
            sheet.write_string(row, 5, "Proses", c3_style)
            sheet.write_string(row, 6, "Susut", c3_style)
            sheet.write_string(row, 7, "Saldo Akhir", c3_style)
            row += 1

            for line in consume_line:
                sheet.write_string(row, 0, line.product_id.code, c2_style)
                row += 1

                sheet.write_string(row, 0, "Dalam KG", c_style)
                sheet.write_number(row, 1, line.opening_qty, num_style)
                sheet.write_number(row, 2, line.purchase_qty, num_style)
                sheet.write_string(row, 3, "", num_style)
                sheet.write_number(row, 4, line.onhand_qty, num_style)
                sheet.write_number(row, 5, line.consume_qty, num_style)
                sheet.write_number(row, 6, line.adjustment_qty, num_style)
                sheet.write_number(row, 7, line.closing_qty, num_style)
                row += 1

                sheet.write_string(row, 0, "Dalam RP", c_style)
                sheet.write_number(row, 1, line.opening_value, num_style)
                sheet.write_number(row, 2, line.purchase_value, num_style)
                sheet.write_string(row, 3, "", num_style)
                sheet.write_number(row, 4, line.onhand_value, num_style)
                sheet.write_number(row, 5, line.consume_value, num_style)
                sheet.write_number(row, 6, line.adjustment_qty*line.average_cost_price, num_style)
                sheet.write_number(row, 7, line.closing_value, num_style)
                row += 1

                sheet.write_string(row, 0, "Harga", c_style)
                sheet.write_number(row, 1, line.opening_value/line.opening_qty if line.opening_qty else 0.0, num_style)
                sheet.write_number(row, 2, line.purchase_value/line.purchase_qty if line.purchase_qty else 0.0, num_style)
                sheet.write_string(row, 3, "", num_style)
                sheet.write_number(row, 4, line.onhand_value/line.onhand_qty if line.onhand_qty else 0.0, num_style)
                sheet.write_number(row, 5, line.consume_value/line.consume_qty if line.consume_qty else 0.0, num_style)
                sheet.write_number(row, 6, line.average_cost_price, num_style)
                sheet.write_number(row, 7, line.closing_value/line.closing_qty if line.closing_qty else 0.0, num_style)
                row += 1

            row += 1
            sheet.write_string(row, 0, "LAPORAN MUTASI PERSEDIAAN BARANG JADI", t2_style)
            row += 1
            sheet.write_string(row, 0, "UNTUK PERIODE %s s.d %s"%(date_start, date_stop), t_style)
            row += 1

            sheet.write_string(row, 0, "Keterangan", c3_style)
            sheet.write_string(row, 1, "Saldo awal", c3_style)
            sheet.write_string(row, 2, "Produksi", c3_style)
            sheet.write_string(row, 3, "Rend", c3_style)
            sheet.write_string(row, 4, "Pembelian", c3_style)
            sheet.write_string(row, 5, "Tersedian u/ Dijual", c3_style)
            sheet.write_string(row, 6, "Penjualan", c3_style)
            sheet.write_string(row, 7, "Susut", c3_style)
            sheet.write_string(row, 8, "Delivery Intransit", c3_style)
            sheet.write_string(row, 9, "Saldo Akhir", c3_style)
            row += 1

            total_consume_qty = sum(consume_line.mapped('consume_qty'))
            for line in produce_lines:
                sheet.write_string(row, 0, line.product_id.code, c2_style)
                row += 1

                sheet.write_string(row, 0, "Dalam KG", c_style)
                sheet.write_number(row, 1, line.opening_qty, num_style)
                sheet.write_number(row, 2, line.produce_qty, num_style)
                sheet.write_number(row, 3, line.produce_qty/total_consume_qty * 100 if total_consume_qty else 0.0, num_style)
                sheet.write_number(row, 4, line.purchase_qty, num_style)
                sheet.write_number(row, 5, line.onhand_qty, num_style)
                sheet.write_number(row, 6, line.sale_qty, num_style)
                sheet.write_number(row, 7, line.adjustment_qty + (line.sale_qty - line.delivered_qty), num_style)
                sheet.write_number(row, 8, line.delivery_intransit_qty, num_style)
                sheet.write_number(row, 9, line.closing_qty, num_style)
                row += 1

                sheet.write_string(row, 0, "Dalam RP", c_style)
                sheet.write_number(row, 1, line.opening_value, num_style)
                sheet.write_number(row, 2, line.cogm_value, num_style)
                sheet.write_string(row, 3, "", num_style)
                sheet.write_number(row, 4, line.purchase_value + line.other_cost_value, num_style)
                sheet.write_number(row, 5, line.onhand_value, num_style)
                sheet.write_number(row, 6, line.sale_qty*line.average_cost_price, num_style)
                sheet.write_number(row, 7, (line.adjustment_qty + (line.sale_qty - line.delivered_qty))*line.average_cost_price, num_style)
                sheet.write_number(row, 8, line.delivery_intransit_value, num_style)
                sheet.write_number(row, 9, line.closing_value, num_style)
                row += 1

                sheet.write_string(row, 0, "Harga", c_style)
                sheet.write_number(row, 1, line.opening_value/line.opening_qty if line.opening_qty else 0.0, num_style)
                sheet.write_number(row, 2, line.cogm_value/line.produce_qty if line.produce_qty else 0.0, num_style)
                sheet.write_string(row, 3, "", num_style)
                sheet.write_number(row, 4, (line.purchase_value + line.other_cost_value)/line.purchase_qty if line.purchase_qty else 0.0, num_style)
                sheet.write_number(row, 5, line.onhand_value/line.onhand_qty if line.onhand_qty else 0.0, num_style)
                sheet.write_number(row, 6, line.average_cost_price, num_style)
                sheet.write_number(row, 7, line.average_cost_price, num_style)
                sheet.write_number(row, 8, line.delivery_intransit_value/line.delivery_intransit_qty if line.delivery_intransit_qty else 0.0, num_style)
                sheet.write_number(row, 9, line.closing_value/line.closing_qty if line.closing_qty else 0.0, num_style)
                row += 1


            sheet.set_margins(0.5, 0.5, 0.5, 0.5)
            sheet.print_area(0, 0, row, 18) #print area of selected cell
            sheet.set_paper(9)  # set A4 as page format
            sheet.center_horizontally()
            pages_horz = 1 # wide
            pages_vert = 0 # as long as necessary
            sheet.fit_to_pages(pages_horz, pages_vert)
        pass

ReportHPPXlsx('report.report_hpp_xlsx', 'mill.valuation')