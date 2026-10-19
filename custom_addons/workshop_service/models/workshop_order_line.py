"""Líneas ejecutables de una orden de trabajo."""
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .workshop_order import LINE_LOCKED_STATES
from .workshop_procedure import LINE_TYPES, VALUATION_METHODS


class WorkshopOrderLine(models.Model):
    """Elemento aplicado a una orden: conserva su procedencia y registra lo real.

    Los datos copiados del procedimiento son una instantánea: los cambios
    posteriores en la plantilla no los actualizan. Las cantidades previstas y
    las reales se mantienen separadas. Registrar una línea NO genera
    movimientos de inventario ni cargos comerciales (fases posteriores).
    """

    _name = 'workshop.order.line'
    _description = 'Línea ejecutable de la orden de trabajo'
    _order = 'order_id, sequence, id'

    _quantities_not_negative = models.Constraint(
        'CHECK(planned_quantity >= 0 AND actual_quantity >= 0 AND actual_minutes >= 0)',
        'Las cantidades y los tiempos no pueden ser negativos.',
    )

    order_id = fields.Many2one(
        'workshop.order',
        string='Orden',
        required=True,
        ondelete='cascade',
        index=True,
    )
    procedure_application_id = fields.Many2one(
        'workshop.order.procedure',
        string='Aplicación de procedimiento',
        ondelete='cascade',
        index=True,
        help='Vacío en las líneas manuales.',
    )
    source_procedure_line_id = fields.Many2one(
        'workshop.procedure.line',
        string='Línea de procedencia',
        ondelete='set null',
    )
    is_manual = fields.Boolean(
        string='Línea manual',
        compute='_compute_is_manual',
        store=True,
    )
    sequence = fields.Integer(string='Secuencia', default=10)
    line_type = fields.Selection(
        LINE_TYPES,
        string='Tipo',
        required=True,
        default='operation',
    )
    name = fields.Char(string='Descripción', required=True)
    description = fields.Text(string='Instrucciones')
    required = fields.Boolean(string='Obligatoria', default=False)
    is_blocking = fields.Boolean(string='Bloqueante')
    product_category_id = fields.Many2one(
        'product.category',
        string='Categoría de producto',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto concreto',
        help='Producto realmente seleccionado o utilizado.',
    )
    alternative_product_ids = fields.Many2many(
        'product.product',
        'workshop_order_line_alt_product_rel',
        'line_id',
        'product_id',
        string='Alternativas autorizadas',
    )
    product_uom_id = fields.Many2one('uom.uom', string='Unidad de medida')
    planned_quantity = fields.Float(
        string='Cantidad prevista',
        digits=(16, 4),
    )
    actual_quantity = fields.Float(
        string='Cantidad real',
        digits=(16, 4),
        help='La define el técnico; puede diferir de la prevista, incluso superarla.',
    )
    estimated_minutes = fields.Float(string='Minutos estimados')
    actual_minutes = fields.Float(
        string='Minutos reales',
        help='Necesarios para servicios valorados por tiempo.',
    )
    valuation_method = fields.Selection(
        VALUATION_METHODS,
        string='Valoración',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='order_id.company_id.currency_id',
        readonly=True,
    )
    applied_unit_price = fields.Monetary(
        string='Precio unitario acordado',
        currency_field='currency_id',
        help='Precio congelado en la orden; no cambia si cambia el catálogo.',
    )
    state = fields.Selection(
        [
            ('pending', 'Pendiente'),
            ('done', 'Realizada'),
            ('not_applicable', 'No aplicable'),
        ],
        string='Estado',
        required=True,
        default='pending',
    )
    not_applicable_reason = fields.Text(string='Motivo de no aplicabilidad')

    # ------------------------------------------------------------------
    # Cómputos y validaciones
    # ------------------------------------------------------------------
    @api.depends('procedure_application_id')
    def _compute_is_manual(self):
        for line in self:
            line.is_manual = not line.procedure_application_id

    @api.constrains('state', 'not_applicable_reason')
    def _check_not_applicable_reason(self):
        for line in self:
            if line.state == 'not_applicable' and not (
                line.not_applicable_reason or ''
            ).strip():
                raise ValidationError(
                    f'Indique el motivo por el que la línea «{line.name}» '
                    'no aplica.'
                )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Completa unidad, categoría, descripción y precio desde el producto."""
        if self.product_id:
            if not self.product_uom_id:
                self.product_uom_id = self.product_id.uom_id
            if not self.product_category_id:
                self.product_category_id = self.product_id.categ_id
            if not self.name:
                self.name = self.product_id.display_name
            if not self.applied_unit_price:
                self.applied_unit_price = self.product_id.lst_price

    # ------------------------------------------------------------------
    # Escritura protegida
    # ------------------------------------------------------------------
    @api.model
    def _ensure_orders_open(self, orders):
        """Rechaza cambios en líneas de órdenes ya terminadas o cerradas."""
        locked = orders.filtered(lambda o: o.state in LINE_LOCKED_STATES)
        if locked:
            raise UserError(
                f'No se pueden modificar las líneas de la orden '
                f'{locked[0].name} en su estado actual.'
            )

    @api.model_create_multi
    def create(self, vals_list):
        orders = self.env['workshop.order'].browse(
            [vals['order_id'] for vals in vals_list if vals.get('order_id')]
        )
        self._ensure_orders_open(orders)
        return super().create(vals_list)

    def write(self, vals):
        for fname in ('order_id', 'procedure_application_id', 'source_procedure_line_id'):
            if fname in vals and any(
                line[fname].id != vals[fname] for line in self
            ):
                raise UserError('No se puede cambiar el origen de una línea.')
        self._ensure_orders_open(self.order_id)
        return super().write(vals)

    def unlink(self):
        self._ensure_orders_open(self.order_id)
        return super().unlink()

    # ------------------------------------------------------------------
    # Acciones de ejecución
    # ------------------------------------------------------------------
    def action_mark_done(self):
        """Marca las líneas como realizadas."""
        for line in self:
            if line.valuation_method == 'hourly' and not line.actual_minutes:
                raise UserError(
                    f'Registre los minutos reales de «{line.name}» antes de '
                    'marcarla como realizada.'
                )
        self.write({'state': 'done'})
        return True

    def action_mark_not_applicable(self):
        """Marca las líneas como no aplicables (exige indicar el motivo)."""
        self.write({'state': 'not_applicable'})
        return True

    def action_mark_pending(self):
        """Devuelve las líneas a pendiente."""
        self.write({'state': 'pending'})
        return True
