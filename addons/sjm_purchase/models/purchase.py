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

class PurchaseOrder(models.Model):
    _inherit    = ['purchase.order']

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        if res.partner_id and res.name:
            if res.name.find('custom_partner') > 0:
                partner_code    = str(res.partner_id.partner_code) if str(res.partner_id.partner_code) != 'False' else "PO"
                new_name        = res.name.replace(res.name[(res.name.find('custom_partner')):(res.name.find('custom_partner'))+14], str(partner_code))
                if res.name:
                    res.name = new_name
        return res

    price_statement_rule    = fields.Char("Peraturan Pemerintah")
    delivery_of_goods       = fields.Char("Penyerahan")
    quantity_note           = fields.Char("Kuantitas")
    quality_ffa             = fields.Char("FFA")
    quality_mni             = fields.Char("M & I")
    quality_iv              = fields.Char("IV (WIJS)")
    quality_claim           = fields.Text("Perhitungan Klaim")
    quality_note            = fields.Text("Catatan")
    other_claim             = fields.Text("Lain - lain")
    payment_term_note       = fields.Text("Pembayaran")
    partner_bank_id         = fields.Many2one("res.partner.bank", string="Bank Payment")
    ppn_include             = fields.Boolean(string="Include PPN")
    sign_seller             = fields.Char("Ttd Penjual", default="ROSDIANA")
    sign_buyer              = fields.Char("Ttd Pembeli", default="PEMBELI")


class PurchaseOrderLine(models.Model):
    _inherit    = ['purchase.order.line']

    order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, required=True, ondelete='cascade')
    date_order = fields.Datetime('Date Order', related="order_id.date_order", store=True)