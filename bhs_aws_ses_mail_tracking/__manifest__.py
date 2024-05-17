{
    'name': 'AWS SES Mail Tracking',
    'summary': 'Proper redirection of fetched replies of emails sent from Odoo through SES outgoing.',
    'version': '1.0',
    'category': 'Discuss',
    'website': 'https://bachasoftware.com/',
    'author': 'Bac Ha Software',
    'depends': ['mail', 'mass_mailing'],
    'data': [
        'data/tracking_reply_data.xml',
        'views/mailing_trace_view.xml',
    ],
    'images': ['static/description/banner.gif'],
    'license': 'LGPL-3',
}
