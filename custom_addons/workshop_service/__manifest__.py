{
    'name': 'Workshop Service',
    'author': 'Taller',
    'summary': 'Gestión de órdenes de trabajo para talleres de reparación y servicios',
    'version': '20.0.2.0.0',
    'category': 'Services',
    'license': 'LGPL-3',
    'depends': ['base', 'product', 'sale', 'stock'],
    'data': [
        'security/workshop_groups.xml',
        'security/ir.access.csv',
        'data/workshop_sequence.xml',
        'views/workshop_location_views.xml',
        'views/workshop_procedure_views.xml',
        'views/workshop_order_views.xml',
        'views/workshop_consumable_allocation_views.xml',
        'views/workshop_menus.xml',
        'views/workshop_dashboard_views.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'workshop_service/static/src/js/workshop_dashboard.js',
            'workshop_service/static/src/xml/workshop_dashboard.xml',
            'workshop_service/static/src/scss/workshop_dashboard.scss',
        ],
    },
}
