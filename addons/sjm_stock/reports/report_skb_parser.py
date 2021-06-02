from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report

class jasper_report_stock_picking(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_stock_picking, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        #data['form'].update({'company_name': 'PT. SINAR JAYA INTI MULYA'})
        #data['form'].update({'location_id': data['form']['location_id'][0]})
        #return data['form']
        return {
                'date_start'    : str(data['form']['date_start']),
                'date_stop'     : str(data['form']['date_stop']),
                'location_id'   : str(data['form']['location_id']),
                'company_id'    : data['form']['company_id'][0],
                }

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data['report_type']
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.report_picking_skb', 'wizard.report.picking.skb', parser=jasper_report_stock_picking,)
jasper_report.ReportJasper('report.report_picking_skb_xlsx', 'wizard.report.picking.skb', parser=jasper_report_stock_picking,)
jasper_report.ReportJasper('report.report_picking_skb_without_subtotal', 'wizard.report.picking.skb', parser=jasper_report_stock_picking,)

class jasper_report_stock_picking_with_type_locations(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_report_stock_picking_with_type_locations, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        #data['form'].update({'company_name': 'PT. SINAR JAYA INTI MULYA'})
        #data['form'].update({'location_id': data['form']['location_id'][0]})
        #data['form'].update({'type_location_id': data['form']['type_location_id'][0]})
        #return data['form']
        return {
                'date_start'        : str(data['form']['date_start']),
                'date_stop'         : str(data['form']['date_stop']),
                'location_id'       : str(data['form']['location_id']),
                'type_location_id'  : str(data['form']['type_location_id']),
                'company_id'        : data['form']['company_id'][0],
                }
        
    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self,cr, uid, ids, data, context):
        return data['report_type']
    
    def generate_records(self, cr, uid, ids, data, context):
        return {}
jasper_report.ReportJasper('report.report_picking_skb_with_type_locations_xlsx', 'wizard.report.picking.skb', parser=jasper_report_stock_picking_with_type_locations,)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
