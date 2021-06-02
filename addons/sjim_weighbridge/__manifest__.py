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
    'name': 'SJIM Weightbridge Data Converter',
    'depends': ['c10i_base', 'account',
                'c10i_stock',
                'c10i_account',
                'sjm_purchase',
                'sjm_sale',
                'c10i_bea_cukai'],
    'description': """
        Special Tools to collect data from Sampit Weightbridge 
        and convert it into Odoo's Data Structure
    """,
    'author'    : "Konsaltén Indonesia (Consult10 Indonesia)",
    'website'   : "www.consult10indonesia.com",
    'category'  : 'Accounting',
    'sequence'  : 32,
    'license'   : 'AGPL-3',
    'data': [
        'data/weighbridge_data.xml',
        'security/weighbridge_security.xml',
        'security/ir.model.access.csv',
        'views/master_data_views.xml',
        'views/weighbridge_metro_views.xml',
        'views/weighbridge_sampit_views.xml',
        'views/stock_views.xml',
        'views/manual_import_views.xml',
        'views/rekap_transport_views.xml',
        'report/report_views.xml',
        'wizard/wizard_weighbridge_recap_views.xml',
        'wizard/wizard_rekap_timbangan_manual_views.xml',
        'data/ir_sequence.xml',
    ],
    'installable': True,
    'application': False,
}
