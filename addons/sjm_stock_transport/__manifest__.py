# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2020  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Anggar Bagus Kurniawan <anggar.bagus@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

{
    'name'      : "Stock Transport",
    'category'  : 'Custom Module',
    'version'   : '1.0.0.1',
    'author'    : "Konsaltén Indonesia (Consult10 Indonesia)",
    'website'   : "www.consult10indonesia.com",
    'license'   : 'AGPL-3',
    'depends'   : ['base', 'c10i_base', 'sjm_base', 'stock', 'c10i_stock', 'c10i_account', 'c10i_account_location','c10i_palm_oil_mill', 'sjim_weighbridge', 'c10i_purchase', 'purchase'],
    'summary'   : """
                        Stock Transport Management
                    """,
    'description'   : """
Customize Modul Base KLI
========================

Preferences
-----------
* Stock Transport Management
                    """,
    'data'      : [
        'security/stock_transport.xml',
        'views/stock_transport_rate_view.xml',
        'views/stock_transport_move_view.xml',
        'views/stock_transport_import_view.xml',
        'views/delivery_order_weighbridge_views.xml',
        'views/generate_transport_data_views.xml',
        'views/stock_transport_accrue_views.xml',
        'views/stock_transport_invoice_views.xml',
        'views/purchase_views.xml',
        'views/rekap_transport_views.xml',
        'views/partner_views.xml',
        'wizard/stock_transport_report_wizard_views.xml',
        'wizard/stock_transport_report_purchase_wizard_views.xml',
        'wizard/stock_transport_report_sale_wizard_views.xml',
        'wizard/stock_transport_report_spk_wizard_views.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
