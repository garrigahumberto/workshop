"""Tipos de reparación: agrupan trabajos y definen requisitos configurables."""
from odoo import fields, models


class WorkshopRepairType(models.Model):
    """Tipo de reparación (por ejemplo, «Electricidad» o «Motor»).

    Puede sugerir procedimientos y definir si se exige aceptación del
    presupuesto. NO define un ciclo de estados alternativo ni puede desactivar
    controles críticos (especificación funcional §11).
    """

    _name = 'workshop.repair.type'
    _description = 'Tipo de reparación'
    _order = 'name, id'

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'El código del tipo de reparación debe ser único.',
    )

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True, copy=False, index=True)
    description = fields.Text(string='Descripción')
    active = fields.Boolean(string='Activo', default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
    )
    require_quote_acceptance = fields.Boolean(
        string='Exige aceptación del presupuesto',
        default=True,
        help='Si está activo, la reparación no puede iniciarse sin registrar '
             'antes la aprobación del presupuesto.',
    )
    suggested_procedure_ids = fields.Many2many(
        'workshop.procedure',
        'workshop_repair_type_procedure_rel',
        'repair_type_id',
        'procedure_id',
        string='Procedimientos sugeridos',
    )
