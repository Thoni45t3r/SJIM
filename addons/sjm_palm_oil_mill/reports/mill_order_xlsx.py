from odoo import api, fields, models

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.addons.c10i_amount_in_words.amount_in_words import amount_in_words as convert
from xlsxwriter.utility import xl_rowcol_to_cell
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT

class ReportLHPXlsx(ReportXlsx):
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

        days = {6: 'Minggu', 0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu'}
        for mill in objects:
            date = datetime.strptime(mill.date, DF)
            date_start = (date + relativedelta(day=1)).strftime(DF)

            temp_products = {'pk': mill.product_id.id}
            for x in mill.editable_produce_line_ids.mapped('product_id'):
                  if x.default_code=='CPKO':
                        temp_products.update({'cpko': x.id})
                  elif x.default_code=='PKE':
                        temp_products.update({'pke': x.id})
            
            prev_mills = self.env['mrp.unbuild'].search([('bom_id','=',mill.bom_id.id),('product_id','=',mill.product_id.id),
                ('date','>=',date_start),('date','<',mill.date),('state','=','done')])
            
            sheet_name = "LHP %s"%date.strftime('%d %m %Y')
            sheet = workbook.add_worksheet(sheet_name[:31])
            sheet.set_portrait()
            sheet.set_footer('&R&6&"Courier New,Italic"Page &P of &N', {'margin': 0.25})

            column_width = [1, 5, 18,  8, 10, 10, 15, 15, 8, 15, 8, 15, 15, 15, 8]
            for col_pos in range(0,15):
                sheet.set_column(col_pos, col_pos, column_width[col_pos])
            
            # TITLE
            t_cell_format = {'font_name': 'Arial', 'font_size': 10, 'valign': 'vcenter', 'align': 'left'}
            t_style = workbook.add_format(t_cell_format)
            t2_cell_format = {'font_name': 'Arial', 'font_size': 10, 'bold': True, 'valign': 'vcenter', 'align': 'left'}
            t2_style = workbook.add_format(t2_cell_format)
            t3_cell_format = {'font_name': 'Arial', 'font_size': 10, 'bold': True, 'valign': 'vcenter', 'align': 'center'}
            t3_style = workbook.add_format(t3_cell_format)
            sheet.merge_range(0, 1, 0, 13, "PT SINAR JAYA INTI MULYA", t3_style)
            sheet.merge_range(1, 1, 1, 13, "LAPORAN HARIAN PRODUKSI & PENGIRIMAN PRODUCT (PKO BUNGKIL)", t3_style)

            # DETAIL
            c_cell_format = {'font_name': 'Arial', 'font_size': 11, 'valign': 'top', 'align': 'left'}
            c_style = workbook.add_format(c_cell_format)
            c2_cell_format = c_cell_format.copy()
            c2_cell_format.update({'border': 1})
            c2_style = workbook.add_format(c2_cell_format)
            c3_cell_format = c_cell_format.copy()
            c3_cell_format.update({'border': 1, 'align': 'center'})
            c3_style = workbook.add_format(c3_cell_format)

            c_datetime_format = c_cell_format.copy()
            c_datetime_format.update({'align': 'center', 'num_format': 'd mmm yy'})
            c_datetime_style = workbook.add_format(c_datetime_format)
            
            num_cell_format = c_cell_format.copy()
            num_cell_format.update({'align': 'right', 'num_format':'#,##0;-#,##0;-'})
            num_style = workbook.add_format(num_cell_format)
            num2_cell_format = num_cell_format.copy()
            num2_cell_format.update({'border': 1})
            num2_style = workbook.add_format(num2_cell_format)
            num3_cell_format = num_cell_format.copy()
            num3_cell_format.update({'border': 1, 'num_format': '0.00%'})
            num3_style = workbook.add_format(num3_cell_format)
            
            sheet.write_string(2, 1, 'Bulan', c_style)
            sheet.write_string(2, 4, date.strftime('%b %Y'), c_style)
            sheet.write_string(3, 1, 'Tanggal', c_style)
            sheet.write_number(3, 4, date.day, c_style)
            sheet.write_string(4, 1, 'Hari', c_style)
            sheet.write_string(4, 4, days.get(date.weekday(), 'Unknown'), c_style)
            
            sheet.write_string(2, 12, 'Start Proses', c_style)
            sheet.write_string(3, 12, 'Stop Proses', c_style)

            sheet.merge_range(5, 1, 6, 1, 'NO.', c3_style)
            sheet.merge_range(5, 2, 6, 4, 'URAIAN', c3_style)
            sheet.merge_range(5, 5, 6, 5, 'SAT', c3_style)
            sheet.merge_range(5, 6, 6, 6, 'KERNEL', c3_style)
            sheet.merge_range(5, 7, 5, 10, 'HI', c3_style)
            sheet.write_string(6, 7, 'CPKO', c3_style)
            sheet.write_string(6, 8, '%', c3_style)
            sheet.write_string(6, 9, 'BUNGKIL', c3_style)
            sheet.write_string(6, 10, '%', c3_style)
            sheet.merge_range(5, 11, 5, 13, 'AKUMULASI S/D HI', c3_style)
            sheet.write_string(6, 11, 'KERNEL', c3_style)
            sheet.write_string(6, 12, 'CPKO', c3_style)
            sheet.write_string(6, 13, 'BUNGKIL', c3_style)

            # Variable
            saldo_awal_pk = saldo_awal_cpko = saldo_awal_pke = 0.0
            for code, product_id in temp_products.items():
                  resq = {}
                  query_opening = """SELECT  
                          product_id, sum(product_qty) as qty
                      FROM
                          (
                          (select product_id, product_qty from stock_move 
                          where product_id=%(product_id)s and location_id<>%(location_id)s and location_dest_id=%(location_id)s
                              and (date + INTERVAL '7 hours')::TIMESTAMP<'%(date)s' and state='done')
                          UNION ALL
                          (select product_id, -1*product_qty from stock_move 
                          where product_id=%(product_id)s and location_id=%(location_id)s and location_dest_id<>%(location_id)s
                              and (date + INTERVAL '7 hours')::TIMESTAMP<'%(date)s' and state='done')
                          ) dummy
                      GROUP BY product_id"""
                  query_opening = query_opening%{'product_id': product_id, 'location_id': mill.location_id.id, 'date': date_start + ' 00:00:00'}
                  self.env.cr.execute(query_opening)
                  resq = self.env.cr.dictfetchone()
                  if resq:
                        if code=='pk':
                              saldo_awal_pk = resq.get('qty',0.0)
                        elif code=='cpko':
                              saldo_awal_cpko = resq.get('qty',0.0)
                        elif code=='pke':
                              saldo_awal_pke = resq.get('qty',0.0)

            penerimaan_pk = penerimaan_cpko = penerimaan_pke = 0.0
            cumm_penerimaan_pk = cumm_penerimaan_cpko = cumm_penerimaan_pke = 0.0
            for code, product_id in temp_products.items():
                  resq1 = {}
                  query_incoming = """SELECT  
                          product_id, sum(product_qty) as qty
                      FROM
                        (select product_id, product_qty from stock_move 
                        where product_id=%(product_id)s and location_id<>%(location_id)s and location_dest_id=%(location_id)s
                              and location_id in (select id from stock_location where usage='supplier')
                              and (date + INTERVAL '7 hours')::TIMESTAMP between '%(date_start)s' and '%(date_stop)s' and state='done'
                        ) dummy
                      GROUP BY product_id"""
                  query_incoming = query_incoming%{'product_id': product_id, 'location_id': mill.location_id.id, 'date_start': date_start + ' 00:00:00', 'date_stop': mill.date + ' 00:00:00'}
                  self.env.cr.execute(query_incoming)
                  resq1 = self.env.cr.dictfetchone()
                  if resq1:
                        if code=='pk':
                              cumm_penerimaan_pk = resq1.get('qty',0.0)
                        elif code=='cpko':
                              cumm_penerimaan_cpko = resq1.get('qty',0.0)
                        elif code=='pke':
                              cumm_penerimaan_pke = resq1.get('qty',0.0)
            for code, product_id in temp_products.items():
                  resq2 = {}
                  query_incoming2 = """SELECT  
                          product_id, sum(product_qty) as qty
                      FROM
                        (select product_id, product_qty from stock_move 
                        where product_id=%(product_id)s and location_id<>%(location_id)s and location_dest_id=%(location_id)s
                              and location_id in (select id from stock_location where usage='supplier')
                              and (date + INTERVAL '7 hours')::TIMESTAMP between '%(date_start)s' and '%(date_stop)s' and state='done'
                        ) dummy
                      GROUP BY product_id"""
                  query_incoming2 = query_incoming2%{'product_id': product_id, 'location_id': mill.location_id.id, 'date_start': mill.date + ' 00:00:00', 'date_stop': mill.date + ' 23:59:59'}
                  self.env.cr.execute(query_incoming2)
                  resq2 = self.env.cr.dictfetchone()
                  if resq2:
                        if code=='pk':
                              penerimaan_pk = resq2.get('qty',0.0)
                              cumm_penerimaan_pk += resq2.get('qty',0.0)
                        elif code=='cpko':
                              penerimaan_cpko = resq2.get('qty',0.0)
                              cumm_penerimaan_cpko += resq2.get('qty',0.0)
                        elif code=='pke':
                              penerimaan_pke = resq2.get('qty',0.0)
                              cumm_penerimaan_pke += resq2.get('qty',0.0)

            pengiriman_cpko = pengiriman_pke = 0.0
            cumm_pengiriman_cpko = cumm_pengiriman_pke = 0.0
            for code, product_id in temp_products.items():
                  resq3 = {}
                  query_outgoing = """SELECT  
                          product_id, sum(product_qty) as qty
                      FROM
                        (select product_id, product_qty from stock_move 
                        where product_id=%(product_id)s and location_id=%(location_id)s and location_dest_id<>%(location_id)s
                              and location_dest_id in (select id from stock_location where usage='customer')
                              and (date + INTERVAL '7 hours')::TIMESTAMP between '%(date_start)s' and '%(date_stop)s' and state='done'
                        ) dummy
                      GROUP BY product_id"""
                  query_outgoing = query_outgoing%{'product_id': product_id, 'location_id': mill.location_id.id, 'date_start': date_start + ' 00:00:00', 'date_stop': mill.date + ' 00:00:00'}
                  self.env.cr.execute(query_outgoing)
                  resq3 = self.env.cr.dictfetchone()
                  if resq3:
                        if code=='pk':
                              continue
                        elif code=='cpko':
                              cumm_pengiriman_cpko = resq3.get('qty',0.0)
                        elif code=='pke':
                              cumm_pengiriman_pke = resq3.get('qty',0.0)
            for code, product_id in temp_products.items():
                  resq4 = {}
                  query_outgoing2 = """SELECT  
                          product_id, sum(product_qty) as qty
                      FROM
                        (select product_id, product_qty from stock_move 
                        where product_id=%(product_id)s and location_id=%(location_id)s and location_dest_id<>%(location_id)s
                              and location_id in (select id from stock_location where usage='customer')
                              and (date + INTERVAL '7 hours')::TIMESTAMP between '%(date_start)s' and '%(date_stop)s' and state='done'
                        ) dummy
                      GROUP BY product_id"""
                  query_outgoing2 = query_outgoing2%{'product_id': product_id, 'location_id': mill.location_id.id, 'date_start': mill.date + ' 00:00:00', 'date_stop': mill.date + ' 23:59:59'}
                  self.env.cr.execute(query_outgoing2)
                  resq4 = self.env.cr.dictfetchone()
                  if resq4:
                        if code=='pk':
                              continue
                        elif code=='cpko':
                              pengiriman_cpko = resq4.get('qty',0.0)
                              cumm_pengiriman_cpko += resq4.get('qty',0.0)
                        elif code=='pke':
                              pengiriman_pke = resq4.get('qty',0.0)
                              cumm_pengiriman_pke += resq4.get('qty',0.0)

            olah_pk = produksi_cpko = produksi_pke = 0.0
            cumm_olah_pk = cumm_produksi_cpko = cumm_produksi_pke = 0.0
            olah_pk = mill.product_qty
            if prev_mills:
                cumm_olah_pk = olah_pk + sum(prev_mills.mapped('product_qty'))

            cpko_produce_line = mill.editable_produce_line_ids.filtered(lambda x: x.product_id.default_code=='CPKO')
            produksi_cpko = cpko_produce_line.product_uom_qty if cpko_produce_line else 0.0
            pke_produce_line = mill.editable_produce_line_ids.filtered(lambda x: x.product_id.default_code=='PKE')
            produksi_pke = pke_produce_line.product_uom_qty if cpko_produce_line else 0.0
            if prev_mills:
                for pmo in prev_mills:
                    p_cpko_produce_lines = pmo.editable_produce_line_ids.filtered(lambda x: x.product_id.default_code=='CPKO')
                    p_pke_produce_lines = pmo.editable_produce_line_ids.filtered(lambda x: x.product_id.default_code=='PKE')
                    cumm_produksi_cpko += (p_cpko_produce_lines.product_uom_qty if p_cpko_produce_lines else 0.0)
                    cumm_produksi_pke += (p_pke_produce_lines.product_uom_qty if p_pke_produce_lines else 0.0)
            cumm_produksi_cpko += produksi_cpko
            cumm_produksi_pke += produksi_pke

            sheet.write_number(7, 1, 1, c3_style)
            sheet.merge_range(7, 2, 7, 3, "Saldo Awal", c2_style)
            sheet.write_string(7, 4, "", c2_style)
            sheet.write_string(7, 5, "Kg", c2_style)
            sheet.write_number(7, 6, saldo_awal_pk + ((cumm_penerimaan_pk - penerimaan_pk) - (cumm_olah_pk - olah_pk)), num2_style) # diisi
            sheet.write_number(7, 7, saldo_awal_cpko + ((cumm_penerimaan_cpko - penerimaan_cpko) + (cumm_produksi_cpko - produksi_cpko) - (cumm_pengiriman_cpko - pengiriman_cpko)), num2_style) # diisi
            sheet.write_number(7, 8, 0.0, num2_style)
            sheet.write_number(7, 9, saldo_awal_pke + ((cumm_penerimaan_pke - penerimaan_pke) + (cumm_produksi_pke - produksi_pke) - (cumm_pengiriman_pke - pengiriman_pke)), num2_style) # diisi
            sheet.write_number(7, 10, 0.0, num2_style)
            sheet.write_number(7, 11, saldo_awal_pk, num2_style) # diisi
            sheet.write_number(7, 12, saldo_awal_cpko, num2_style) # diisi
            sheet.write_number(7, 13, saldo_awal_pke, num2_style) # diisi

            sheet.merge_range(8, 1, 10, 1, 2, c3_style)
            sheet.merge_range(8, 2, 10, 3, "Penerimaan PK", c2_style)
            sheet.write_string(8, 4, "Bruto", c2_style)
            sheet.write_string(8, 5, "Kg", c2_style)
            sheet.write_number(8, 6, 0.0, num2_style)
            sheet.write_number(8, 7, 0.0, num2_style)
            sheet.write_number(8, 8, 0.0, num2_style)
            sheet.write_number(8, 9, 0.0, num2_style)
            sheet.write_number(8, 10, 0.0, num2_style)
            sheet.write_number(8, 11, 0.0, num2_style)
            sheet.write_number(8, 12, 0.0, num2_style)
            sheet.write_number(8, 13, 0.0, num2_style)
            sheet.write_string(9, 4, "Sortasi", c2_style)
            sheet.write_string(9, 5, "Kg", c2_style)
            sheet.write_number(9, 6, 0.0, num2_style)
            sheet.write_number(9, 7, 0.0, num2_style)
            sheet.write_number(9, 8, 0.0, num2_style)
            sheet.write_number(9, 9, 0.0, num2_style)
            sheet.write_number(9, 10, 0.0, num2_style)
            sheet.write_number(9, 11, 0.0, num2_style)
            sheet.write_number(9, 12, 0.0, num2_style)
            sheet.write_number(9, 13, 0.0, num2_style)
            sheet.write_string(10, 4, "Netto", c2_style)
            sheet.write_string(10, 5, "Kg", c2_style)
            sheet.write_number(10, 6, penerimaan_pk, num2_style)
            sheet.write_number(10, 7, 0.0, num2_style)
            sheet.write_number(10, 8, 0.0, num2_style)
            sheet.write_number(10, 9, 0.0, num2_style)
            sheet.write_number(10, 10, 0.0, num2_style)
            sheet.write_number(10, 11, cumm_penerimaan_pk, num2_style)
            sheet.write_number(10, 12, 0.0, num2_style)
            sheet.write_number(10, 13, 0.0, num2_style)
            
            sheet.merge_range(11, 1, 12, 1, 3, c3_style)
            sheet.merge_range(11, 2, 12, 3, "Kernel diolah", c2_style)
            sheet.write_string(11, 4, "Bruto", c2_style)
            sheet.write_string(11, 5, "Kg", c2_style)
            sheet.write_number(11, 6, 0.0, num2_style)
            sheet.write_number(11, 7, 0.0, num2_style)
            sheet.write_number(11, 8, 0.0, num2_style)
            sheet.write_number(11, 9, 0.0, num2_style)
            sheet.write_number(11, 10, 0.0, num2_style)
            sheet.write_number(11, 11, 0.0, num2_style)
            sheet.write_number(11, 12, 0.0, num2_style)
            sheet.write_number(11, 13, 0.0, num2_style)
            sheet.write_string(12, 4, "Netto", c2_style)
            sheet.write_string(12, 5, "Kg", c2_style)
            sheet.write_number(12, 6, olah_pk, num2_style) # diisi
            sheet.write_number(12, 7, 0.0, num2_style)
            sheet.write_number(12, 8, 0.0, num2_style)
            sheet.write_number(12, 9, 0.0, num2_style)
            sheet.write_number(12, 10, 0.0, num2_style)
            sheet.write_number(12, 11, cumm_olah_pk, num2_style) # diisi
            sheet.write_number(12, 12, 0.0, num2_style)
            sheet.write_number(12, 13, 0.0, num2_style)

            sheet.write_number(13, 1, 4, c3_style)
            sheet.merge_range(13, 2, 13, 3, "Jumlah Jam Olah", c2_style)
            sheet.write_string(13, 4, "", c2_style)
            sheet.write_string(13, 5, "Jam", c2_style)
            sheet.write_number(13, 6, 0.0, num2_style)
            sheet.write_number(13, 7, 0.0, num2_style)
            sheet.write_number(13, 8, 0.0, num2_style)
            sheet.write_number(13, 9, 0.0, num2_style)
            sheet.write_number(13, 10, 0.0, num2_style)
            sheet.write_number(13, 11, 0.0, num2_style)
            sheet.write_number(13, 12, 0.0, num2_style)
            sheet.write_number(13, 13, 0.0, num2_style)

            sheet.write_number(14, 1, 5, c3_style)
            sheet.merge_range(14, 2, 14, 3, "Jumlah Jam Stagnasi", c2_style)
            sheet.write_string(14, 4, "", c2_style)
            sheet.write_string(14, 5, "Jam", c2_style)
            sheet.write_number(14, 6, 0.0, num2_style)
            sheet.write_number(14, 7, 0.0, num2_style)
            sheet.write_number(14, 8, 0.0, num2_style)
            sheet.write_number(14, 9, 0.0, num2_style)
            sheet.write_number(14, 10, 0.0, num2_style)
            sheet.write_number(14, 11, 0.0, num2_style)
            sheet.write_number(14, 12, 0.0, num2_style)
            sheet.write_number(14, 13, 0.0, num2_style)

            sheet.write_number(15, 1, 6, c3_style)
            sheet.merge_range(15, 2, 15, 3, "Kapasitas Produksi", c2_style)
            sheet.write_string(15, 4, "", c2_style)
            sheet.write_string(15, 5, "Ton/Jam", c2_style)
            sheet.write_number(15, 6, 0.0, num2_style)
            sheet.write_number(15, 7, 0.0, num2_style)
            sheet.write_number(15, 8, 0.0, num2_style)
            sheet.write_number(15, 9, 0.0, num2_style)
            sheet.write_number(15, 10, 0.0, num2_style)
            sheet.write_number(15, 11, 0.0, num2_style)
            sheet.write_number(15, 12, 0.0, num2_style)
            sheet.write_number(15, 13, 0.0, num2_style)

            sheet.write_number(16, 1, 7, c3_style)
            sheet.merge_range(16, 2, 16, 3, "Hasil Produksi", c2_style)
            sheet.write_string(16, 4, "", c2_style)
            sheet.write_string(16, 5, "Kg", c2_style)
            sheet.write_number(16, 6, 0.0, num2_style)
            sheet.write_number(16, 7, produksi_cpko, num2_style) # diisi
            sheet.write_number(16, 8, produksi_cpko/olah_pk if olah_pk else 0.0, num3_style) # diisi
            sheet.write_number(16, 9, produksi_pke, num2_style) # diisi
            sheet.write_number(16, 10, produksi_pke/olah_pk if olah_pk else 0.0, num3_style) # diisi
            sheet.write_number(16, 11, 0.0, num2_style) # diisi
            sheet.write_number(16, 12, cumm_produksi_cpko, num2_style) # diisi
            sheet.write_number(16, 13, cumm_produksi_pke, num2_style) # diisi

            sheet.write_number(17, 1, 8, c3_style)
            sheet.merge_range(17, 2, 17, 3, "Stock Dalam Proses", c2_style)
            sheet.write_string(17, 4, "", c2_style)
            sheet.write_string(17, 5, "Kg", c2_style)
            sheet.write_number(17, 6, 0.0, num2_style)
            sheet.write_number(17, 7, 0.0, num2_style)
            sheet.write_number(17, 8, 0.0, num2_style)
            sheet.write_number(17, 9, 0.0, num2_style)
            sheet.write_number(17, 10, 0.0, num2_style)
            sheet.write_number(17, 11, 0.0, num2_style)
            sheet.write_number(17, 12, 0.0, num2_style)
            sheet.write_number(17, 13, 0.0, num2_style)

            sheet.write_number(18, 1, 9, c3_style)
            sheet.merge_range(18, 2, 18, 3, "Retur Penjualan", c2_style)
            sheet.write_string(18, 4, "", c2_style)
            sheet.write_string(18, 5, "Kg", c2_style)
            sheet.write_number(18, 6, 0.0, num2_style)
            sheet.write_number(18, 7, 0.0, num2_style)
            sheet.write_number(18, 8, 0.0, num2_style)
            sheet.write_number(18, 9, 0.0, num2_style)
            sheet.write_number(18, 10, 0.0, num2_style)
            sheet.write_number(18, 11, 0.0, num2_style)
            sheet.write_number(18, 12, 0.0, num2_style)
            sheet.write_number(18, 13, 0.0, num2_style)

            sheet.write_number(19, 1, 10, c3_style)
            sheet.merge_range(19, 2, 19, 3, "Pengiriman Barang", c2_style)
            sheet.write_string(19, 4, "", c2_style)
            sheet.write_string(19, 5, "Kg", c2_style)
            sheet.write_number(19, 6, 0.0, num2_style)
            sheet.write_number(19, 7, 0.0, num2_style) # diisi
            sheet.write_number(19, 8, pengiriman_cpko, num2_style)
            sheet.write_number(19, 9, 0.0, num2_style) # diisi
            sheet.write_number(19, 10, pengiriman_pke, num2_style)
            sheet.write_number(19, 11, 0.0, num2_style)
            sheet.write_number(19, 12, cumm_pengiriman_cpko, num2_style) # diisi
            sheet.write_number(19, 13, cumm_pengiriman_pke, num2_style) # diisi

            sheet.write_number(20, 1, 11, c3_style)
            sheet.merge_range(20, 2, 20, 3, "Pemasukan Barang", c2_style)
            sheet.write_string(20, 4, "", c2_style)
            sheet.write_string(20, 5, "Kg", c2_style)
            sheet.write_number(20, 6, 0.0, num2_style)
            sheet.write_number(20, 7, penerimaan_cpko, num2_style)
            sheet.write_number(20, 8, 0.0, num2_style)
            sheet.write_number(20, 9, penerimaan_pke, num2_style)
            sheet.write_number(20, 10, 0.0, num2_style)
            sheet.write_number(20, 11, 0.0, num2_style)
            sheet.write_number(20, 12, cumm_penerimaan_cpko, num2_style)
            sheet.write_number(20, 13, cumm_penerimaan_pke, num2_style)

            sheet.write_number(21, 1, 12, c3_style)
            sheet.merge_range(21, 2, 21, 3, "Stock Akhir", c2_style)
            sheet.write_string(21, 4, "", c2_style)
            sheet.write_string(21, 5, "Kg", c2_style)
            sheet.write_formula(21, 6, "=G8+G11-G13", num2_style) # diisi
            sheet.write_formula(21, 7, "=H8+H17+H21-H20", num2_style) # diisi
            sheet.write_number(21, 8, 0.0, num2_style)
            sheet.write_formula(21, 9, "=J8+J17+J21-J20", num2_style) # diisi
            sheet.write_number(21, 10, 0.0, num2_style)
            sheet.write_formula(21, 11, "=L8+L11-L13", num2_style) # diisi
            sheet.write_formula(21, 12, "=M8+M17+M21-M20", num2_style) # diisi
            sheet.write_formula(21, 13, "=N8+N17+N21-N20", num2_style) # diisi

            sheet.set_margins(0.5, 0.5, 0.5, 0.5)
            sheet.print_area(0, 0, 40, 14) #print area of selected cell
            sheet.set_paper(9)  # set A4 as page format
            sheet.center_horizontally()
            pages_horz = 1 # wide
            pages_vert = 0 # as long as necessary
            sheet.fit_to_pages(pages_horz, pages_vert)
        pass

ReportLHPXlsx('report.report_lhp_xlsx', 'mrp.unbuild')