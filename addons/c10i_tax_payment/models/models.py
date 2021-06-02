# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class c10i_tax_payment(models.Model):
#     _name = 'c10i_tax_payment.c10i_tax_payment'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100