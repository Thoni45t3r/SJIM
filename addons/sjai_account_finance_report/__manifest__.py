# -*- coding: utf-8 -*-
# © 2019 Ibrohim Binladin | ibradiiin@gmail.com | +62-838-7190-9782
{
    'name': 'Accounting and Financial Reports',
    'version': '10.0.0.1.0',
    'category': 'Customization',
    'summary': 'Custom Report Module Created by Ibrohim Binladin',
    'description': """
Accounting and Financial Report Customization
=============================================
* Laporan Neraca
* Laporan Neraca Detail
* Laporan Laba Rugi
* Laporan Laba Rugi Detail

""",
    'author': 'Konsaltén Indonesia (Consult10 Indonesia)',
    'website': 'http://www.consult10indonesia.com',
    'depends':[
        'base',
        'jasper_reports',
        'c10i_account',
    ],
    'demo': [],
    'test': [],
    'data':[
        # 'data/defaults.xml',
        # 'views/reports.xml',
        # 'views/master_data_report.xml',
        'views/account_financial_report_views.xml',
        'wizard/account_financial_report_view.xml',
        # 'views/account_report_type_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
