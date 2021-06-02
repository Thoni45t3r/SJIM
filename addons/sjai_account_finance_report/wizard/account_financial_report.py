# -*- coding: utf-8 -*-
# © 2018 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
import time
from datetime import date
from odoo import http
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class WzdAccountFinancialReport(models.TransientModel):
    _name = "wzd.account.financial.report"
    _description = "Accounting Financial Report"

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    period_id = fields.Many2one('account.period', 'Period')
    report_type = fields.Selection([('xls', 'XLS'), ('pdf', 'PDF')], string='Type', default='xls')
    target_move = fields.Selection([('posted', 'All Posted Entries'), ('all', 'All Entries')],
                                   string='Target Moves', default='posted')

    @api.multi
    def print_report(self):
        addons_path = http.addons_manifest['sjai_account_finance_report']['addons_path']
        data = self.read()[-1]
        context = dict(self._context or {})
        if isinstance(data, dict):
            if self.period_id:
                data.update({
                    'period_id': self.period_id.id,
                    'target_move': "%s" % _("".join([_("['"), _("posted"), _("']")] if self.target_move and self.target_move == 'posted' else [_("["), _("'draft','posted'"), _("]")])),
                })
            if addons_path:
                data.update({'SUBREPORT_DIR': addons_path + str("/sjai_account_finance_report/report/")})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': _('c10i_account_financial_report'),
            'datas': {
                'model': 'wzd.account.financial.report',
                'id': self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                'ids': self._context.get('active_ids') and self._context.get('active_ids') or [],
                'form': data,
            },
            'nodestroy': False
        }

class AccountingReport(models.TransientModel):
    _inherit = "accounting.report"

    @api.model
    def _get_account_reports(self):
        reports = []
        if self._context.get('active_id'):
            menu = self.env['ir.ui.menu'].browse(self._context.get('active_id')).name
            reports = self.env['account.financial.report'].search([('name', 'ilike', menu)])
        return reports and [(6,0,reports.ids)] or []

    account_report_id = fields.Many2one('account.financial.report', string='Account Reports', required=False)
    account_report_ids = fields.Many2many('account.financial.report', string='Account Reports', required=True, default=_get_account_reports)

    def check_report(self, data):
        if self.report_type != 'xlsx':
            res = super(AccountingReport, self).check_report()
            return res
        else:
            self.ensure_one()
            data = {}
            # data['ids'] = self.env.context.get('active_ids', [])
            # data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
            # data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
            # used_context = self._build_contexts(data)
            # data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
            
            # data2 = {}
            # data2['form'] = self.read(['account_report_id', 'date_from_cmp', 'date_to_cmp', 'journal_ids', 'filter_cmp', 'target_move'])[0]
            # for field in ['account_report_id']:
            #     if isinstance(data2['form'][field], tuple):
            #         data2['form'][field] = data2['form'][field][0]
            # comparison_context = self._build_comparison_context(data2)
            
            # data['form']['comparison_context'] = comparison_context
            # data['form'].update(self.read(['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move'])[0])
            return self.env['report'].get_action(self, 'report_sjai_financial_xlsx', data=data)