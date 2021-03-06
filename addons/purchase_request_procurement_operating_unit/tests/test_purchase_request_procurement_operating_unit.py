# -*- coding: utf-8 -*-
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016-17 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import common


class TestProcurement(common.TransactionCase):

    def setUp(self):
        super(TestProcurement, self).setUp()
        self.res_users_model = self.env['res.users']
        self.procurement_order_model = self.env['procurement.order']
        self.procurement_rule_model = self.env['procurement.rule']
        self.warehouse_id = self.env.ref('stock.warehouse0')

        # Main Operating Unit
        self.ou1 = self.env.ref('operating_unit.main_operating_unit')
        # B2C Operating Unit
        self.b2c = self.env.ref('operating_unit.b2c_operating_unit')

        # Products
        self.product1 = self.env.ref('product.product_product_9')
        self.product1.write({'purchase_request': True})

        # Picking Type
        b2c_wh = self.env.ref('stock_operating_unit.stock_warehouse_b2c')
        self.b2c_type_in_id = b2c_wh.in_type_id.id
        self.picking_type = self.env.ref('stock.picking_type_in')

        self.rule = self._create_procurement_rule()
        self.procurement_order = self._create_procurement_order()

    def _create_procurement_rule(self):
        rule = self.procurement_rule_model.\
            create({'name': 'Procurement rule',
                    'action': 'buy',
                    'picking_type_id': self.picking_type.id,
                    })
        return rule

    def _create_procurement_order(self):
        # On change for warehouse_id
        new_line = self.procurement_order_model.new()
        new_line.warehouse_id = self.warehouse_id
        new_line.onchange_warehouse_id()
        location_id = new_line.location_id
        # On change for product_id
        new_line = self.procurement_order_model.new()
        new_line.product_id = self.product1.id
        new_line.onchange_product_id()
        product_uom = new_line.product_uom
        procurement = self.procurement_order_model.\
            create({'product_id': self.product1.id,
                    'product_uom': product_uom.id,
                    'product_qty': '10',
                    'name': 'Procurement Order',
                    'warehouse_id': self.warehouse_id.id,
                    'rule_id': self.rule.id,
                    'location_id': location_id.id,
                    })
        procurement.run()
        procurement.check()
        return procurement

    def test_security(self):
        self.assertEqual(self.procurement_order.location_id.operating_unit_id,
                         self.procurement_order.request_id.operating_unit_id,
                         'The Operating Unit in Procurement Order Location'
                         'does not match to Purchase Request OU.')
