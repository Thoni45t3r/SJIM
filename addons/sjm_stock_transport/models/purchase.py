from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit    = ['purchase.order']

    transport_invoice_id         = fields.Many2one("stock.transport.invoice", string="Stock Transport Invoice")