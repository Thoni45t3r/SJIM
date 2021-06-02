# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report

class jasper_report_outstanding_payment_request(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_outstanding_payment_request, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        return {
                'to_date'       : data['form']['to_date'],
                }

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data['form']['report_type']
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.report_outstanding_payment_request_xls', 'wizard.report.outstanding.payment.request', parser=jasper_report_outstanding_payment_request,)
jasper_report.ReportJasper('report.report_outstanding_payment_request_comodity_xls', 'wizard.report.outstanding.payment.request.comodity', parser=jasper_report_outstanding_payment_request,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
