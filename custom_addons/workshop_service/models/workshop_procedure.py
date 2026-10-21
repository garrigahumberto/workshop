from odoo import api, fields, models
from odoo.exceptions import UserError


class WorkshopProcedure(models.Model):
    _name = 'workshop.procedure'
    _description = 'Revisión de procedimiento'
    _order = 'code, revision desc'

    _code_revision_unique = models.Constraint(
        'UNIQUE(code, revision)',
        'La revisión debe ser única dentro del código del procedimiento.',
    )

    name = fields.Char(string='Servicio', required=True)
    code = fields.Char(string='Código base', required=True, index=True)
    revision = fields.Integer(
        string='Revisión',
        required=True,
        readonly=True,
        copy=False,
        default=1,
    )
    reference = fields.Char(
        string='Identificador',
        compute='_compute_reference',
    )
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('published', 'Publicado'),
            ('archived', 'Archivado'),
        ],
        string='Estado',
        required=True,
        default='draft',
        copy=False,
        index=True,
    )
    description = fields.Text(string='Descripción')
    change_summary = fields.Text(string='Resumen del cambio')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
    )
    published_by_id = fields.Many2one(
        'res.users',
        string='Publicado por',
        readonly=True,
        copy=False,
    )
    published_at = fields.Datetime(string='Publicado el', readonly=True, copy=False)
    archived_by_id = fields.Many2one(
        'res.users',
        string='Archivado por',
        readonly=True,
        copy=False,
    )
    archived_at = fields.Datetime(string='Archivado el', readonly=True, copy=False)
    line_ids = fields.One2many(
        'workshop.procedure.line',
        'procedure_id',
        string='Contenido del procedimiento',
    )

    @api.depends('code', 'revision')
    def _compute_reference(self):
        for procedure in self:
            procedure.reference = f'{procedure.code}-{procedure.revision:03d}'

    @api.model_create_multi
    def create(self, vals_list):
        codes = sorted({vals.get('code') for vals in vals_list if vals.get('code')})
        for code in codes:
            self.env.cr.execute(
                'SELECT pg_advisory_xact_lock(hashtext(%s))',
                [code],
            )
        next_revisions = {}
        for code in codes:
            self.env.cr.execute(
                'SELECT COALESCE(MAX(revision), 0) FROM workshop_procedure WHERE code = %s',
                [code],
            )
            next_revisions[code] = self.env.cr.fetchone()[0] + 1
        for vals in vals_list:
            code = vals.get('code')
            if code:
                vals['revision'] = next_revisions[code]
                next_revisions[code] += 1
        return super().create(vals_list)

    def write(self, vals):
        if {'code', 'revision'} & vals.keys():
            raise UserError('El código y la revisión de un procedimiento son inmutables.')
        if any(procedure.state != 'draft' for procedure in self):
            raise UserError(
                'Una revisión publicada o archivada no se puede editar. '
                'Cree una revisión nueva para cambiar el servicio.'
            )
        if {'state', 'active', 'published_by_id', 'published_at',
                'archived_by_id', 'archived_at'} & vals.keys():
            raise UserError('Use las acciones del procedimiento para cambiar su estado.')
        return super().write(vals)

    def action_publish(self):
        if not self.env.user.has_group(
            'workshop_service.group_workshop_procedure_manager'
        ) and not self.env.user.has_group('workshop_service.group_workshop_manager'):
            raise UserError('No tiene permiso para publicar procedimientos.')
        for procedure in self:
            if procedure.state != 'draft':
                raise UserError('Solo se pueden publicar revisiones en borrador.')
            latest_revision = self.with_context(active_test=False).search(
                [('code', '=', procedure.code)],
                order='revision desc',
                limit=1,
            )
            if latest_revision != procedure:
                raise UserError(
                    'Solo se puede publicar la revisión más reciente del procedimiento.'
                )
            previous_revisions = self.search([
                ('code', '=', procedure.code),
                ('state', '=', 'published'),
                ('revision', '<', procedure.revision),
            ])
            for previous in previous_revisions:
                super(WorkshopProcedure, previous).write({
                    'state': 'archived',
                    'active': False,
                    'archived_by_id': self.env.user.id,
                    'archived_at': fields.Datetime.now(),
                })
            super(WorkshopProcedure, procedure).write({
                'state': 'published',
                'published_by_id': self.env.user.id,
                'published_at': fields.Datetime.now(),
            })
        return True

    def action_create_revision(self):
        self.ensure_one()
        if self.state != 'published':
            raise UserError('Solo se puede crear una revisión desde una publicada.')
        new_revision = self.copy({
            'state': 'draft',
            'change_summary': False,
            'published_by_id': False,
            'published_at': False,
            'archived_by_id': False,
            'archived_at': False,
            'active': True,
        })
        new_revision.change_summary = f'Revisión basada en {self.reference}'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nueva revisión',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': new_revision.id,
            'target': 'current',
        }

    def copy(self, default=None):
        self.ensure_one()
        values = dict(default or {})
        values.setdefault('code', self.code)
        values.setdefault('revision', 0)
        values.setdefault('state', 'draft')
        values['line_ids'] = [
            (0, 0, {
                'sequence': line.sequence,
                'line_type': line.line_type,
                'name': line.name,
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'uom_id': line.uom_id.id,
                'optional': line.optional,
            })
            for line in self.line_ids
        ]
        return super().copy(values)

    def action_archive(self):
        if not self.env.user.has_group('workshop_service.group_workshop_manager'):
            raise UserError('Solo gerencia puede archivar procedimientos.')
        for procedure in self:
            if procedure.state != 'published':
                raise UserError('Solo se pueden archivar procedimientos publicados.')
            super(WorkshopProcedure, procedure).write({
                'state': 'archived',
                'active': False,
                'archived_by_id': self.env.user.id,
                'archived_at': fields.Datetime.now(),
            })
        return True
