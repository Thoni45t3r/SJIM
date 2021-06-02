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
    'name': 'SJIM Payment Instruction',
    'depends': ['base','account','c10i_account','c10i_account_location','c10i_account_invoice_advance'],
    'description': """
        Payment Request and Payment Instruction
    """,
    'author'    : "Konsaltén Indonesia (Consult10 Indonesia)",
    'website'   : "www.consult10indonesia.com",
    'category'  : 'Accounting',
    'sequence'  : 32,
    'license'   : 'AGPL-3',
    'data': [
        'data/ir_sequence.xml',
        'security/account_security.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_request_payment_from_invoice_views.xml',
        'wizard/wizard_report_outstanding_payment_request_views.xml',
        'wizard/wizard_payment_instruction_from_invoice_views.xml',
        'views/account_payment_request_views.xml',
        'views/account_payment_instruction_views.xml',
        'views/account_invoice_views.xml',
        'views/product_views.xml',
        'report/report_views.xml',
    ],
    'installable': True,
    'application': True,
}
