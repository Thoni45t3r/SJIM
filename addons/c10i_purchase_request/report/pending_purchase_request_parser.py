# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report

class jasper_pending_purchase_request(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_pending_purchase_request, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        temp = list(data['form']['operating_unit_ids'])
        # if selected more than one document_type_ids or selected only one document_type_ids 
        str_operating_unit_id = str(tuple(data['form']['operating_unit_ids'])) if len(temp) > 1 else '('+str(temp[0])+')'
        params = {
                'company_name': data['form']['company_id'][1],
                'to_date' : str(data['form']['to_date']),
                'operating_unit_query': "pr.operating_unit_id in %s "%(str_operating_unit_id if data['form']['operating_unit_ids'] else '1=1') # [(5,[1,1,1,1,1,1,1,])]
                }
        return params

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data['form']['report_type']
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.report_pending_purchase_request', 'wizard.pending.purchase.request', parser=jasper_pending_purchase_request,)
jasper_report.ReportJasper('report.report_pending_purchase_request_xls', 'wizard.pending.purchase.request', parser=jasper_pending_purchase_request,)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
