{
    'name': 'Workshop Service',
    'author': 'Taller',
    'summary': 'Gestión de órdenes de trabajo para talleres de reparación y servicios',
    'description': """
Núcleo del módulo de taller (primera versión para demostración):

* Órdenes de trabajo con ciclo de vida validado en el servidor.
* Equipos del cliente y tipos de reparación.
* Procedimientos versionados (borrador, publicada, retirada) y composición
  mediante subprocedimientos, sin ciclos.
* Aplicación de procedimientos a las órdenes con copia histórica de líneas.
* Grupos de seguridad y permisos de acceso (ir.access, Odoo 20).

Fuera de esta versión: calidad, inventario y propuestas comerciales.
""",
    'version': '20.0.1.2.0',
    'category': 'Services',
    'license': 'LGPL-3',
    # mail: chatter y seguimiento de campos. product: productos y unidades de medida.
    'depends': ['base', 'mail', 'product'],
    'data': [
        'security/workshop_groups.xml',
        'security/ir.access.csv',
        'data/workshop_sequence.xml',
        'views/workshop_order_views.xml',
        'views/workshop_procedure_views.xml',
        'views/workshop_equipment_views.xml',
        'views/workshop_repair_type_views.xml',
        'views/workshop_menus.xml',
    ],
    'installable': True,
    'application': True,
}
