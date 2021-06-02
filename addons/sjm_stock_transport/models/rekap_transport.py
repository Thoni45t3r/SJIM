import time
import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import base64
import xlrd
from xlrd import open_workbook, XLRDError
from odoo import models, fields, tools, exceptions, api, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DT
import os
import tempfile

import logging
_logger = logging.getLogger(__name__)

class import_rekap_timbang_line(models.Model):
	_inherit = 'import.rekap.timbang.line'
	_description = 'Rekap Timbang Line'

	transport_move_id = fields.Many2one("stock.transport.move", "Transport Move ID")
	wb_do = fields.Char(string="Delivery Order")