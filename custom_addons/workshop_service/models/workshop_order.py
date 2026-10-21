from datetime import datetime, time, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class WorkshopOrder(models.Model):
    _name = 'workshop.order'
    _description = 'Orden de servicio'
    _order = 'request_date desc, id desc'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('workshop.order') or 'New'
                )
            vals.setdefault('received_by_id', self.env.user.id)
            if not vals.get('location_id'):
                raise UserError('Seleccione la tienda o taller responsable.')
        orders = super().create(vals_list)
        orders._record_event('opened')
        return orders

    @api.constrains('origin', 'location_id', 'company_id')
    def _check_location(self):
        for order in self:
            if not order.location_id:
                continue
            if (
                order.location_id.location_type != order.origin
                or order.location_id.company_id != order.company_id
            ):
                raise ValidationError(
                    'La ubicación debe corresponder al origen y compañía de la orden.'
                )

    name = fields.Char(
        string='Número de orden',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one('res.partner', string='Cliente')
    origin = fields.Selection(
        [
            ('store', 'Tienda'),
            ('workshop', 'Taller'),
        ],
        string='Origen',
        required=False,
        default='workshop',
    )
    location_id = fields.Many2one(
        'workshop.location',
        string='Ubicación responsable',
        required=False,
        ondelete='restrict',
        domain="[('location_type', '=', origin), ('company_id', '=', company_id)]",
    )
    received_by_id = fields.Many2one(
        'res.users',
        string='Atendido por',
        required=False,
    )
    technician_id = fields.Many2one('res.users', string='Técnico principal')
    equipment_name = fields.Char(string='Equipo o artículo')
    equipment_identifier = fields.Char(string='Identificador')
    state = fields.Selection(
        [
            ('open', 'Abierta'),
            ('closed', 'Cerrada'),
            ('cancelled', 'Cancelada'),
        ],
        string='Estado',
        default='open',
        required=True,
        readonly=True,
        copy=False,
        index=True,
    )
    active = fields.Boolean(string='Activa', default=True)
    request_date = fields.Datetime(
        string='Fecha de recepción',
        required=True,
        default=fields.Datetime.now,
        readonly=True,
    )
    promised_date = fields.Datetime(string='Fecha prometida')
    budget_amount = fields.Monetary(string='Presupuesto comunicado')
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
    )
    description = fields.Text(string='Solicitud / notas de recepción')
    diagnosis = fields.Text(string='Diagnóstico')
    work_summary = fields.Text(string='Trabajo realizado')
    cancellation_reason = fields.Char(string='Motivo de cancelación')
    reopen_reason = fields.Char(string='Motivo de reapertura')
    follow_up_type = fields.Selection(
        [
            ('warranty', 'Garantía'),
            ('rework', 'Retrabajo'),
        ],
        string='Tipo de reapertura',
    )
    closed_at = fields.Datetime(string='Último cierre', readonly=True, copy=False)
    cancelled_at = fields.Datetime(string='Cancelada el', readonly=True, copy=False)
    event_ids = fields.One2many(
        'workshop.order.event',
        'order_id',
        string='Historial',
        readonly=True,
    )
    line_ids = fields.One2many(
        'workshop.order.line',
        'order_id',
        string='Servicios y materiales',
    )
    application_ids = fields.One2many(
        'workshop.order.procedure',
        'order_id',
        string='Procedimientos aplicados',
        readonly=True,
    )
    procedure_to_apply_id = fields.Many2one(
        'workshop.procedure',
        string='Aplicar procedimiento',
        domain="[('state', '=', 'published'), ('active', '=', True), "
               "('company_id', '=', company_id)]",
    )
    sale_order_ids = fields.Many2many(
        'sale.order',
        'workshop_order_sale_order_rel',
        'workshop_order_id',
        'sale_order_id',
        string='Pedidos de venta relacionados',
    )

    @api.model
    def get_dashboard_data(
        self,
        date_from=False,
        date_to=False,
        location_id=False,
    ):
        if not self.has_access('read'):
            return {'error': _('No tienes permiso para consultar órdenes de trabajo.')}

        Location = self.env['workshop.location']
        if not Location.has_access('read'):
            return {'error': _('No tienes permiso para consultar las ubicaciones.')}

        if date_from is False and date_to is False:
            date_from = date_to = fields.Date.context_today(self)
        elif not date_from or not date_to:
            raise UserError(_('Selecciona una fecha inicial y una fecha final.'))

        try:
            start_date = fields.Date.to_date(date_from)
            end_date = fields.Date.to_date(date_to)
        except (TypeError, ValueError):
            raise UserError(_('Selecciona un rango de fechas válido.'))
        if not start_date or not end_date:
            raise UserError(_('Selecciona un rango de fechas válido.'))
        if start_date > end_date:
            raise UserError(
                _('La fecha inicial no puede ser posterior a la fecha final.')
            )

        locations = Location.search([
            ('company_id', '=', self.env.company.id),
            ('location_type', '=', 'workshop'),
            ('active', '=', True),
        ])
        if location_id:
            if (
                isinstance(location_id, bool)
                or not isinstance(location_id, int)
                or location_id not in locations.ids
            ):
                raise UserError(_('El taller seleccionado no está disponible.'))

        user_timezone = pytz.timezone(
            self.env.context.get('tz') or self.env.user.tz or 'UTC'
        )
        start_datetime = user_timezone.localize(
            datetime.combine(start_date, time.min)
        ).astimezone(pytz.UTC).replace(tzinfo=None)
        end_datetime = user_timezone.localize(
            datetime.combine(end_date + timedelta(days=1), time.min)
        ).astimezone(pytz.UTC).replace(tzinfo=None)

        base_domain = [
            ('active', '=', True),
            ('company_id', '=', self.env.company.id),
            ('location_id', 'in', locations.ids),
        ]
        if location_id:
            base_domain.append(('location_id', '=', location_id))

        period_domain = [
            ('request_date', '>=', start_datetime),
            ('request_date', '<', end_datetime),
        ]
        overdue_domain = [
            ('state', '=', 'open'),
            ('promised_date', '!=', False),
            ('promised_date', '<', fields.Datetime.now()),
        ]

        def counts_by_location(domain):
            return dict(self.read_group(
                domain,
                ['location_id'],
                ['__count'],
            ))

        received_counts = counts_by_location(base_domain + period_domain)
        open_counts = counts_by_location(
            base_domain + [('state', '=', 'open')]
        )
        overdue_counts = counts_by_location(base_domain + overdue_domain)

        metrics = {
            'total': self.search_count(base_domain + period_domain),
            'open': self.search_count(
                base_domain + period_domain + [('state', '=', 'open')]
            ),
            'completed': self.search_count(base_domain + [
                ('state', '=', 'closed'),
                ('closed_at', '>=', start_datetime),
                ('closed_at', '<', end_datetime),
            ]),
            'pending': self.search_count(base_domain + overdue_domain),
        }

        recent_orders = self.search(
            base_domain + period_domain,
            order='request_date desc, id desc',
            limit=8,
        )
        state_labels = {
            'open': _('Abierta'),
            'closed': _('Cerrada'),
            'cancelled': _('Cancelada'),
        }

        return {
            'metrics': metrics,
            'locations': [
                {
                    'id': location.id,
                    'name': location.name,
                    'orders': received_counts.get(location.id, 0),
                    'open': open_counts.get(location.id, 0),
                    'overdue': overdue_counts.get(location.id, 0),
                }
                for location in locations
            ],
            'recent_orders': [
                {
                    'id': order.id,
                    'name': order.name,
                    'partner': order.partner_id.display_name or _('Cliente no identificado'),
                    'equipment': order.equipment_name or _('Artículo no especificado'),
                    'location': order.location_id.name,
                    'state': state_labels[order.state],
                    'request_date': fields.Datetime.context_timestamp(
                        self, order.request_date
                    ).strftime('%d/%m/%Y %H:%M'),
                }
                for order in recent_orders
            ],
            'can_create_order': self.has_access('create'),
            'can_read_orders': True,
            'can_manage_locations': self.env.user.has_group(
                'workshop_service.group_workshop_manager'
            ),
        }

    def write(self, vals):
        if 'state' in vals:
            raise UserError(
                'El estado solo puede cambiarse mediante las acciones de la orden.'
            )
        if {'name', 'request_date', 'closed_at', 'cancelled_at', 'active'} & vals.keys():
            raise UserError(
                'Los identificadores, fechas de auditoría y archivo se gestionan mediante acciones.'
            )
        if any(order.state != 'open' for order in self) and vals:
            reopen_fields = {'reopen_reason', 'follow_up_type'}
            if (
                any(order.state != 'closed' for order in self)
                or vals.keys() - reopen_fields
            ):
                raise UserError('Reabra la orden antes de modificar sus datos.')
        return super().write(vals)

    def unlink(self):
        raise UserError(
            'Las órdenes no se eliminan; cancele o archive la orden para conservar su historial.'
        )

    def _record_event(self, event_type, reason=None, follow_up_type=None):
        self.env['workshop.order.event'].sudo().create([
            {
                'order_id': order.id,
                'event_type': event_type,
                'reason': reason,
                'follow_up_type': follow_up_type,
                'user_id': self.env.user.id,
            }
            for order in self
        ])

    def action_close(self):
        for order in self:
            if order.state != 'open':
                raise UserError('Solo se puede cerrar una orden abierta.')
            super(WorkshopOrder, order).write({
                'state': 'closed',
                'closed_at': fields.Datetime.now(),
            })
            order._record_event('closed')
        return True

    def action_cancel(self):
        for order in self:
            if order.state != 'open':
                raise UserError('Solo se puede cancelar una orden abierta.')
            reason = (order.cancellation_reason or '').strip()
            if not reason:
                raise UserError('Indique brevemente el motivo de cancelación.')
            super(WorkshopOrder, order).write({
                'state': 'cancelled',
                'cancelled_at': fields.Datetime.now(),
            })
            order._record_event('cancelled', reason=reason)
        return True

    def action_reopen(self):
        for order in self:
            if order.state != 'closed':
                raise UserError('Solo se puede reabrir una orden cerrada.')
            reason = (order.reopen_reason or '').strip()
            if not reason or not order.follow_up_type:
                raise UserError(
                    'Indique el motivo y si la reapertura es por garantía o retrabajo.'
                )
            follow_up_type = order.follow_up_type
            super(WorkshopOrder, order).write({
                'state': 'open',
                'reopen_reason': False,
                'follow_up_type': False,
            })
            order._record_event(
                'reopened',
                reason=reason,
                follow_up_type=follow_up_type,
            )
        return True

    def action_archive(self):
        if not self.env.user.has_group('workshop_service.group_workshop_manager'):
            raise UserError('Solo gerencia puede archivar órdenes.')
        return super().write({'active': False})

    def action_unarchive(self):
        if not self.env.user.has_group('workshop_service.group_workshop_manager'):
            raise UserError('Solo gerencia puede restaurar órdenes archivadas.')
        return super().write({'active': True})

    def action_apply_procedure(self):
        for order in self:
            if order.state != 'open':
                raise UserError('Solo se pueden aplicar procedimientos a órdenes abiertas.')
            procedure = order.procedure_to_apply_id
            if not procedure or procedure.state != 'published':
                raise UserError('Seleccione un procedimiento publicado.')
            latest_revision = self.env['workshop.procedure'].with_context(
                active_test=False
            ).search(
                [
                    ('code', '=', procedure.code),
                    ('state', '=', 'published'),
                    ('active', '=', True),
                ],
                order='revision desc',
                limit=1,
            )
            if (
                procedure.company_id != order.company_id
                or latest_revision != procedure
            ):
                raise UserError(
                    'Seleccione la revisión vigente del procedimiento para esta compañía.'
                )
            application = self.env['workshop.order.procedure'].create({
                'order_id': order.id,
                'procedure_id': procedure.id,
            })
            self.env['workshop.order.line'].create([
                {
                    'order_id': order.id,
                    'application_id': application.id,
                    'procedure_line_id': line.id,
                    'line_type': line.line_type,
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'uom_id': line.uom_id.id,
                    'planned_quantity': line.quantity,
                    'actual_quantity': line.quantity,
                    'state': 'planned',
                    'performed_by_id': (
                        self.env.user.id if line.line_type == 'labor' else False
                    ),
                }
                for line in procedure.line_ids
            ])
            order.procedure_to_apply_id = False
        return True


class WorkshopOrderProcedure(models.Model):
    _name = 'workshop.order.procedure'
    _description = 'Procedimiento aplicado a una orden'
    _order = 'applied_at, id'

    order_id = fields.Many2one(
        'workshop.order',
        string='Orden',
        required=True,
        ondelete='restrict',
        index=True,
    )
    procedure_id = fields.Many2one(
        'workshop.procedure',
        string='Revisión de procedimiento',
        required=True,
        ondelete='restrict',
    )
    procedure_name = fields.Char(string='Nombre aplicado', required=True)
    procedure_code = fields.Char(string='Código aplicado', required=True)
    procedure_revision = fields.Integer(string='Revisión aplicada', required=True)
    applied_by_id = fields.Many2one(
        'res.users',
        string='Aplicado por',
        required=True,
        default=lambda self: self.env.user,
    )
    applied_at = fields.Datetime(
        string='Aplicado el',
        required=True,
        default=fields.Datetime.now,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            procedure = self.env['workshop.procedure'].browse(
                vals.get('procedure_id')
            )
            if not procedure or procedure.state != 'published':
                raise UserError('Solo se pueden aplicar procedimientos publicados.')
            order = self.env['workshop.order'].browse(vals.get('order_id'))
            if order.state != 'open':
                raise UserError('Solo se aplican procedimientos a órdenes abiertas.')
            vals.update({
                'procedure_name': procedure.name,
                'procedure_code': procedure.code,
                'procedure_revision': procedure.revision,
            })
        return super().create(vals_list)

    def write(self, vals):
        if any(order.state != 'open' for order in self.mapped('order_id')):
            raise UserError('Reabra la orden antes de modificar procedimientos aplicados.')
        if {'procedure_id', 'procedure_name', 'procedure_code', 'procedure_revision'} & vals.keys():
            raise UserError('La revisión aplicada a una orden es inmutable.')
        if 'order_id' in vals and any(
            order.state != 'open'
            for order in self.env['workshop.order'].browse(vals['order_id'])
        ):
            raise UserError('Los procedimientos solo se mueven a órdenes abiertas.')
        return super().write(vals)

    def unlink(self):
        if any(order.state != 'open' for order in self.mapped('order_id')):
            raise UserError('Reabra la orden antes de modificar procedimientos aplicados.')
        return super().unlink()


class WorkshopOrderEvent(models.Model):
    _name = 'workshop.order.event'
    _description = 'Evento de historial de orden'
    _order = 'create_date, id'

    order_id = fields.Many2one(
        'workshop.order',
        string='Orden',
        required=True,
        ondelete='restrict',
        index=True,
    )
    event_type = fields.Selection(
        [
            ('opened', 'Recepción'),
            ('closed', 'Cierre'),
            ('cancelled', 'Cancelación'),
            ('reopened', 'Reapertura'),
        ],
        string='Evento',
        required=True,
    )
    reason = fields.Char(string='Motivo')
    follow_up_type = fields.Selection(
        [
            ('warranty', 'Garantía'),
            ('rework', 'Retrabajo'),
        ],
        string='Tipo de reapertura',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        required=True,
        default=lambda self: self.env.user,
    )
    event_date = fields.Datetime(
        string='Fecha',
        required=True,
        default=fields.Datetime.now,
    )

    def write(self, vals):
        raise UserError('El historial de la orden no se puede modificar.')

    def unlink(self):
        raise UserError('El historial de la orden no se puede eliminar.')
