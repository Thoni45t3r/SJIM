from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from xlsxwriter import workbook
from datetime import datetime

class InvoiceOutstandingXlsx(ReportXlsx):

    def add_workbook_format(self, workbook):
        colors = {
            'white_orange': '#FFFFDB',
            'orange': '#FFC300',
            'red': '#FF0000',
            'yellow': '#F6FA03',
        }
        wbf = {}
        wbf['header'] = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#FFFFFF', 'font_color': '#000000', 'font_name': 'Georgia'})
        wbf['header'].set_border()
        wbf['header_orange'] = workbook.add_format({'bold': 1, 'align': 'center', 'bg_color': colors['orange'], 'font_color': '#000000', 'font_name': 'Georgia'})
        wbf['header_orange'].set_border()
        wbf['header_yellow'] = workbook.add_format({'bold': 1, 'align': 'center', 'bg_color': colors['yellow'], 'font_color': '#000000', 'font_name': 'Georgia'})
        wbf['header_yellow'].set_border()
        wbf['header_no'] = workbook.add_format({'bold': 1, 'align': 'center', 'bg_color': '#FFFFDB', 'font_color': '#000000', 'font_name': 'Georgia'})
        wbf['header_no'].set_border()
        wbf['header_no'].set_align('vcenter')
        wbf['footer'] = workbook.add_format({'align': 'left', 'font_name': 'Georgia'})
        wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss', 'font_name': 'Georgia'})
        wbf['content_datetime'].set_left()
        wbf['content_datetime'].set_right()
        wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd', 'font_name': 'Georgia'})
        wbf['content_date'].set_left()
        wbf['content_date'].set_right()
        wbf['title_doc'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 20,
            'font_name': 'Georgia',
        })
        wbf['title_doc2'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 16,
            'font_name': 'Georgia',
        })
        wbf['title_doc3'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
            'font_name': 'Georgia',
        })
        wbf['company'] = workbook.add_format({'align': 'left', 'font_name': 'Georgia'})
        wbf['company'].set_font_size(11)
        wbf['content'] = workbook.add_format()
        wbf['content'].set_left()
        wbf['content'].set_right()
        wbf['content_float'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00', 'font_name': 'Georgia'})
        wbf['content_float'].set_right()
        wbf['content_float'].set_left()
        wbf['content_number'] = workbook.add_format({'align': 'right', 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['content_number'].set_right()
        wbf['content_number'].set_left()
        wbf['content_percent'] = workbook.add_format({'align': 'right', 'num_format': '0.00%', 'font_name': 'Georgia'})
        wbf['content_percent'].set_right()
        wbf['content_percent'].set_left()
        wbf['total_float'] = workbook.add_format({'bold': 1, 'bg_color': '#FFFFFF', 'align': 'right', 'num_format': '#,##0.00', 'font_name': 'Georgia'})
        wbf['total_float'].set_top()
        wbf['total_float'].set_bottom()
        wbf['total_float'].set_left()
        wbf['total_float'].set_right()
        wbf['total_number'] = workbook.add_format({'align': 'right', 'bg_color': colors['white_orange'], 'bold': 1, 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['total_number'].set_top()
        wbf['total_number'].set_bottom()
        wbf['total_number'].set_left()
        wbf['total_number'].set_right()
        wbf['total'] = workbook.add_format({'bold': 1, 'bg_color': '#FFFFFF', 'align': 'left', 'font_name': 'Georgia'})
        wbf['total'].set_left()
        wbf['total'].set_right()
        wbf['total'].set_top()
        wbf['total'].set_bottom()
        wbf['total_float_yellow'] = workbook.add_format({'bold': 1, 'bg_color': colors['yellow'], 'align': 'right', 'num_format': '#,##0.00', 'font_name': 'Georgia'})
        wbf['total_float_yellow'].set_top()
        wbf['total_float_yellow'].set_bottom()
        wbf['total_float_yellow'].set_left()
        wbf['total_float_yellow'].set_right()
        wbf['total_number_yellow'] = workbook.add_format({'align': 'right', 'bg_color': colors['yellow'], 'bold': 1, 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['total_number_yellow'].set_top()
        wbf['total_number_yellow'].set_bottom()
        wbf['total_number_yellow'].set_left()
        wbf['total_number_yellow'].set_right()
        wbf['total_yellow'] = workbook.add_format({'bold': 1, 'bg_color': colors['yellow'], 'align': 'center', 'font_name': 'Georgia'})
        wbf['total_yellow'].set_left()
        wbf['total_yellow'].set_right()
        wbf['total_yellow'].set_top()
        wbf['total_yellow'].set_bottom()
        wbf['total_float_orange'] = workbook.add_format({'bold': 1, 'bg_color': colors['orange'], 'align': 'right', 'num_format': '#,##0.00', 'font_name': 'Georgia'})
        wbf['total_float_orange'].set_top()
        wbf['total_float_orange'].set_bottom()
        wbf['total_float_orange'].set_left()
        wbf['total_float_orange'].set_right()
        wbf['total_number_orange'] = workbook.add_format({'align': 'right', 'bg_color': colors['orange'], 'bold': 1, 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['total_number_orange'].set_top()
        wbf['total_number_orange'].set_bottom()
        wbf['total_number_orange'].set_left()
        wbf['total_number_orange'].set_right()
        wbf['total_orange'] = workbook.add_format({'bold': 1, 'bg_color': colors['orange'], 'align': 'center', 'font_name': 'Georgia'})
        wbf['total_orange'].set_left()
        wbf['total_orange'].set_right()
        wbf['total_orange'].set_top()
        wbf['total_orange'].set_bottom()
        wbf['header_detail_space'] = workbook.add_format({'font_name': 'Georgia'})
        wbf['header_detail_space'].set_left()
        wbf['header_detail_space'].set_right()
        wbf['header_detail_space'].set_top()
        wbf['header_detail_space'].set_bottom()
        wbf['header_detail'] = workbook.add_format({'bg_color': '#E0FFC2', 'font_name': 'Georgia'})
        wbf['header_detail'].set_left()
        wbf['header_detail'].set_right()
        wbf['header_detail'].set_top()
        wbf['header_detail'].set_bottom()
        return wbf, workbook

    def generate_xlsx_report(self, workbook, data, objects):
        company_name = self.env.user.company_id.name
        # date_string = self.get_default_date_model().strftime("%Y-%m-%d")
        # date_string = self.get_default_date_model()
        report_name = 'Outstanding Invoice Report'
        # filename = '%s %s' % (report_name, date_string)
        filename = report_name
        columns = [
            (5,'no'),
            (30, 'char'),
            (30, 'char'),
            (8, 'date'),
            (30, 'char'),
            (20, 'float'),
            (7, 'char'),
            (20, 'float'),
            (20, 'char'),
            (20, 'float'),
            (20, 'float'),
            (20, 'float'),
            (20, 'float'),
        ]

        query = """
            SELECT rp.name
            , ai.number AS invoice_number
            , ai.date AS invoice_date
            , '['||pt.default_code||']'||pt.name AS product_name
            , ail.quantity AS product_qty
            , uu.name AS uom_name
            , ail.price_unit
            , rc.name AS currency_name
            , ai.amount_untaxed
            , ai.amount_tax
            , ai.amount_total
            , ai.amount_total + (
                (SELECT COALESCE(SUM(CASE WHEN apr.amount_currency <> 0 THEN apr.amount_currency
                            WHEN apr.amount <> 0 THEN apr.amount
                            ELSE 0
                            END),0)
                FROM account_move_line aml
                INNER JOIN account_partial_reconcile apr ON apr.debit_move_id = aml.id
                INNER JOIN account_move_line aml2 ON aml2.id = apr.credit_move_id
                where aml.invoice_id = ai.id and aml.account_id=ai.account_id and aml2.date <= '%s') -
                (SELECT COALESCE(SUM(CASE WHEN apr.amount_currency <> 0 THEN apr.amount_currency
                            WHEN apr.amount <> 0 THEN apr.amount
                            ELSE 0
                            END),0)
                FROM account_move_line aml
                INNER JOIN account_partial_reconcile apr ON apr.credit_move_id = aml.id
                INNER JOIN account_move_line aml2 ON aml2.id = apr.debit_move_id
                where aml.invoice_id = ai.id and aml.account_id=ai.account_id and aml2.date <= '%s')) AS residual_amount
            FROM account_invoice_line ail
            INNER JOIN account_invoice ai ON ai.id = ail.invoice_id
            INNER JOIN res_partner rp ON rp.id = ai.partner_id
            INNER JOIN res_currency rc ON rc.id = ai.currency_id
            LEFT OUTER JOIN product_product pp ON pp.id = ail.product_id
            LEFT OUTER JOIN product_uom uu ON uu.id = ail.uom_id
            LEFT OUTER JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE ai.state IN ('open','paid')
            AND ai.type = '%s'
            AND product_id = %s
            AND ai.date_invoice <= '%s'
            ORDER BY rp.name ASC, ai.date ASC
        """
        self.env.cr.execute(query % (objects.date_to, objects.date_to, objects.invoice_type, objects.product_id.id, objects.date_to))
        result = self.env.cr.fetchall()
        wbf, workbook = self.add_workbook_format(workbook)
        worksheet = workbook.add_worksheet(report_name)
        worksheet.merge_range('A1:M1', company_name, wbf['title_doc'])
        worksheet.merge_range('A2:M2', "Product : " + objects.product_id.name, wbf['title_doc2'])
        worksheet.merge_range('A3:M3', "As of Date : " + objects.date_to, wbf['title_doc3'])
        worksheet.merge_range('A5:A6', "No", wbf['header'])
        worksheet.merge_range('B5:B6', "Customer", wbf['header'])
        worksheet.merge_range('C5:D5', "Invoice", wbf['header'])
        worksheet.write(5, 2, "Number", wbf['header'])
        worksheet.write(5, 3, "Date", wbf['header'])
        worksheet.merge_range('E5:E6', "Product", wbf['header'])
        worksheet.merge_range('F5:F6', "Quantity", wbf['header'])
        worksheet.merge_range('G5:G6', "UoM", wbf['header'])
        worksheet.merge_range('H5:H6', "Unit Price", wbf['header'])
        worksheet.merge_range('I5:I6', "Currency", wbf['header'])
        worksheet.merge_range('J5:J6', "Amount", wbf['header'])
        worksheet.merge_range('K5:K6', "Tax", wbf['header'])
        worksheet.merge_range('L5:L6', "Total Amount", wbf['header'])
        worksheet.merge_range('M5:M6', "Unpaid Amount", wbf['header'])
        col = 0
        for column in columns :
            column_width = column[0]
            worksheet.set_column(col,col,column_width)
            col += 1
        row = 7
        number = 1
        partner_name_previous = False
        total_amount_partner = 0
        total_outstanding_partner = 0
        for res in result:
            if not res[11]:
                continue
            col = 0
            if not partner_name_previous:
                partner_name_previous = res[0]
            elif partner_name_previous and partner_name_previous != res[0]:
                worksheet.merge_range(row-1, 0, row-1, 10, "Subtotal " + (partner_name_previous or ''), wbf['total'])
                worksheet.write(row - 1, 11, total_amount_partner, wbf['total_float'])
                worksheet.write(row - 1, 12, total_outstanding_partner, wbf['total_float'])
                partner_name_previous = res[0]
                row += 1
                total_amount_partner = 0
            for column in columns:
                column_type = column[1]
                if column_type == 'char':
                    col_value = res[col - 1] if res[col - 1] else ''
                    wbf_value = wbf['content']
                elif column_type == 'no':
                    col_value = number
                    wbf_value = wbf['content']
                elif column_type == 'date':
                    col_value = res[col - 1] if res[col - 1] else ''
                    wbf_value = wbf['content_date']
                else:
                    col_value = res[col - 1] if res[col - 1] else 0
                    if column_type == 'float':
                        wbf_value = wbf['content_float']
                    else:  # number
                        wbf_value = wbf['content_number']
                worksheet.write(row - 1, col, col_value, wbf_value)
                col += 1
            total_amount_partner += res[10]
            total_outstanding_partner += res[11]
            row += 1
            number += 1
        ##Last Subtotal
        worksheet.merge_range(row - 1, 0, row - 1, 10, "Subtotal " + (partner_name_previous or ''), wbf['total'])
        worksheet.write(row - 1, 11, total_amount_partner, wbf['total_float'])
        worksheet.write(row - 1, 12, total_outstanding_partner, wbf['total_float'])
        pass

InvoiceOutstandingXlsx('report.sjim_account_invoice_outstanding',
            'wizard.report.outstanding.invoice')