# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2020  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Anggar Bagus Kurniawan <anggar.bagus@gmail.com>
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
from odoo.addons import decimal_precision as dp
import time

class StockTransportLocation(models.Model):
    _name = "stock.transport.location"
    _description = "Master data Location"

    name = fields.Char('Location', required=True)

    _sql_constraints = [
       ('name_unique', 'unique(name)', 'Nama sudah pernah dipakai'),  
    ]

class StockTransportRate(models.Model):
    _name = "stock.transport.rate"
    _description = "Master Data Rate"
    _rec_name = "partner_id"

    @api.one
    @api.constrains('partner_id', 'src_location_id', 'dest_location_id', 'start_date', 'end_date','rate_type')
    def _check_overlap(self):
        for transport in self:
            overlapped_rate = self.search([('partner_id','=',transport.partner_id.id)
                ,('start_date','<=',transport.start_date),('end_date','>=',transport.end_date)
                ,('src_location_id','=',transport.src_location_id.id),('dest_location_id','=',transport.dest_location_id.id)
                ,('rate_type','=',transport.rate_type),('product_id','=',transport.product_id.id)
                ,('id','!=',transport.id)])
            if overlapped_rate:
                raise ValidationError('Rate ini overlap dengan record lain')

    partner_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier','=',True)], required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    src_location_id = fields.Many2one('stock.transport.location', string='Asal Lokasi', required=True)
    dest_location_id = fields.Many2one('stock.transport.location', string='Tujuan Lokasi', required=True)
    rate_type = fields.Selection([('by_weight','By Weight'),('by_delivery','By Delivery'),('by_distance','By Distance')], string='Rate Type', required=True)
    rate = fields.Float("Rate", digits=dp.get_precision('Product Price'), required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)

    # _sql_constraints = [
    #    ('partner_src_dest_unique', 'unique(partner_id, src_location_id, dest_location_id, start_date, end_date, rate_type)', 'Vendor, Asal, & Tujuan Sudah pernah diinput'),  
    # ]