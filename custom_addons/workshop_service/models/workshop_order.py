"""Orden de trabajo: núcleo del flujo del taller.

El estado solo cambia mediante las acciones de este modelo, que validan en el
servidor las transiciones permitidas, los datos exigidos y los permisos. La
escritura directa de ``state`` se rechaza.
"""
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

GROUP_TECHNICIAN = 'workshop_service.group_workshop_technician'
GROUP_SALESPERSON = 'workshop_service.group_workshop_salesperson'
GROUP_SUPERVISOR = 'workshop_service.group_workshop_supervisor'

# Transiciones permitidas. SUPUESTO de la primera versión (la matriz definitiva
# de transiciones sigue pendiente de decisión funcional): flujo lineal, con
# cancelación posible hasta la entrega. Desde «presupuesto» se puede iniciar la
# reparación sin aprobación solo si el tipo de reparación no la exige.
STATE_TRANSITIONS = {
    'solicitud': ('diagnostico', 'cancelada'),
    'diagnostico': ('presupuesto', 'cancelada'),
    'presupuesto': ('aprobada', 'en_reparacion', 'cancelada'),
    'aprobada': ('en_reparacion', 'cancelada'),
    'en_reparacion': ('terminada', 'cancelada'),
    'terminada': ('entregada', 'cancelada'),
    'entregada': ('cerrada',),
    'cerrada': (),
    'cancelada': (),
}

# Estados en los que ya no se pueden alterar las líneas de la orden.
LINE_LOCKED_STATES = ('terminada', 'entregada', 'cerrada', 'cancelada')

# Estados en los que todavía se pueden aplicar procedimientos.
APPLY_ALLOWED_STATES = (
    'solicitud', 'diagnostico', 'presupuesto', 'aprobada', 'en_reparacion',
)


class WorkshopOrder(models.Model):
    _name = 'workshop.order'
    _description = 'Orden de trabajo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc, id desc'

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
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        tracking=True,
    )
    equipment_id = fields.Many2one(
        'workshop.equipment',
        string='Equipo',
        tracking=True,
    )
    repair_type_id = fields.Many2one(
        'workshop.repair.type',
        string='Tipo de reparación',
        tracking=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Técnico responsable',
        tracking=True,
    )
    priority = fields.Selection(
        [
            ('0', 'Normal'),
            ('1', 'Alta'),
            ('2', 'Urgente'),
        ],
        string='Prioridad',
        default='0',
        required=True,
        help='Solo afecta a la priorización operativa; no omite ningún control.',
    )
    state = fields.Selection(
        [
            ('solicitud', 'Solicitud'),
            ('diagnostico', 'Diagnóstico'),
            ('presupuesto', 'Presupuesto'),
            ('aprobada', 'Aprobada'),
            ('en_reparacion', 'En reparación'),
            ('terminada', 'Terminada'),
            ('entregada', 'Entregada'),
            ('cerrada', 'Cerrada'),
            ('cancelada', 'Cancelada'),
        ],
        string='Estado',
        default='solicitud',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )
    request_date = fields.Datetime(
        string='Fecha de recepción',
        required=True,
        default=fields.Datetime.now,
    )
    promised_date = fields.Datetime(string='Fecha prometida')
    is_late = fields.Boolean(
        string='Atrasada',
        compute='_compute_is_late',
    )
    description = fields.Text(string='Solicitud del cliente')
    diagnosis = fields.Text(string='Diagnóstico')
    internal_notes = fields.Text(string='Notas internas')

    # Garantías y retrabajos -------------------------------------------------
    original_order_id = fields.Many2one(
        'workshop.order',
        string='Orden original',
        copy=False,
        index=True,
        help='Orden a la que corresponde esta garantía, retrabajo o devolución.',
    )
    follow_up_type = fields.Selection(
        [
            ('warranty', 'Garantía'),
            ('rework', 'Retrabajo'),
            ('return', 'Devolución'),
        ],
        string='Tipo de seguimiento',
    )

    # Aceptación del presupuesto ----------------------------------------------
    accepted_by_name = fields.Char(
        string='Aceptado por',
        help='Persona del cliente que aceptó el presupuesto.',
    )
    acceptance_channel = fields.Selection(
        [
            ('in_person', 'Presencial'),
            ('phone', 'Teléfono'),
            ('message', 'Mensaje'),
            ('email', 'Correo'),
            ('other', 'Otro'),
        ],
        string='Canal de aceptación',
    )
    acceptance_notes = fields.Text(string='Observaciones de la aceptación')
    accepted_at = fields.Datetime(
        string='Fecha de aceptación',
        readonly=True,
        copy=False,
    )
    accepted_registered_by_id = fields.Many2one(
        'res.users',
        string='Aceptación registrada por',
        readonly=True,
        copy=False,
    )

    # Entrega, cierre y cancelación -----------------------------------------
    delivery_received_by = fields.Char(
        string='Recibido por (cliente)',
        help='Confirmación de recepción del cliente al entregar.',
    )
    delivered_by_id = fields.Many2one(
        'res.users',
        string='Entregado por',
        readonly=True,
        copy=False,
    )
    cancellation_reason = fields.Text(string='Motivo de cancelación')
    completed_at = fields.Datetime(string='Fecha de terminación', readonly=True, copy=False)
    delivered_at = fields.Datetime(string='Fecha de entrega', readonly=True, copy=False)
    closed_at = fields.Datetime(string='Fecha de cierre', readonly=True, copy=False)

    # Ejecución ---------------------------------------------------------------
    procedure_application_ids = fields.One2many(
        'workshop.order.procedure',
        'order_id',
        string='Procedimientos aplicados',
    )
    line_ids = fields.One2many(
        'workshop.order.line',
        'order_id',
        string='Líneas de ejecución',
    )

    # ------------------------------------------------------------------
    # Cómputos y validaciones de datos
    # ------------------------------------------------------------------
    @api.depends('promised_date', 'state')
    def _compute_is_late(self):
        now = fields.Datetime.now()
        for order in self:
            order.is_late = bool(
                order.promised_date
                and order.promised_date < now
                and order.state not in ('entregada', 'cerrada', 'cancelada')
            )

    @api.constrains('original_order_id', 'follow_up_type')
    def _check_follow_up(self):
        for order in self:
            if order.original_order_id == order:
                raise ValidationError(
                    'Una orden no puede ser su propia orden original.'
                )
            if order.original_order_id and not order.follow_up_type:
                raise ValidationError(
                    'Indique si la orden es de garantía, retrabajo o devolución.'
                )
            if order.follow_up_type and not order.original_order_id:
                raise ValidationError('Indique la orden original.')

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        if self.equipment_id.partner_id and not self.partner_id:
            self.partner_id = self.equipment_id.partner_id

    # ------------------------------------------------------------------
    # Escritura protegida
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('state', 'solicitud') != 'solicitud':
                raise UserError(
                    'Una orden nueva solo puede crearse en estado «Solicitud».'
                )
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('workshop.order')
                    or 'New'
                )
        return super().create(vals_list)

    def write(self, vals):
        if 'state' in vals:
            raise UserError(
                'El estado solo puede cambiar mediante las acciones '
                'del flujo de la orden.'
            )
        if self.filtered(lambda o: o.state in ('cerrada', 'cancelada')):
            # Las correcciones posteriores al cierre requerirán un
            # mecanismo autorizado y auditado (pendiente de diseño).
            raise UserError(
                'Una orden cerrada o cancelada no puede modificarse.'
            )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda o: o.state != 'solicitud'):
            raise UserError(
                'Solo pueden eliminarse órdenes en estado «Solicitud». '
                'Cancele la orden para conservar su historial.'
            )
        return super().unlink()

    # ------------------------------------------------------------------
    # Infraestructura de transiciones
    # ------------------------------------------------------------------
    def _require_group(self, group_xmlid, action_label):
        """Exige pertenecer al grupo indicado (el superusuario queda exento)."""
        if self.env.is_superuser() or self.env.user.has_group(group_xmlid):
            return
        raise AccessError(f'No tiene permiso para {action_label}.')

    def _change_state(self, new_state, extra_vals=None):
        """Valida y aplica una transición de estado a todas las órdenes."""
        labels = dict(self._fields['state'].selection)
        for order in self:
            if new_state not in STATE_TRANSITIONS.get(order.state, ()):
                raise UserError(
                    f'Transición no permitida en la orden {order.name}: de '
                    f'«{labels[order.state]}» a «{labels[new_state]}».'
                )
        vals = dict(extra_vals or {}, state=new_state)
        super(WorkshopOrder, self).write(vals)

    # ------------------------------------------------------------------
    # Acciones del flujo
    # ------------------------------------------------------------------
    def action_start_diagnosis(self):
        """Solicitud -> Diagnóstico."""
        self._require_group(GROUP_TECHNICIAN, 'iniciar el diagnóstico')
        self._change_state('diagnostico')
        return True

    def action_send_quote(self):
        """Diagnóstico -> Presupuesto. Exige un diagnóstico registrado."""
        self._require_group(GROUP_TECHNICIAN, 'pasar la orden a presupuesto')
        for order in self:
            if not (order.diagnosis or '').strip():
                raise UserError(
                    f'La orden {order.name} necesita un diagnóstico antes de '
                    'pasar a presupuesto.'
                )
        self._change_state('presupuesto')
        return True

    def action_approve(self):
        """Presupuesto -> Aprobada. Registra quién, cuándo y por qué canal."""
        if not (
            self.env.is_superuser()
            or self.env.user.has_group(GROUP_SUPERVISOR)
            or self.env.user.has_group(GROUP_SALESPERSON)
        ):
            raise AccessError(
                'No tiene permiso para registrar la aprobación del presupuesto.'
            )
        for order in self:
            if not order.accepted_by_name or not order.acceptance_channel:
                raise UserError(
                    f'Indique quién aceptó el presupuesto de la orden '
                    f'{order.name} y por qué canal.'
                )
        self._change_state('aprobada', {
            'accepted_at': fields.Datetime.now(),
            'accepted_registered_by_id': self.env.user.id,
        })
        return True

    def action_start_repair(self):
        """Aprobada (o Presupuesto, si no se exige aprobación) -> En reparación."""
        self._require_group(GROUP_TECHNICIAN, 'iniciar la reparación')
        for order in self:
            requires_acceptance = (
                order.repair_type_id.require_quote_acceptance
                if order.repair_type_id else True
            )
            if order.state == 'presupuesto' and requires_acceptance:
                raise UserError(
                    f'La orden {order.name} requiere la aprobación del '
                    'presupuesto antes de iniciar la reparación.'
                )
        self._change_state('en_reparacion')
        return True

    def action_finish(self):
        """En reparación -> Terminada. Exige completar las líneas obligatorias."""
        self._require_group(GROUP_TECHNICIAN, 'terminar la reparación')
        for order in self:
            pending = order.line_ids.filtered(
                lambda line: line.required and line.state == 'pending'
            )
            if pending:
                raise UserError(
                    f'La orden {order.name} tiene líneas obligatorias '
                    'pendientes:\n- ' + '\n- '.join(pending.mapped('name'))
                )
        self._change_state('terminada', {'completed_at': fields.Datetime.now()})
        return True

    def action_deliver(self):
        """Terminada -> Entregada. Registra quién entrega y quién recibe."""
        self._require_group(GROUP_SUPERVISOR, 'registrar la entrega')
        for order in self:
            if not order.delivery_received_by:
                raise UserError(
                    f'Indique quién recibe el equipo en la orden {order.name}.'
                )
        self._change_state('entregada', {
            'delivered_at': fields.Datetime.now(),
            'delivered_by_id': self.env.user.id,
        })
        return True

    def action_close(self):
        """Entregada -> Cerrada (cierre administrativo)."""
        self._require_group(GROUP_SUPERVISOR, 'cerrar órdenes')
        self._change_state('cerrada', {'closed_at': fields.Datetime.now()})
        return True

    def action_cancel(self):
        """Cancela la orden antes de su entrega. Exige un motivo.

        La orden y su historial se conservan. El tratamiento de materiales y
        movimientos de inventario llegará con la integración con Stock.
        """
        self._require_group(GROUP_SUPERVISOR, 'cancelar órdenes')
        for order in self:
            if not (order.cancellation_reason or '').strip():
                raise UserError(
                    f'Indique el motivo de cancelación de la orden {order.name}.'
                )
        self._change_state('cancelada')
        return True
