# -*- coding: utf-8 -*-
######################################################################################################
#
#   @author Pranoto Tahrir Fathoni <Thoni.45t3r@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report

class jasper_report_general_ledger_by_locations(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_general_ledger_by_locations, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        return {
                'from_date'             : str(data['form']['from_date']),
                'to_date'               : str(data['form']['to_date']),
                'target_move'           : str(data['target_move']),
                'operating_unit_ids'    : str(data['form']['operating_unit_ids']),
                'type_location_id'      : str(data['form']['type_location_id']),
                'company_id'            : data['form']['company_id'][0],
                }

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data['report_type']
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.report_general_ledger_by_locations', 'wizard.general.ledger.by.locations', parser=jasper_report_general_ledger_by_locations,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
