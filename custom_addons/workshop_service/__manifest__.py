{
    'name': 'Workshop Service',
    'author': 'Taller',
    'summary': 'Gestión de órdenes de trabajo para talleres de reparación y servicios',
    'version': '20.0.1.0.0',
    'category': 'Services',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/workshop_groups.xml',
        'security/ir.access.csv',
        'data/workshop_sequence.xml',
        'views/workshop_order_views.xml',
        'views/workshop_menus.xml',
    ],
    'installable': True,
    'application': True,
}
