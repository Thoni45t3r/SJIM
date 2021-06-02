import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.addons import decimal_precision as dp
import time
import os, base64, xlrd
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
	_inherit = 'res.partner'
	_description = 'Partner'

	default_invoice_taxes_ids = fields.Many2many('account.tax', string="Default Taxes for Transport Invoice")
	default_account_ongkos_angkut_id = fields.Many2one('account.account', string="Default Account Ongkos Angkut")