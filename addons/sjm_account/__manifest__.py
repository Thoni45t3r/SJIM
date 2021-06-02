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
    'name'      : "Account Module for PT. Sinar Jaya Inti Mulia",
    'category'  : 'Custom Module',
    'version'   : '1.0.0.1',
    'author'    : "Konsaltén Indonesia (Consult10 Indonesia)",
    'website'   : "www.consult10indonesia.com",
    'license'   : 'AGPL-3',
    'depends'   : ['base', 'c10i_account',
                   'c10i_account_invoice_advance', 'account',
                   'c10i_account_faktur_pajak', 'sjm_base'],
    'summary'   : """
                        SJM Account Module - C10i
                    """,
    'description'   : """
Customize Modul Accounting SJM
========================

Preferences
-----------
* Modified Sequence Number per Partner
                    """,
    'data'      : [
        'views/ir_sequence_views.xml',
        'views/account_views.xml',
        'reports/report_views.xml',
        'wizard/wizard_report_outstanding_payment_views.xml',
        'wizard/wizard_report_outstanding_invoice_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
