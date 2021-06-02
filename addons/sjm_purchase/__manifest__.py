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
    'name'      : "Purchase Module for PT. Sinar Jaya Inti Mulia",
    'category'  : 'Custom Module',
    'version'   : '1.0.0.1',
    'author'    : "Konsaltén Indonesia (Consult10 Indonesia)",
    'website'   : "www.consult10indonesia.com",
    'license'   : 'AGPL-3',
    'depends'   : ['base', 'c10i_base', 'purchase', 'c10i_purchase', 'account', 'c10i_account', 'sjm_base', 'sjm_stock','c10i_account_invoice_advance'],
    'summary'   : """
                        SJM Purchase Module - C10i
                    """,
    'description'   : """
Customize Modul Purchase SJM
========================

Preferences
-----------
* Modified Sequence Number per Partner
                    """,
    'data'      : [

        'wizard/wizard_purchase_report_views.xml',
        'views/ir_sequence_views.xml',
        'views/purchase_views.xml',
        'views/res_document_type_views.xml',
        'views/report_purchase_order.xml',
        'reports/report_views.xml',
        'wizard/wizard_pending_po_views.xml',
        'wizard/wizard_pr_register_views.xml',
        'wizard/wizard_rekap_purchase_requisition_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
