# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#   --- Pranoto Tahrir Fathoni ---                                               #
#                                                                            #
##############################################################################

from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report
import odoo.tools

class jasper_report_nota_purchase_sparepart(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_nota_purchase_sparepart, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        return {
            'id'            : int(data['id']),
            'suffix_report' : " " + str(data['name'])
        }

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return 'xlsx'
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.report_nota_purchase_sparepart', 'purchase.order', parser=jasper_report_nota_purchase_sparepart,)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: