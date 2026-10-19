"""Equipos o activos de los clientes atendidos por el taller."""
from odoo import fields, models


class WorkshopEquipment(models.Model):
    """Artículo o equipo que puede aparecer en varias órdenes de trabajo.

    La orden también puede existir sin un equipo registrado (los datos de
    identificación son opcionales). Se usa un modelo propio para no depender
    del módulo Mantenimiento (ver arquitectura §2.4 y modelo lógico §4.2).
    """

    _name = 'workshop.equipment'
    _description = 'Equipo del cliente'
    _order = 'name, id'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre o descripción que permita identificar el equipo.',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
    )
    equipment_type = fields.Char(string='Tipo de equipo')
    brand = fields.Char(string='Marca')
    model = fields.Char(string='Modelo')
    serial_number = fields.Char(string='Número de serie')
    description = fields.Text(string='Observaciones')
    active = fields.Boolean(string='Activo', default=True)
    order_count = fields.Integer(
        string='Órdenes',
        compute='_compute_order_count',
    )

    def _compute_order_count(self):
        """Cuenta las órdenes de trabajo asociadas a cada equipo."""
        Order = self.env['workshop.order']
        for equipment in self:
            equipment.order_count = Order.search_count(
                [('equipment_id', '=', equipment.id)]
            )

    def action_view_orders(self):
        """Abre la lista de órdenes del equipo (botón inteligente)."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Órdenes del equipo',
            'res_model': 'workshop.order',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {
                'default_equipment_id': self.id,
                'default_partner_id': self.partner_id.id,
            },
        }
