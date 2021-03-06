# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

{
    'name': 'Debit Note',
    'depends': ['c10i_account_invoice_advance'],
    'description': """
===========================
 Debit Note
===========================
""",
    'author'    : "Konsaltén Indonesia (Consult10 Indonesia)",
    'website'   : "www.consult10indonesia.com",
    'category'  : 'Accounting',
    'sequence'  : 32,
    'license'   : 'AGPL-3',
    'data': [
        # 'data/ir_sequence.xml',
        # 'security/ir.model.access.csv',
        # 'wizard/wizard_invoice_advance_balance_views.xml',
        # 'reports/report_views.xml',
        'views/account_debit_note_views.xml',
        'views/account_invoice_views.xml',
    ],
    'installable': True,
    'application': True,
}
