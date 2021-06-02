# -*- coding: utf-8 -*-
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report

class jasper_rekap_purchase_requisition(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_rekap_purchase_requisition, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        temp = list(data['form']['operating_unit_ids'])
        # if selected more than one operating_unit_ids or selected only one operating_unit_ids 
        str_operating_unit_id = str(tuple(data['form']['operating_unit_ids'])) if len(temp) > 1 else '('+str(temp[0])+')'
        params = {
                'company_name': data['form']['company_id'][1],
                'date_start' : str(data['form']['date_start']),
                'date_stop' : str(data['form']['date_stop']),
                'operating_unit_query': "pr.operating_unit_id in %s "%(str_operating_unit_id if data['form']['operating_unit_ids'] else '1=1') # [(5,[1,1,1,1,1,1,1,])]
                }
        # print('-------->params2', params)
        return params

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data['form']['report_type']
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.report_rekap_purchase_requisition', 'wizard.rekap.purchase.requisition', parser=jasper_rekap_purchase_requisition)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
