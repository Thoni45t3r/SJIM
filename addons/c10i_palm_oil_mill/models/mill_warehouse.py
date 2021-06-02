# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   @author Pranoto Tahrir Fathoni <thoni.45t3r@gmail.com>
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

class mill_warehouse(models.Model):
    _name           = "mill.warehouse"
    _description    = "Master Warehouse"
    
    def _default_location_type(self):
        location_type_ids   = self.env['account.location.type'].search([('general_charge','=',False)])
        if location_type_ids:
            return location_type_ids[0].id
        else:
            return False
            
    name                = fields.Char('Gudang', required=True)
    code                = fields.Char('Kode', required=True)
    product_id          = fields.Many2one('product.product', string='Product')
    location_id         = fields.Many2one(comodel_name="account.location", string="Lokasi")
    location_type_id    = fields.Many2one(comodel_name="account.location.type", string="Tipe Lokasi", ondelete="restrict", default=_default_location_type)
    active              = fields.Boolean("Active", default=True)
    parent_id           = fields.Many2one("mrp.workcenter", string="Parent")
    company_id          = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    
    @api.model
    def create(self, values):
        location_name       = values.get('name', False)
        location_code       = values.get('code', False)
        location_type_id    = values.get('location_type_id', False)
        location_values     = {
            'name'      : location_name or "(NoName)",
            'code'      : location_code or "(NoCode)",
            'type_id'   : location_type_id or False,
        }
        new_location = False
        location = super(mill_warehouse, self).create(values)
        if location:
            new_location = self.env['account.location'].create(location_values)
        if new_location:
            location.location_id = new_location.id
        return location

    @api.multi
    def write(self, values):
        if 'name' in values and self.location_id:
            self.location_id.write({'name': values.get('name', False)})
        if 'code' in values and self.location_id:
            self.location_id.write({'code': values.get('code', False)})
        if 'location_type_id' in values and self.location_id:
            self.location_id.write({'type_id': values.get('location_type_id', False)})
        if 'active' in values and self.location_id:
            self.location_id.write({'active': values.get('active', False)})
        return super(mill_warehouse, self).write(values)

    @api.multi
    def unlink(self):
        for location in self:
            if location.location_id:
                location.location_id.unlink()
        location = super(mill_warehouse, self).unlink()
        return location