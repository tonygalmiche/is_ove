# -*- coding: utf-8 -*-

{
    'name': 'OVE',
    'version': '1.0',
    'category': 'InfoSaône',
    'description': """
OVE Gestion des usagers
""",
    'author': 'Tony GALMICHE / Asma BOUSSELMI',
    'maintainer': 'InfoSaone',
    'website': 'http://www.infosaone.com',
    'depends': ['base', 'document'],
    'data': ['security/is_ove_security.xml',
             'security/ir.model.access.csv',
             'views/assets.xml',
             'is_ove_view.xml',
             'is_ove_data.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
