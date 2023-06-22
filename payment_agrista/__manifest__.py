# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Provider: Agrista',
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "An payment provider covering South Africa.",
    'depends': ['payment'],
    'data': [
        'views/payment_agrista_templates.xml',
        'views/payment_provider_views.xml',
        'views/payment_token_views.xml',

        'data/payment_provider_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'payment_agrista/static/src/scss/payment_agrista.scss',
            'payment_agrista/static/src/js/payment_form.js',
        ],
    },
    'license': 'LGPL-3',
}
