from odoo import api, fields, models
from odoo.exceptions import UserError


class WorkshopProcedure(models.Model):
    _name = 'workshop.procedure'
    _description = 'Procedimiento de taller'
    _order = 'code, id'

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'El código del procedimiento debe ser único.',
    )

    name = fields.Char(
        string='Nombre',
        required=True,
    )
    code = fields.Char(
        string='Código',
        required=True,
        copy=False,
        index=True,
    )
    description = fields.Text(
        string='Descripción',
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )
    version_ids = fields.One2many(
        'workshop.procedure.version',
        'procedure_id',
        string='Versiones',
    )


class WorkshopProcedureVersion(models.Model):
    _name = 'workshop.procedure.version'
    _description = 'Versión de procedimiento de taller'
    _order = 'procedure_id, version_number desc'

    _procedure_version_unique = models.Constraint(
        'UNIQUE(procedure_id, version_number)',
        'El número de versión debe ser único dentro de cada procedimiento.',
    )

    procedure_id = fields.Many2one(
        'workshop.procedure',
        string='Procedimiento',
        required=True,
        ondelete='restrict',
        index=True,
    )
    version_number = fields.Integer(
        string='Número de versión',
        required=True,
        readonly=True,
        copy=False,
    )
    state = fields.Selection(
        [
            ('preparation', 'En preparación'),
        ],
        string='Estado',
        required=True,
        default='preparation',
        copy=False,
    )
    change_summary = fields.Text(
        string='Resumen de cambios',
    )

    def write(self, vals):
        if 'version_number' in vals:
            if any(
                version.version_number != vals['version_number']
                for version in self
            ):
                raise UserError(
                    'No se puede modificar el número de una versión existente.'
                )

        if 'procedure_id' in vals:
            if any(
                version.procedure_id.id != vals['procedure_id']
                for version in self
            ):
                raise UserError(
                    'No se puede cambiar el procedimiento propietario '
                    'de una versión existente.'
                )

        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        procedure_ids = sorted({
            vals['procedure_id']
            for vals in vals_list
            if vals.get('procedure_id')
        })

        # Serializar la asignación de versiones por procedimiento.
        for procedure_id in procedure_ids:
            self.env.cr.execute(
                """
                SELECT id
                FROM workshop_procedure
                WHERE id = %s
                FOR UPDATE
                """,
                [procedure_id],
            )

        next_numbers = {}
        for procedure_id in procedure_ids:
            self.env.cr.execute(
                """
                SELECT COALESCE(MAX(version_number), 0)
                FROM workshop_procedure_version
                WHERE procedure_id = %s
                """,
                [procedure_id],
            )
            next_numbers[procedure_id] = self.env.cr.fetchone()[0] + 1

        for vals in vals_list:
            procedure_id = vals.get('procedure_id')
            if procedure_id:
                vals['version_number'] = next_numbers[procedure_id]
                next_numbers[procedure_id] += 1

        return super().create(vals_list)
