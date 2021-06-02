# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2020
#   @author Pranoto Tahrir Fathoni <Thoni.45t3r@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

from odoo import api, fields, models
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report

class jasper_report_proforma_invoice(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_proforma_invoice, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        order_id = int(context.get('active_id', data.get('id',False)))
        env = api.Environment(cr, uid, context)
        if order_id:
            order = env['sale.proforma.invoice'].browse(order_id)
            return {
                    'id'            : order_id,
                    'suffix_report' : " Contract - " + order.name
            }
        else:
            return False

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data.get('report_type','pdf')
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.sale_proforma_invoice','sale.proforma.invoice', parser=jasper_report_proforma_invoice,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: