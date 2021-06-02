# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#   --- Deby Wahyu Kurdian ---                                               #
#                                                                            #
##############################################################################

from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report
import odoo.tools

class jasper_report_nota_kwitansi_sjm(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_nota_kwitansi_sjm, self).__init__(cr, uid, ids, data, context)

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
        return 'pdf'
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}
        
class jasper_report_nota_kwitansi_advance_sjm(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_nota_kwitansi_advance_sjm,self).__init__(cr, uid, ids, data, context)
        
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
        return 'pdf'   
        
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.report_nota_kwitansi_sjm', 'account.invoice', parser=jasper_report_nota_kwitansi_sjm,)
jasper_report.ReportJasper('report.report_nota_kwitansi_advance_sjm', 'account.invoice.advance', parser=jasper_report_nota_kwitansi_advance_sjm,)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: