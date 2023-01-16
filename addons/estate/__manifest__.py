# -*- coding: utf-8 -*-

{
    'name': 'Real Estate',
    'category': 'Uncategorized',
    'version': '0.4',
    'depends': [
        'base',
        
    ],
    'application': True,
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_menu_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_view.xml',
    ],
}
