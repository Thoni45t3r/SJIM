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
    'name'      : "Sale Module for PT. Sinar Jaya Inti Mulia",
    'category'  : 'Custom Module',
    'version'   : '1.0.0.1',
    'author'    : "Konsaltén Indonesia (Consult10 Indonesia)",
    'website'   : "www.consult10indonesia.com",
    'license'   : 'AGPL-3',
    'depends'   : ['base', 'c10i_base', 'sale', 'c10i_sale',
                   'account', 'c10i_account', 'sjm_base', 'c10i_document_type', 'report_xlsx'],
    'summary'   : """
                        SJM Sale Module - C10i
                    """,
    'description'   : """
Customize Modul Sale SJM
========================

Preferences
-----------
* Remove view Warehouse
* Modified Sequence Number per Partner
                    """,
    'data'      : [
        'views/sale_views.xml',
        'views/res_document_type_views.xml',
        'views/ir_sequence_views.xml',
        'views/report_sale_order.xml',
        'reports/report_views.xml',
        'reports/report_proforma_invoice_qweb.xml',
        'reports/report_packing_list_qweb.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
