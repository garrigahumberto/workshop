"""Procedimientos de taller versionados.

Modelos de este archivo:

* ``workshop.procedure``: identidad estable de una receta reutilizable.
* ``workshop.procedure.version``: definición concreta y reproducible. Ciclo de
  vida: en preparación -> publicada -> retirada. Una versión publicada o
  retirada es inmutable (se valida en el servidor, no solo en la interfaz).
* ``workshop.procedure.line``: elemento previsto dentro de una versión.

Los procedimientos compuestos referencian versiones concretas y publicadas de
otros procedimientos. Los ciclos entre procedimientos se rechazan.
"""
from odoo import Command, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

GROUP_PROCEDURE_MANAGER = 'workshop_service.group_workshop_procedure_manager'

# Clave de contexto que permite a las acciones de publicar/retirar escribir en
# una versión bloqueada. Solo la usa el código de este archivo.
INTERNAL_CONTEXT_KEY = 'workshop_version_internal'

LINE_TYPES = [
    ('operation', 'Operación'),
    ('component', 'Componente'),
    ('consumable', 'Consumible'),
    ('service_labor', 'Servicio / mano de obra'),
    ('quality_test', 'Prueba de calidad'),
    ('subprocedure', 'Subprocedimiento'),
]

VALUATION_METHODS = [
    ('fixed', 'Precio fijo'),
    ('hourly', 'Horas reales por tarifa'),
]


class WorkshopProcedure(models.Model):
    """Identidad estable de un procedimiento; las líneas viven en sus versiones."""

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
    published_version_id = fields.Many2one(
        'workshop.procedure.version',
        string='Versión publicada vigente',
        compute='_compute_published_version_id',
        help='Última versión publicada (la de número más alto).',
    )

    @api.depends('version_ids.state', 'version_ids.version_number')
    def _compute_published_version_id(self):
        for procedure in self:
            published = procedure.version_ids.filtered(
                lambda version: version.state == 'published'
            )
            procedure.published_version_id = (
                published.sorted('version_number')[-1:] if published else False
            )

    def action_new_version(self):
        """Crea una versión en blanco en preparación y la abre."""
        self.ensure_one()
        Version = self.env['workshop.procedure.version']
        Version._check_procedure_manager()
        version = Version.create({'procedure_id': self.id})
        return version._get_form_action()


class WorkshopProcedureVersion(models.Model):
    """Versión de un procedimiento.

    Solo las versiones en preparación pueden editarse. Publicar valida la
    integridad de las líneas; retirar impide nuevas aplicaciones sin afectar
    a las órdenes históricas.
    """

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
            ('published', 'Publicada'),
            ('retired', 'Retirada'),
        ],
        string='Estado',
        required=True,
        default='preparation',
        copy=False,
    )
    change_summary = fields.Text(
        string='Resumen de cambios',
    )
    line_ids = fields.One2many(
        'workshop.procedure.line',
        'version_id',
        string='Líneas',
    )
    published_by = fields.Many2one(
        'res.users',
        string='Publicada por',
        readonly=True,
        copy=False,
    )
    published_at = fields.Datetime(
        string='Fecha de publicación',
        readonly=True,
        copy=False,
    )
    retired_by = fields.Many2one(
        'res.users',
        string='Retirada por',
        readonly=True,
        copy=False,
    )
    retired_at = fields.Datetime(
        string='Fecha de retirada',
        readonly=True,
        copy=False,
    )

    # ------------------------------------------------------------------
    # Presentación
    # ------------------------------------------------------------------
    @api.depends('procedure_id.code', 'procedure_id.name', 'version_number')
    def _compute_display_name(self):
        for version in self:
            procedure = version.procedure_id
            version.display_name = (
                f'[{procedure.code or ""}] {procedure.name or ""} '
                f'- v{version.version_number}'
            )

    # ------------------------------------------------------------------
    # Escritura protegida
    # ------------------------------------------------------------------
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

        if not self.env.context.get(INTERNAL_CONTEXT_KEY):
            if 'state' in vals:
                raise UserError(
                    'El estado de una versión solo cambia mediante las '
                    'acciones de publicar o retirar.'
                )
            if self.filtered(lambda version: version.state != 'preparation'):
                raise UserError(
                    'Una versión publicada o retirada no puede modificarse. '
                    'Cree una nueva versión a partir de ella.'
                )

        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda version: version.state != 'preparation'):
            raise UserError(
                'No se puede eliminar una versión publicada o retirada: '
                'forma parte del historial.'
            )
        return super().unlink()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('state', 'preparation') != 'preparation':
                raise UserError(
                    'Una versión nueva solo puede crearse en preparación.'
                )

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

    # ------------------------------------------------------------------
    # Permisos
    # ------------------------------------------------------------------
    @api.model
    def _check_procedure_manager(self):
        """Exige pertenecer al grupo «Gestor de procedimientos».

        Los técnicos pueden ejecutar procedimientos pero no publicarlos ni
        crear versiones. El superusuario técnico queda exento (pruebas y
        tareas del sistema).
        """
        if self.env.is_superuser() or self.env.user.has_group(
            GROUP_PROCEDURE_MANAGER
        ):
            return
        raise AccessError(
            'Solo un gestor de procedimientos puede crear, publicar o '
            'retirar versiones.'
        )

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------
    def _get_referenced_procedure_ids(self):
        """Devuelve los ids de procedimientos alcanzables desde esta versión.

        Recorre de forma transitiva las líneas de subprocedimiento y recoge
        el procedimiento de cada versión referenciada.
        """
        self.ensure_one()
        visited = set()
        procedure_ids = set()
        pending = self
        while pending:
            next_versions = self.browse()
            for version in pending:
                if version.id in visited:
                    continue
                visited.add(version.id)
                for line in version.line_ids.filtered(
                    lambda l: l.line_type == 'subprocedure'
                    and l.subprocedure_version_id
                ):
                    target = line.subprocedure_version_id
                    procedure_ids.add(target.procedure_id.id)
                    next_versions |= target
            pending = next_versions
        return procedure_ids

    def _check_no_cycles(self):
        """Rechaza referencias circulares entre procedimientos."""
        for version in self:
            if version.procedure_id.id in version._get_referenced_procedure_ids():
                raise ValidationError(
                    f'La versión {version.display_name} forma una referencia '
                    'circular entre procedimientos.'
                )

    def _validate_for_publication(self):
        """Valida que la versión pueda publicarse; lanza error si no."""
        self.ensure_one()
        if not self.line_ids:
            raise UserError(
                f'No se puede publicar {self.display_name}: no tiene líneas.'
            )
        for line in self.line_ids:
            line._validate_for_publication()
        self._check_no_cycles()

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def _get_form_action(self):
        """Acción de ventana que abre esta versión en su formulario."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.display_name,
            'res_model': 'workshop.procedure.version',
            'res_id': self.id,
            'view_mode': 'form',
        }

    def action_publish(self):
        """Publica versiones en preparación (las vuelve inmutables)."""
        self._check_procedure_manager()
        for version in self:
            if version.state != 'preparation':
                raise UserError(
                    f'Solo se puede publicar una versión en preparación '
                    f'({version.display_name}).'
                )
            version._validate_for_publication()
        self.with_context(**{INTERNAL_CONTEXT_KEY: True}).write({
            'state': 'published',
            'published_by': self.env.user.id,
            'published_at': fields.Datetime.now(),
        })
        return True

    def action_retire(self):
        """Retira versiones publicadas: no admiten nuevas aplicaciones."""
        self._check_procedure_manager()
        for version in self:
            if version.state != 'published':
                raise UserError(
                    f'Solo se puede retirar una versión publicada '
                    f'({version.display_name}).'
                )
        self.with_context(**{INTERNAL_CONTEXT_KEY: True}).write({
            'state': 'retired',
            'retired_by': self.env.user.id,
            'retired_at': fields.Datetime.now(),
        })
        return True

    def action_create_new_version(self):
        """Crea una nueva versión en preparación copiando las líneas actuales.

        La versión original se conserva intacta.
        """
        self.ensure_one()
        self._check_procedure_manager()
        new_version = self.create({
            'procedure_id': self.procedure_id.id,
            'line_ids': [
                Command.create(line._get_copy_values())
                for line in self.line_ids
            ],
        })
        return new_version._get_form_action()


class WorkshopProcedureLine(models.Model):
    """Línea de definición de una versión de procedimiento.

    Una línea puede describir una necesidad genérica sin fijar marca ni
    referencia comercial; el producto concreto se elige al ejecutar la orden.
    Las líneas de una versión no editable no pueden crearse, modificarse ni
    eliminarse.
    """

    _name = 'workshop.procedure.line'
    _description = 'Línea de procedimiento de taller'
    _order = 'version_id, sequence, id'

    _quantity_positive = models.Constraint(
        'CHECK(quantity >= 0)',
        'La cantidad prevista no puede ser negativa.',
    )

    version_id = fields.Many2one(
        'workshop.procedure.version',
        string='Versión',
        required=True,
        ondelete='cascade',
        index=True,
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
    required = fields.Boolean(string='Obligatoria', default=True)
    is_blocking = fields.Boolean(
        string='Bloqueante',
        help='Para pruebas de calidad: una prueba obligatoria y bloqueante '
             'impide terminar la orden mientras no se apruebe.',
    )
    product_category_id = fields.Many2one(
        'product.category',
        string='Categoría de producto',
        help='Permite definir una necesidad genérica (p. ej. «Batería 12 V»).',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        help='Solo cuando el procedimiento prescribe una referencia concreta.',
    )
    quantity = fields.Float(
        string='Cantidad prevista',
        digits=(16, 4),
        default=1.0,
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unidad de medida',
    )
    estimated_minutes = fields.Float(string='Minutos estimados')
    valuation_method = fields.Selection(
        VALUATION_METHODS,
        string='Valoración',
        help='Solo para servicios y mano de obra.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id.id,
    )
    reference_price = fields.Monetary(
        string='Precio de referencia',
        currency_field='currency_id',
    )
    reference_hourly_rate = fields.Monetary(
        string='Tarifa horaria de referencia',
        currency_field='currency_id',
    )
    alternative_product_ids = fields.Many2many(
        'product.product',
        'workshop_procedure_line_alt_product_rel',
        'line_id',
        'product_id',
        string='Alternativas autorizadas',
    )
    subprocedure_version_id = fields.Many2one(
        'workshop.procedure.version',
        string='Versión del subprocedimiento',
        ondelete='restrict',
        help='Versión concreta y publicada que se expandirá al aplicar.',
    )

    # ------------------------------------------------------------------
    # Escritura protegida
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        version_ids = {
            vals['version_id'] for vals in vals_list if vals.get('version_id')
        }
        versions = self.env['workshop.procedure.version'].browse(version_ids)
        if versions.filtered(lambda version: version.state != 'preparation'):
            raise UserError(
                'No se pueden añadir líneas a una versión publicada o retirada.'
            )
        return super().create(vals_list)

    def write(self, vals):
        if 'version_id' in vals and any(
            line.version_id.id != vals['version_id'] for line in self
        ):
            raise UserError('No se puede mover una línea a otra versión.')
        self._check_version_editable()
        return super().write(vals)

    def unlink(self):
        self._check_version_editable()
        return super().unlink()

    def _check_version_editable(self):
        if self.version_id.filtered(lambda version: version.state != 'preparation'):
            raise UserError(
                'Las líneas de una versión publicada o retirada no pueden '
                'modificarse ni eliminarse.'
            )

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------
    @api.constrains('alternative_product_ids', 'line_type')
    def _check_alternatives(self):
        for line in self:
            if line.alternative_product_ids and line.line_type not in (
                'component', 'consumable',
            ):
                raise ValidationError(
                    f'Línea «{line.name}»: solo los componentes y consumibles '
                    'admiten productos alternativos.'
                )

    @api.constrains('subprocedure_version_id', 'version_id', 'line_type')
    def _check_subprocedure(self):
        for line in self:
            if line.line_type != 'subprocedure':
                if line.subprocedure_version_id:
                    raise ValidationError(
                        f'Línea «{line.name}»: solo las líneas de tipo '
                        'subprocedimiento pueden referenciar otra versión.'
                    )
                continue
            if line.subprocedure_version_id:
                line.version_id._check_no_cycles()

    def _validate_for_publication(self):
        """Comprueba los datos exigidos según el tipo de línea."""
        self.ensure_one()
        prefix = f'Línea «{self.name}»: '
        if self.line_type in ('component', 'consumable'):
            if self.quantity <= 0:
                raise UserError(prefix + 'indique una cantidad prevista mayor que cero.')
            if not self.product_uom_id:
                raise UserError(prefix + 'indique la unidad de medida.')
        elif self.line_type == 'service_labor':
            if not self.valuation_method:
                raise UserError(prefix + 'indique el método de valoración.')
            if self.valuation_method == 'fixed' and self.reference_price <= 0:
                raise UserError(prefix + 'indique un precio de referencia mayor que cero.')
            if self.valuation_method == 'hourly' and self.reference_hourly_rate <= 0:
                raise UserError(prefix + 'indique una tarifa horaria mayor que cero.')
        elif self.line_type == 'subprocedure':
            if not self.subprocedure_version_id:
                raise UserError(prefix + 'indique la versión del subprocedimiento.')
            if self.subprocedure_version_id.state != 'published':
                raise UserError(
                    prefix + 'el subprocedimiento debe referenciar una '
                    'versión publicada.'
                )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Completa unidad, categoría y descripción desde el producto elegido."""
        if self.product_id:
            if not self.product_uom_id:
                self.product_uom_id = self.product_id.uom_id
            if not self.product_category_id:
                self.product_category_id = self.product_id.categ_id
            if not self.name:
                self.name = self.product_id.display_name

    def _get_copy_values(self):
        """Valores para duplicar la línea en otra versión."""
        self.ensure_one()
        return {
            'sequence': self.sequence,
            'line_type': self.line_type,
            'name': self.name,
            'description': self.description,
            'required': self.required,
            'is_blocking': self.is_blocking,
            'product_category_id': self.product_category_id.id,
            'product_id': self.product_id.id,
            'quantity': self.quantity,
            'product_uom_id': self.product_uom_id.id,
            'estimated_minutes': self.estimated_minutes,
            'valuation_method': self.valuation_method,
            'currency_id': self.currency_id.id,
            'reference_price': self.reference_price,
            'reference_hourly_rate': self.reference_hourly_rate,
            'alternative_product_ids': [
                Command.set(self.alternative_product_ids.ids)
            ],
            'subprocedure_version_id': self.subprocedure_version_id.id,
        }
