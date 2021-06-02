# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

{
    'name'      : "Warehouse Module for PT. Sinar Jaya Inti Mulia",
    'category'  : 'Custom Module',
    'version'   : '1.0.0.1',
    'author'    : "Konsaltén Indonesia (Consult10 Indonesia)",
    'website'   : "www.consult10indonesia.com",
    'license'   : 'AGPL-3',
    'depends'   : ['base', 'c10i_base', 'sjm_base',
                   'stock', 'c10i_stock', 'c10i_account',
                   'c10i_account_location', 'c10i_stock_inter_warehouse'],
    'summary'   : """
                        SJM Purchase Module - C10i
                    """,
    'description'   : """
Customize Modul Base SJM
========================

Preferences
-----------
* Add SKB
                    """,
    'data'      : [
        'reports/report_views.xml',
        'views/stock_picking_views.xml',
        'wizard/wizard_report_picking_skb_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
