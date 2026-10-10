from odoo import api, fields, models


class WorkshopOrder(models.Model):
    _name = 'workshop.order'
    _description = 'Orden de trabajo'
    _order = 'request_date desc, id desc'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('workshop.order') or 'New'
        return super().create(vals_list)

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
    )
    user_id = fields.Many2one(
        'res.users',
        string='Técnico responsable',
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
    )
    request_date = fields.Datetime(
        string='Fecha de recepción',
        required=True,
        default=fields.Datetime.now,
    )
    promised_date = fields.Datetime(string='Fecha prometida')
    description = fields.Text(string='Solicitud del cliente')
    diagnosis = fields.Text(string='Diagnóstico')
    internal_notes = fields.Text(string='Notas internas')
    cancellation_reason = fields.Text(string='Motivo de cancelación')
    completed_at = fields.Datetime(string='Fecha de terminación')
    delivered_at = fields.Datetime(string='Fecha de entrega')
    closed_at = fields.Datetime(string='Fecha de cierre')
