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
    'name'      : "LHP Module for PT. Sinar Jaya Inti Mulya",
    'category'  : 'Custom Module',
    'version'   : '1.0.0.1',
    'author'    : "Konsaltén Indonesia",
    'website'   : "www.konsaltenindonesia.com",
    'license'   : 'AGPL-3',
    'depends'   : ['base', 
        'c10i_base', 
        'sjm_base', 
        'stock', 
        'c10i_stock', 
        'c10i_account', 
        'c10i_account_location',
        'c10i_palm_oil_mill',
        'report_xlsx'],
    'summary'   : """
                        SJM Module - C10i
                    """,
    'description'   : """
Customize Modul Base KLI
========================

Preferences
-----------
* Add LHP, SOUNDING
                    """,
    'data'      : [
        'views/account_invoice_views.xml',
        'views/account_voucher_views.xml',
        'reports/report_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
