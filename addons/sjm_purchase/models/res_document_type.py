from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class res_document_type(models.Model):
	_inherit = 'res.document.type'

	account_purchase_susut_id = fields.Many2one('account.account', 'Purchase Susut Account')