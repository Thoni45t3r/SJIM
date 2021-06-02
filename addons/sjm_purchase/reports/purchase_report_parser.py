from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report
import odoo.tools

class jasper_report_purchase_report(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_purchase_report, self).__init__(cr, uid, ids, data, context)
    
    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        doc_type_ids = data['form'].get('doc_type_ids',[])
        data['form'].update({'doc_type_ids': str(doc_type_ids)})
        data['form'].update({'company_name': 'PT. SINAR JAYA INTI MULYA'})
        return data['form']

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data['report_type']
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

# jasper_report.ReportJasper('report.report_purchase_report_rekap', 'wizard.purchase.report', parser=jasper_report_purchase_report,)
# jasper_report.ReportJasper('report.report_purchase_report_rekap_xslx', 'wizard.purchase.report', parser=jasper_report_purchase_report,)
# jasper_report.ReportJasper('report.report_purchase_report_rekap_spb', 'wizard.purchase.report', parser=jasper_report_purchase_report,)
# jasper_report.ReportJasper('report.report_purchase_report_rekap_spb_xlsx', 'wizard.purchase.report', parser=jasper_report_purchase_report,)
# jasper_report.ReportJasper('report.report_purchase_report_rekap_spk', 'wizard.purchase.report', parser=jasper_report_purchase_report,)
# jasper_report.ReportJasper('report.report_purchase_report_rekap_spk_xlsx', 'wizard.purchase.report', parser=jasper_report_purchase_report,)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: