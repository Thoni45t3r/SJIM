# -*- coding: utf-8 -*-
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report

class jasper_pending_po_request(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_pending_po_request, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        temp = list(data['form']['document_type_ids'])
        # if selected more than one document_type_ids or selected only one document_type_ids 
        str_doc_type_id = str(tuple(data['form']['document_type_ids'])) if len(temp) > 1 else '('+str(temp[0])+')'
        params = {
                'company_name': data['form']['company_id'][1],
                'to_date' : str(data['form']['to_date']),
                'document_type_query': "po.doc_type_id in %s "%(str_doc_type_id if data['form']['document_type_ids'] else '1=1') # [(5,[1,1,1,1,1,1,1,])]
                }
        # print('-------->params2', params)
        return params

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data['form']['report_type']
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.report_pending_po_sjm', 'wizard.pending.purchase.order', parser=jasper_pending_po_request,)
jasper_report.ReportJasper('report.report_pending_po_sjm_xls', 'wizard.pending.purchase.order', parser=jasper_pending_po_request,)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
