# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
import urllib3
from lxml import etree
import time

class Picking(models.Model):
	_inherit = 'stock.picking'

	transporter_id = fields.Many2one('res.partner', string='Transporter')
	# incoterm_id = fields.Many2one('stock.incoterms', string='Incoterm', domain=[('transport_cost','=',True)])
	vehicle_number = fields.Char('Vehicle Number')
	driver_name = fields.Char('Driver Name')

	tiket_timbang = fields.Char('No. Tiket Timbang')
	internal_quality_ffa = fields.Float('Free Fatid Acid (FFA)')
	internal_quality_ka = fields.Float('Kadar Air (KA)')
	internal_quality_kk = fields.Float('Kadar Kotor (KK)')
	vendor_quality_ffa = fields.Float('Free Fatid Acid (FFA)')
	vendor_quality_ka = fields.Float('Kadar Air (KA)')
	vendor_quality_kk = fields.Float('Kadar Kotor (KK)')

class StockMove(models.Model):
    _inherit = 'stock.move'

    netto_pks = fields.Float('Netto PKS', digits=(15,2))
    tara_weight = fields.Float('Tara Weight', digits=(15,2))
    potongan_weight = fields.Float('Potongan Weight', digits=(15,2))