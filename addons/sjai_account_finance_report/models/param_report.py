# -*- encoding: utf-8 -*-
# © 2018-2019 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
from odoo import api, fields, models, _
from odoo.addons.jasper_reports import JasperDataParser
from odoo.addons.jasper_reports import jasper_report
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class AccountFinancialReport(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(AccountFinancialReport, self).__init__(cr, uid, ids, data, context)

    def generate_data_source(self, cr, uid, ids, data, context):
        return 'parameters'

    def generate_parameters(self, cr, uid, ids, data, context):
        report_name = data['form']['report_name'] if data['form'].get('report_name') else _(''),
        if not report_name:
            raise UserError('Report Name is Invalid!')
        return {
            'period_id': data['form']['period_id'] if data['form'].get('period_id') else 0,
            'states': str(data['form']['target_move']) if data['form'].get('target_move') else 0,
            'id': str(ids).replace("[","(").replace("]",")"),
            'SUBREPORT_DIR': str(data['form']['SUBREPORT_DIR']) if data['form'].get('SUBREPORT_DIR') else '',
        }

    def generate_properties(self, cr, uid, ids, data, context):
        return {}

    def generate_output(self, cr, uid, ids, data, context):
        if 'form' in data or data.get('form'):
            return data['form']['report_type']
        return _("pdf")

    def generate_records(self, cr, uid, ids, data, context):
        return {}

jasper_report.ReportJasper('report.c10i_account_financial_report', 'wzd.account.financial.report', parser=AccountFinancialReport, )