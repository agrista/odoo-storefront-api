# -*- coding: utf-8 -*-
# Copyright 2023 ODOOGAP/PROMPTEQUATION LDA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    # Application Information
    'name': 'Agrista Payment Acquirer or Storefront',
    'category': 'Accounting/Payment Acquirers',
    'version': '1.0.1',
    'summary': 'Agrista Payment Acquirer: Adapting Agrista for Storefront',

    # Author
    'author': "Agrista",
    'website': "https://agrista.com/",
    'maintainer': 'Agrista',
    'license': 'LGPL-3',

    # Dependencies
    'depends': [
        'payment',
        'payment_agrista'
    ],

    # Views
    'data': [],

    # Technical
    'installable': True,
    'application': False,
    'auto_install': False,
}
