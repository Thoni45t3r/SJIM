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

class DeliveryOrderWeighbridge(models.Model):
    _name = "delivery.order.weighbridge"
    _description = "Delivery Order Weighbrige"


    asal = fields.Many2one("stock.transport.location", string="Asal")
    tujuan = fields.Many2one("stock.transport.location", string="Tujuan")
    name = fields.Char("Nomor")
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')], string='State', default='draft')

    @api.multi
    def action_confirm(self):
    	for res in self:
    		res.state = "confirmed"

    @api.multi
    def action_draft(self):
    	for res in self:
    		res.state = "draft"