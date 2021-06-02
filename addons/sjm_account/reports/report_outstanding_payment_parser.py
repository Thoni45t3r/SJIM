# -*- coding: utf-8 -*-
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report

class jasper_report_outstanding_payment(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_outstanding_payment, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        params = {
                'company_name': data['form']['company_id'][1],
                'currency_name': data['form']['currency_name'],
                'date_start' : str(data['form']['date_start']),
                'date_stop' : str(data['form']['date_stop']),
                'status_id' : str(data['form']['state']),
                }
        return params

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data['form']['report_type']
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.report_outstanding_payment', 'wizard.report.outstanding.payment', parser=jasper_report_outstanding_payment,)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
