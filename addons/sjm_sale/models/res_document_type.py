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

    source_warehouse_note   = fields.Text("Asal Barang")
    picking_location_note   = fields.Text("Lokasi Pemuatan")
    price_statement_rule    = fields.Char("Peraturan Pemerintah")
    delivery_of_goods       = fields.Char("Penyerahan")
    quantity_note           = fields.Char("Catatan Kuantitas")
    quality_ffa             = fields.Char("FFA")
    quality_mni             = fields.Char("M & I")
    quality_iv              = fields.Char("IV (WIJS)")
    quality_claim           = fields.Text("Perhitungan Klaim")
    quality_note            = fields.Text("Catatan Kualitas")
    other_claim             = fields.Text("Lain - lain")
    payment_term_note       = fields.Text("Pembayaran")
    partner_bank_id         = fields.Many2one("res.partner.bank", string="Bank Payment")
    ppn_include             = fields.Boolean(string="Include PPN")
    sign_seller             = fields.Char("Ttd Penjual")
    sign_buyer              = fields.Char("Ttd Pembeli")