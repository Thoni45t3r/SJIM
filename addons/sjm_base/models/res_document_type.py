# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

from odoo import models, fields, api, _

class ResDocumentType(models.Model):
    _inherit    = ['res.document.type']

    transport       = fields.Boolean("Is Transport?")
    header_report   = fields.Selection([('model_1','Bandar Lampung'), ('model_2','Jakarta')], string='Kop Surat', default="model_1")

class ResCompany(models.Model):
    _inherit    = ['res.company']

    head_office_transport_id = fields.Many2one(comodel_name="res.partner", string="Head Office 2")