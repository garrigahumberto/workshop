from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class WorkshopProcedureLine(models.Model):
    _name = 'workshop.procedure.line'
    _description = 'Línea de procedimiento'
    _order = 'sequence, id'

    procedure_id = fields.Many2one(
        'workshop.procedure',
        string='Procedimiento',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    line_type = fields.Selection(
        [
            ('component', 'Componente'),
            ('consumable', 'Material gastable'),
            ('labor', 'Mano de obra'),
            ('operation', 'Operación'),
        ],
        string='Tipo',
        required=True,
        default='operation',
    )
    name = fields.Char(string='Descripción', required=True)
    product_id = fields.Many2one('product.product', string='Producto sugerido')
    quantity = fields.Float(string='Cantidad de referencia', default=1.0)
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unidad',
        default=lambda self: self.env.ref(
            'uom.product_uom_unit', raise_if_not_found=False
        ),
    )
    optional = fields.Boolean(string='Opcional')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id

    @api.constrains('quantity', 'line_type', 'product_id', 'uom_id')
    def _check_quantity(self):
        for line in self:
            if line.line_type in {'component', 'consumable', 'labor'} and line.quantity < 0:
                raise ValidationError('La cantidad de referencia no puede ser negativa.')
            if (
                line.product_id
                and line.uom_id
                and not line.product_id.uom_id._has_common_reference(line.uom_id)
            ):
                raise ValidationError(
                    'La unidad debe ser compatible con la unidad del producto.'
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            procedure = self.env['workshop.procedure'].browse(vals.get('procedure_id'))
            if procedure.state != 'draft':
                raise UserError('Solo se editan líneas de procedimientos en borrador.')
        return super().create(vals_list)

    def write(self, vals):
        if any(line.procedure_id.state != 'draft' for line in self):
            raise UserError('Las líneas de un procedimiento publicado son inmutables.')
        return super().write(vals)

    def unlink(self):
        if any(line.procedure_id.state != 'draft' for line in self):
            raise UserError('Las líneas de un procedimiento publicado son inmutables.')
        return super().unlink()


class WorkshopOrderLine(models.Model):
    _name = 'workshop.order.line'
    _description = 'Servicio o material de una orden'
    _order = 'sequence, id'

    order_id = fields.Many2one(
        'workshop.order',
        string='Orden',
        required=True,
        ondelete='restrict',
        index=True,
    )
    application_id = fields.Many2one(
        'workshop.order.procedure',
        string='Procedimiento aplicado',
        ondelete='restrict',
    )
    procedure_line_id = fields.Many2one(
        'workshop.procedure.line',
        string='Línea de origen',
        ondelete='restrict',
    )
    sequence = fields.Integer(default=10)
    line_type = fields.Selection(
        [
            ('component', 'Componente'),
            ('consumable', 'Material gastable'),
            ('labor', 'Mano de obra'),
            ('operation', 'Operación'),
        ],
        string='Tipo',
        required=True,
        default='operation',
    )
    name = fields.Char(string='Descripción', required=True)
    product_id = fields.Many2one('product.product', string='Producto')
    uom_id = fields.Many2one('uom.uom', string='Unidad')
    planned_quantity = fields.Float(string='Cantidad de referencia')
    actual_quantity = fields.Float(string='Cantidad real')
    state = fields.Selection(
        [
            ('planned', 'Pendiente'),
            ('done', 'Realizado'),
            ('not_applicable', 'No aplica'),
        ],
        string='Ejecución',
        required=True,
        default='planned',
    )
    performed_by_id = fields.Many2one(
        'res.users',
        string='Realizado por',
    )
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='Línea de venta relacionada',
        ondelete='restrict',
    )
    stock_move_id = fields.Many2one(
        'stock.move',
        string='Movimiento de inventario relacionado',
        ondelete='restrict',
    )
    allocation_id = fields.Many2one(
        'workshop.consumable.allocation',
        string='Asignación de gastables',
        ondelete='restrict',
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id

    @api.onchange('sale_order_line_id')
    def _onchange_sale_order_line_id(self):
        if self.sale_order_line_id:
            self.product_id = self.sale_order_line_id.product_id
            self.uom_id = self.sale_order_line_id.product_uom_id

    @api.onchange('stock_move_id')
    def _onchange_stock_move_id(self):
        if self.stock_move_id:
            self.product_id = self.stock_move_id.product_id
            self.uom_id = self.stock_move_id.uom_id

    @api.onchange('allocation_id')
    def _onchange_allocation_id(self):
        if self.allocation_id:
            self.line_type = 'consumable'
            self.product_id = self.allocation_id.product_id
            self.uom_id = self.allocation_id.uom_id

    @api.constrains(
        'order_id',
        'application_id',
        'product_id',
        'line_type',
        'uom_id',
        'sale_order_line_id',
        'stock_move_id',
        'allocation_id',
    )
    def _check_linked_product(self):
        for line in self:
            if line.application_id and line.application_id.order_id != line.order_id:
                raise ValidationError(
                    'El procedimiento aplicado debe pertenecer a la misma orden.'
                )
            if (
                line.product_id
                and line.uom_id
                and not line.product_id.uom_id._has_common_reference(line.uom_id)
            ):
                raise ValidationError(
                    'La unidad debe ser compatible con la unidad del producto.'
                )
            if (
                line.sale_order_line_id
                and line.sale_order_line_id.product_id != line.product_id
            ):
                raise ValidationError(
                    'El producto de la línea debe coincidir con la línea de venta relacionada.'
                )
            if (
                line.stock_move_id
                and line.stock_move_id.product_id != line.product_id
            ):
                raise ValidationError(
                    'El producto de la línea debe coincidir con el movimiento relacionado.'
                )
            if line.stock_move_id and line.stock_move_id.state != 'done':
                raise ValidationError(
                    'La línea debe enlazarse a un movimiento de inventario validado.'
                )
            if (
                line.stock_move_id
                and line.stock_move_id.company_id != line.order_id.company_id
            ):
                raise ValidationError(
                    'El movimiento debe pertenecer a la misma compañía que la orden.'
                )
            if (
                line.allocation_id
                and line.allocation_id.product_id != line.product_id
            ):
                raise ValidationError(
                    'El producto debe coincidir con la asignación de gastables.'
                )
            if (
                line.allocation_id
                and line.allocation_id.workshop_location_id != line.order_id.location_id
            ):
                raise ValidationError(
                    'La asignación debe pertenecer al taller responsable de la orden.'
                )
            if line.allocation_id and line.line_type != 'consumable':
                raise ValidationError(
                    'Una asignación de material gastable requiere una línea de tipo gastable.'
                )
            if (
                line.sale_order_line_id
                and line.sale_order_line_id.order_id.company_id != line.order_id.company_id
            ):
                raise ValidationError(
                    'La venta debe pertenecer a la misma compañía que la orden.'
                )

    @api.constrains('actual_quantity', 'planned_quantity')
    def _check_quantities(self):
        for line in self:
            if line.actual_quantity < 0 or line.planned_quantity < 0:
                raise ValidationError('Las cantidades no pueden ser negativas.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            order = self.env['workshop.order'].browse(vals.get('order_id'))
            if order.state != 'open':
                raise UserError('Solo se pueden añadir líneas a órdenes abiertas.')
            sale_line = self.env['sale.order.line'].browse(
                vals.get('sale_order_line_id')
            )
            stock_move = self.env['stock.move'].browse(vals.get('stock_move_id'))
            allocation = self.env[
                'workshop.consumable.allocation'
            ].browse(vals.get('allocation_id'))
            if sale_line:
                vals.setdefault('line_type', 'component')
                vals.setdefault('product_id', sale_line.product_id.id)
                vals.setdefault('uom_id', sale_line.product_uom_id.id)
            elif stock_move:
                vals.setdefault('line_type', 'component')
                vals.setdefault('product_id', stock_move.product_id.id)
                vals.setdefault('uom_id', stock_move.uom_id.id)
            elif allocation:
                vals.setdefault('line_type', 'consumable')
                vals.setdefault('product_id', allocation.product_id.id)
                vals.setdefault('uom_id', allocation.uom_id.id)
            if vals.get('line_type') == 'labor':
                vals.setdefault('performed_by_id', self.env.user.id)
            application_id = vals.get('application_id')
            if application_id and self.env[
                'workshop.order.procedure'
            ].browse(application_id).order_id != order:
                raise ValidationError(
                    'El procedimiento aplicado debe pertenecer a la misma orden.'
                )
        return super().create(vals_list)

    def write(self, vals):
        orders = self.mapped('order_id')
        if any(order.state != 'open' for order in orders):
            raise UserError('Reabra la orden antes de modificar sus líneas.')
        if 'order_id' in vals and any(
            order.state != 'open'
            for order in self.env['workshop.order'].browse(vals['order_id'])
        ):
            raise UserError('Las líneas solo se pueden mover a órdenes abiertas.')
        if 'sale_order_line_id' in vals:
            sale_line = self.env['sale.order.line'].browse(vals['sale_order_line_id'])
            vals.setdefault('line_type', 'component')
            vals.setdefault('product_id', sale_line.product_id.id)
            vals.setdefault('uom_id', sale_line.product_uom_id.id)
        elif 'stock_move_id' in vals:
            stock_move = self.env['stock.move'].browse(vals['stock_move_id'])
            vals.setdefault('line_type', 'component')
            vals.setdefault('product_id', stock_move.product_id.id)
            vals.setdefault('uom_id', stock_move.uom_id.id)
        elif 'allocation_id' in vals:
            allocation = self.env[
                'workshop.consumable.allocation'
            ].browse(vals['allocation_id'])
            vals.setdefault('line_type', 'consumable')
            vals.setdefault('product_id', allocation.product_id.id)
            vals.setdefault('uom_id', allocation.uom_id.id)
        if vals.get('line_type') == 'labor' and 'performed_by_id' not in vals:
            vals['performed_by_id'] = self.env.user.id
        return super().write(vals)

    def unlink(self):
        if any(order.state != 'open' for order in self.mapped('order_id')):
            raise UserError('Reabra la orden antes de modificar sus líneas.')
        return super().unlink()
