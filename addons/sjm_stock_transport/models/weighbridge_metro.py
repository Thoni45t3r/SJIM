import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
import urllib3
from lxml import etree
import time

import logging
_logger = logging.getLogger(__name__)

class WeighbridgeScaleMetro(models.Model):
    _inherit = "weighbridge.scale.metro"
    _description = "Timbangan Metro"
    _order = "id desc"

    transport_move_id = fields.Many2one("stock.transport.move", "Transport Move ID")