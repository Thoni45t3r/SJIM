# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
#   @modified Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################


from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    skb = fields.Boolean("Is SKB?")
    inter_transfer_send = fields.Boolean("Is Internal Transfer (Send)?")
    inter_transfer_receive = fields.Boolean("Is Internal Transfer (Receive)?")

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    skb = fields.Boolean("Is SKB?")
    # Untuk modul internal transfer
    receipt_picking_id = fields.Many2one('stock.picking', string='Add Receipt', readonly=True, states={'draft': [('readonly',False)]})

    @api.model
    def default_get(self, fields):
        res = super(StockPicking, self).default_get(fields)
        picking_type_ids = self.env['stock.picking.type'].search([('code','=','internal'),('skb','=',True),
                ('return_picking_type_id','!=',False),
                ('default_location_src_id.usage','=','internal'),
                ('default_location_dest_id.usage','!=','internal')])
        picking_type_ids2 = self.env['stock.picking.type'].search([('code','=','incoming'),('skb','=',False)])
        if res.get('skb',False):
            res['picking_type_id'] = picking_type_ids[-1].id if picking_type_ids else False
        elif res.get('inter_warehouse') and res.get('inter_warehouse_type'):
            src_picking_type = self.env['stock.picking.type'].search([('code','=','internal'),
                ('inter_transfer_send','=',True),
                ('default_location_src_id.usage','=','internal'),
                ('default_location_dest_id.usage','=','transit')])
            dest_picking_type = self.env['stock.picking.type'].search([('code','=','internal'),
                ('inter_transfer_receive','=',True),
                ('default_location_src_id.usage','=','transit'),
                ('default_location_dest_id.usage','=','internal')])
            if res['inter_warehouse_type'] == 'internal_out' and src_picking_type:
                res['picking_type_id'] = src_picking_type[-1].id if src_picking_type else False
                res['dest_picking_type_id'] = dest_picking_type[-1].id if dest_picking_type else False
            elif res['inter_warehouse_type'] == 'internal_in' and dest_picking_type:
                res['picking_type_id'] = dest_picking_type[-1].id if dest_picking_type else False
                res['dest_picking_type_id'] = src_picking_type[-1].id if src_picking_type else False
        return res

    def _prepare_move_line_from_receipt_line(self, line):
        order_name = line.purchase_line_id and line.purchase_line_id.order_id.name or ''
        pr_name = line.purchase_line_id and line.purchase_line_id.request_id and line.purchase_line_id.request_id.name or ''
        note = '%s\n%s'%(order_name,pr_name)
        data = {
            'purchase_line_id2': line.purchase_line_id and line.purchase_line_id.id or False,
            'date_expected': datetime.now(),
            'picking_type_id': self.picking_type_id.id,
            'warehouse_id': self.picking_type_id.warehouse_id.id,
            'name': line.picking_id.name+': '+line.name,
            'product_id': line.product_id.id,
            'product_uom': line.product_uom.id,
            'product_uom_qty': 0.0,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'state': 'draft',
            'procure_method': 'make_to_stock',
            'note': note,
        }
        return data

    @api.onchange('receipt_picking_id')
    def onchange_receipt_picking(self):
        if self.state=='draft' and self.inter_warehouse and self.receipt_picking_id:
            new_lines = self.env['stock.move']
            for line in self.receipt_picking_id.move_lines:
                data = self._prepare_move_line_from_receipt_line(line)
                new_line = new_lines.new(data)
                new_lines += new_line

            self.move_lines += new_lines
            self.receipt_picking_id= False

    # @api.multi
    # def write(self, update_vals):
    #     print ">>>>>>>>>>>>>>>>>>>", update_vals
    #     res = super(StockPicking, self).write(update_vals)
    #     # print ">>>>>>>>>>>>>>>>>>>", asd
    #     return res

    @api.multi
    def print_report_picking(self):
        if self.skb:
            if self.skb == False:
                return {
                        'type'          : 'ir.actions.report.xml',
                        'report_name'   : 'report_grn',
                        'datas'         : {
                            'model'         : 'stock.picking',
                            'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                            'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                            'name'          : self.name or "---",
                            },
                        'nodestroy'     : False
                }  
            else:
                return {
                        'type'          : 'ir.actions.report.xml',
                        'report_name'   : 'report_stock_picking',
                        'datas'         : {
                            'model'         : 'stock_picking',
                            'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                            'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                            'name'          : self.name or "---",
                            },
                        'nodestroy'     : False
                }
        elif self.inter_warehouse:
            if self.inter_warehouse_type=='internal_out':
                return {
                        'type'          : 'ir.actions.report.xml',
                        'report_name'   : 'report_form_spb',
                        'datas'         : {
                            'model'         : 'stock.picking',
                            'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                            'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                            'name'          : self.name or "---",
                            },
                        'nodestroy'     : False
                }
            else:
                return {
                        'type'          : 'ir.actions.report.xml',
                        'report_name'   : 'report_form_spb',
                        'datas'         : {
                            'model'         : 'stock.picking',
                            'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                            'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                            'name'          : self.name or "---",
                            },
                        'nodestroy'     : False
                }