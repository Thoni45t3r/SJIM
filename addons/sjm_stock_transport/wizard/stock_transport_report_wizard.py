import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.addons import decimal_precision as dp
import time
import os, base64, xlrd
import logging
_logger = logging.getLogger(__name__)

class StockTransportReportWizard(models.TransientModel):
    _name = "stock.transport.report.wizard"
    _description = "Transport Report Creation Wizard"

    date_start = fields.Date('Date Start', required=True)
    date_end = fields.Date('Date End', required=True)
    product_id = fields.Many2one('product.product', 'Filter Product')
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.account'))
    
    def print_report(self):
        return self.env['report'].get_action(self, 'report_transport_data_xlsx')