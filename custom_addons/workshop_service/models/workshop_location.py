from odoo import fields, models


class WorkshopLocation(models.Model):
    _name = 'workshop.location'
    _description = 'Ubicación operativa del taller'
    _order = 'sequence, name'

    _location_name_unique = models.Constraint(
        'UNIQUE(name, company_id)',
        'El nombre de la ubicación debe ser único dentro de la compañía.',
    )

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código')
    location_type = fields.Selection(
        [
            ('store', 'Tienda'),
            ('workshop', 'Taller'),
        ],
        string='Tipo',
        required=True,
        default='workshop',
    )
    stock_location_id = fields.Many2one(
        'stock.location',
        string='Ubicación de inventario',
        domain=[('usage', '=', 'internal')],
        ondelete='restrict',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
