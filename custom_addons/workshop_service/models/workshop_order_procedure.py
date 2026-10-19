"""Aplicación de una versión de procedimiento a una orden de trabajo."""
from odoo import api, fields, models
from odoo.exceptions import UserError

from .workshop_order import APPLY_ALLOWED_STATES, LINE_LOCKED_STATES


class WorkshopOrderProcedure(models.Model):
    """Registra qué versión exacta de un procedimiento se aplicó a una orden.

    Al crearse genera las líneas ejecutables como copia de la versión, de modo
    que los cambios posteriores en la plantilla no alteran la orden. Los
    subprocedimientos se expanden en aplicaciones hijas que conservan la
    versión concreta referenciada.
    """

    _name = 'workshop.order.procedure'
    _description = 'Aplicación de procedimiento a una orden'
    _order = 'order_id, applied_at, id'

    order_id = fields.Many2one(
        'workshop.order',
        string='Orden',
        required=True,
        ondelete='cascade',
        index=True,
    )
    procedure_version_id = fields.Many2one(
        'workshop.procedure.version',
        string='Versión aplicada',
        required=True,
        ondelete='restrict',
        index=True,
    )
    procedure_id = fields.Many2one(
        'workshop.procedure',
        string='Procedimiento',
        related='procedure_version_id.procedure_id',
        store=True,
        readonly=True,
    )
    parent_application_id = fields.Many2one(
        'workshop.order.procedure',
        string='Aplicación de origen',
        ondelete='cascade',
        readonly=True,
        help='Si esta aplicación procede de un subprocedimiento expandido, '
             'indica la aplicación que lo contenía.',
    )
    applied_by = fields.Many2one(
        'res.users',
        string='Aplicado por',
        required=True,
        readonly=True,
        default=lambda self: self.env.user,
    )
    applied_at = fields.Datetime(
        string='Fecha de aplicación',
        required=True,
        readonly=True,
        default=fields.Datetime.now,
    )
    line_ids = fields.One2many(
        'workshop.order.line',
        'procedure_application_id',
        string='Líneas generadas',
    )

    # ------------------------------------------------------------------
    # Creación y generación de líneas
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        Order = self.env['workshop.order']
        Version = self.env['workshop.procedure.version']
        for vals in vals_list:
            order = Order.browse(vals.get('order_id'))
            version = Version.browse(vals.get('procedure_version_id'))
            if order and order.state not in APPLY_ALLOWED_STATES:
                raise UserError(
                    f'No se pueden aplicar procedimientos a la orden '
                    f'{order.name} en su estado actual.'
                )
            if version and version.state != 'published':
                raise UserError(
                    f'Solo se pueden aplicar versiones publicadas '
                    f'({version.display_name}).'
                )
        applications = super().create(vals_list)
        # Las aplicaciones hijas generan sus líneas desde la aplicación padre.
        for application in applications.filtered(
            lambda a: not a.parent_application_id
        ):
            application._generate_lines()
        return applications

    def _generate_lines(self, path=(), counter=None):
        """Copia las líneas de la versión aplicada a la orden.

        :param path: ids de versiones ya expandidas en esta rama (salvaguarda
            adicional frente a ciclos).
        :param counter: lista de un elemento con la siguiente secuencia.
        """
        self.ensure_one()
        version = self.procedure_version_id
        path = path + (version.id,)
        if counter is None:
            current = max(self.order_id.line_ids.mapped('sequence') or [0])
            counter = [current + 10]
        Line = self.env['workshop.order.line']
        for source in version.line_ids.sorted(lambda l: (l.sequence, l.id)):
            if source.line_type == 'subprocedure':
                sub_version = source.subprocedure_version_id
                if sub_version.id in path:
                    raise UserError(
                        f'Referencia circular detectada en '
                        f'{sub_version.display_name}.'
                    )
                if sub_version.state != 'published':
                    # SUPUESTO: una versión retirada no admite nuevas
                    # aplicaciones, tampoco como subprocedimiento.
                    raise UserError(
                        f'El subprocedimiento {sub_version.display_name} no '
                        'está publicado y no puede aplicarse.'
                    )
                child = self.create({
                    'order_id': self.order_id.id,
                    'procedure_version_id': sub_version.id,
                    'parent_application_id': self.id,
                })
                child._generate_lines(path, counter)
                continue
            Line.create(self._prepare_order_line_vals(source, counter[0]))
            counter[0] += 10

    def _prepare_order_line_vals(self, source, sequence):
        """Valores de la línea ejecutable a partir de una línea de la versión."""
        self.ensure_one()
        unit_price = 0.0
        if source.line_type == 'service_labor':
            unit_price = (
                source.reference_price
                if source.valuation_method == 'fixed'
                else source.reference_hourly_rate
            )
        return {
            'order_id': self.order_id.id,
            'procedure_application_id': self.id,
            'source_procedure_line_id': source.id,
            'sequence': sequence,
            'line_type': source.line_type,
            'name': source.name,
            'description': source.description,
            'required': source.required,
            'is_blocking': source.is_blocking,
            'product_id': source.product_id.id,
            'product_category_id': source.product_category_id.id,
            'product_uom_id': source.product_uom_id.id,
            'planned_quantity': source.quantity,
            'estimated_minutes': source.estimated_minutes,
            'valuation_method': source.valuation_method,
            'applied_unit_price': unit_price,
            'alternative_product_ids': [
                (6, 0, source.alternative_product_ids.ids)
            ],
        }

    # ------------------------------------------------------------------
    # Escritura protegida
    # ------------------------------------------------------------------
    def write(self, vals):
        for fname in ('order_id', 'procedure_version_id', 'parent_application_id'):
            if fname in vals and any(
                application[fname].id != vals[fname] for application in self
            ):
                raise UserError(
                    'No se puede cambiar la orden ni la versión de una '
                    'aplicación de procedimiento.'
                )
        return super().write(vals)

    def unlink(self):
        """Quita aplicaciones (y sus líneas) solo si no hay trabajo registrado."""
        to_remove = self
        pending = self
        while pending:
            pending = self.search(
                [('parent_application_id', 'in', pending.ids)]
            ) - to_remove
            to_remove |= pending
        for application in to_remove:
            if application.order_id.state in LINE_LOCKED_STATES:
                raise UserError(
                    f'No se pueden quitar procedimientos de la orden '
                    f'{application.order_id.name} en su estado actual.'
                )
            if application.line_ids.filtered(
                lambda l: l.state != 'pending'
                or l.actual_quantity
                or l.actual_minutes
            ):
                raise UserError(
                    'No se puede quitar un procedimiento con trabajo ya '
                    'registrado en sus líneas.'
                )
        to_remove.line_ids.unlink()
        return super(WorkshopOrderProcedure, to_remove).unlink()
