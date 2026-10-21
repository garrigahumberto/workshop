from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WorkshopConsumableAllocation(models.Model):
    _name = 'workshop.consumable.allocation'
    _description = 'Asignación de material gastable a taller'
    _order = 'allocation_date desc, id desc'

    stock_move_id = fields.Many2one(
        'stock.move',
        string='Movimiento de transferencia',
        required=True,
        ondelete='restrict',
        index=True,
    )
    workshop_location_id = fields.Many2one(
        'workshop.location',
        string='Taller destinatario',
        required=True,
        ondelete='restrict',
        domain=[('location_type', '=', 'workshop')],
    )
    product_id = fields.Many2one(
        related='stock_move_id.product_id',
        string='Producto',
        store=True,
        readonly=True,
    )
    quantity = fields.Float(
        related='stock_move_id.quantity',
        string='Cantidad transferida',
        store=True,
        readonly=True,
    )
    uom_id = fields.Many2one(
        related='stock_move_id.uom_id',
        string='Unidad',
        store=True,
        readonly=True,
    )
    allocation_date = fields.Datetime(
        related='stock_move_id.date',
        string='Fecha del movimiento',
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        related='stock_move_id.company_id',
        string='Compañía',
        store=True,
        readonly=True,
    )

    _stock_move_unique = models.Constraint(
        'UNIQUE(stock_move_id)',
        'Cada movimiento solo puede asignarse una vez a un taller.',
    )

    @api.constrains('stock_move_id', 'workshop_location_id')
    def _check_transfer(self):
        for allocation in self:
            move = allocation.stock_move_id
            stock_location = allocation.workshop_location_id.stock_location_id
            if move.state != 'done':
                raise ValidationError(
                    'La asignación debe referenciar una transferencia validada en Inventario.'
                )
            if move.quantity <= 0:
                raise ValidationError(
                    'La asignación debe referenciar una transferencia con cantidad positiva.'
                )
            if not stock_location:
                raise ValidationError(
                    'Configure la ubicación de inventario del taller antes de registrar asignaciones.'
                )
            if move.company_id != allocation.workshop_location_id.company_id:
                raise ValidationError(
                    'El movimiento y el taller deben pertenecer a la misma compañía.'
                )
            if move.location_dest_id != stock_location:
                raise ValidationError(
                    'El destino del movimiento no coincide con la ubicación de inventario del taller.'
                )

    def write(self, vals):
        if {'stock_move_id', 'workshop_location_id'} & vals.keys():
            raise ValidationError(
                'No cambie una asignación validada; corrija el movimiento en Inventario.'
            )
        return super().write(vals)

    def unlink(self):
        raise ValidationError(
            'Una asignación validada no se elimina; corrija el movimiento en Inventario.'
        )
