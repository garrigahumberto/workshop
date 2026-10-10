# Modelo lógico de datos — Módulo de taller Odoo 20 Community

**Estado:** Diseño propuesto para implementación
**Versión:** 1.0
**Ámbito:** MVP del módulo genérico de taller y servicios técnicos
**Plataforma:** Odoo 20 Community

## 1. Propósito

Este documento transforma el modelo conceptual en una estructura lógica que pueda implementarse en Odoo.

Define los modelos propios, sus campos esenciales, relaciones, restricciones y responsabilidades. No sustituye los requisitos ni la especificación funcional consolidada.

### Documentos de referencia

* `requisitos.md`
* `especificacion_funcional_consolidada.md`
* `modelo_conceptual_datos.md`

En caso de discrepancia, prevalece la especificación funcional consolidada. Los agentes no deben resolver contradicciones funcionales por iniciativa propia.

## 2. Principios de diseño

1. La orden de trabajo y los procedimientos versionados constituyen el núcleo propio del módulo.
2. Odoo conserva la autoridad sobre productos, unidades de medida, inventario, movimientos físicos, lotes, números de serie, pedidos de venta, impuestos, facturas y contabilidad.
3. Aplicar un procedimiento genera una copia ejecutable de sus instrucciones. Los cambios posteriores en la plantilla no alteran las órdenes existentes.
4. Las versiones publicadas de los procedimientos son inmutables.
5. Los registros de ejecución, intentos de calidad y decisiones comerciales conservan su historial.
6. Las cantidades previstas, las cantidades reales, los movimientos físicos y los conceptos facturables son datos distintos.
7. Las validaciones críticas se aplican en el servidor y no pueden desactivarse mediante configuración.
8. Los modelos propios deben respetar la compañía activa y los mecanismos estándar de acceso de Odoo.
9. No se crearán modelos adicionales sin una necesidad funcional identificada.
10. Las API exactas se verificarán contra Odoo 20 antes de implementarlas.

## 3. Convenciones generales

* Prefijo de modelos: `workshop`.
* Los campos relacionales deben apuntar a los modelos estándar correspondientes cuando estos ya representen el concepto.
* Los identificadores técnicos deben mantenerse consistentes en todo el módulo.
* Los registros principales deben incluir seguimiento de cambios cuando aporte valor.
* Las cantidades utilizarán las unidades de medida de Odoo y sus reglas de precisión.
* Los precios, impuestos y redondeos comerciales utilizarán los mecanismos estándar de Odoo.
* Los datos históricos que deban conservar su significado se copiarán al crear la ejecución, en lugar de depender exclusivamente de referencias a plantillas modificables.
* La eliminación de registros se restringirá cuando pueda destruir trazabilidad. Se preferirán archivado y acciones controladas.

## 4. Modelos de datos

### 4.1. `workshop.order` — Orden de trabajo

**Responsabilidad:** gestionar la reparación desde la recepción hasta el cierre, coordinando diagnóstico, presupuesto, ejecución, calidad y entrega.

| Campo                       | Tipo                                    | Regla o finalidad                                     |
| --------------------------- | --------------------------------------- | ----------------------------------------------------- |
| `name`                      | Char                                    | Número único de orden, asignado mediante secuencia.   |
| `company_id`                | Many2one → `res.company`                | Compañía responsable. Obligatorio.                    |
| `partner_id`                | Many2one → `res.partner`                | Cliente de la orden.                                  |
| `equipment_id`              | Many2one → `workshop.equipment`         | Equipo recibido, opcional según el caso.              |
| `repair_type_id`            | Many2one → `workshop.repair.type`       | Tipo de reparación.                                   |
| `user_id`                   | Many2one → `res.users`                  | Técnico responsable principal.                        |
| `priority`                  | Selection                               | Normal, alta o urgente.                               |
| `state`                     | Selection                               | Estado del ciclo funcional definido.                  |
| `request_date`              | Datetime                                | Fecha de recepción o registro.                        |
| `promised_date`             | Datetime                                | Fecha prometida opcional.                             |
| `description`               | Text                                    | Solicitud o descripción inicial del cliente.          |
| `diagnosis`                 | Text                                    | Diagnóstico técnico.                                  |
| `internal_notes`            | Text                                    | Notas internas, sujetas a permisos.                   |
| `cancellation_reason`       | Text                                    | Motivo obligatorio al cancelar.                       |
| `original_order_id`         | Many2one → `workshop.order`             | Orden original para garantía, retrabajo o devolución. |
| `procedure_application_ids` | One2many → `workshop.order.procedure`   | Procedimientos aplicados.                             |
| `line_ids`                  | One2many → `workshop.order.line`        | Instrucciones y ejecución.                            |
| `removed_component_ids`     | One2many → `workshop.removed.component` | Componentes retirados.                                |
| `billing_proposal_ids`      | One2many → `workshop.billing.proposal`  | Propuestas comerciales relacionadas.                  |
| `completed_at`              | Datetime                                | Fecha de terminación técnica.                         |
| `delivered_at`              | Datetime                                | Fecha de entrega.                                     |
| `closed_at`                 | Datetime                                | Fecha de cierre.                                      |

#### Reglas

* Los estados corresponden al flujo funcional acordado: solicitud, diagnóstico, presupuesto, aprobada, en reparación, terminada, entregada y cerrada, además de cancelación controlada.
* Las transiciones se ejecutan mediante acciones de servidor que comprueban sus precondiciones.
* El campo `state` no debe permitir transiciones arbitrarias por escritura directa.
* La cancelación requiere motivo y tratamiento controlado del trabajo y los materiales ya utilizados.
* La cancelación nunca revierte silenciosamente movimientos de inventario completados.
* Las correcciones posteriores al cierre deben estar restringidas y auditadas.
* La orden debe conservar la aceptación del presupuesto y sus datos de trazabilidad conforme a la especificación funcional.
* La prioridad urgente no elimina requisitos de autorización, inventario o calidad.

### 4.2. `workshop.equipment` — Equipo del cliente

**Responsabilidad:** identificar un artículo o equipo que pueda aparecer en varias órdenes.

| Campo            | Tipo                      | Regla o finalidad                         |
| ---------------- | ------------------------- | ----------------------------------------- |
| `name`           | Char                      | Nombre o descripción identificable.       |
| `company_id`     | Many2one → `res.company`  | Compañía responsable.                     |
| `partner_id`     | Many2one → `res.partner`  | Propietario o cliente asociado.           |
| `equipment_type` | Char o categoría definida | Tipo de equipo.                           |
| `brand`          | Char                      | Marca.                                    |
| `model`          | Char                      | Modelo.                                   |
| `serial_number`  | Char                      | Número de serie, si existe.               |
| `description`    | Text                      | Observaciones e identificación adicional. |
| `active`         | Boolean                   | Archivado lógico.                         |

Un equipo puede relacionarse con muchas órdenes. La orden también puede existir sin un registro permanente de equipo.

No se debe interpretar automáticamente `maintenance.equipment.partner_id` como propietario: su semántica estándar debe respetarse. El MVP utiliza un modelo propio para evitar una dependencia obligatoria del módulo Mantenimiento.

### 4.3. `workshop.repair.type` — Tipo de reparación

**Responsabilidad:** agrupar trabajos y definir requisitos configurables por tipo.

Campos esenciales:

* `name`: nombre.
* `code`: código identificador.
* `active`: disponibilidad.
* `company_id`: ámbito de compañía, cuando corresponda.
* Relaciones con procedimientos o versiones sugeridas.
* Parámetros de recepción.
* Reglas configurables de aceptación del presupuesto.
* Requisitos de documentación y pruebas que permita la especificación funcional.

El tipo de reparación puede sugerir procedimientos y exigir validaciones. No define un ciclo de estados alternativo ni puede desactivar controles críticos.

### 4.4. `workshop.procedure` — Procedimiento

**Responsabilidad:** representar la identidad estable de una receta o procedimiento reutilizable.

Campos esenciales:

* `name`: nombre.
* `code`: código único según el ámbito definido.
* `active`: indica si puede utilizarse para nuevas aplicaciones.
* `company_id`: ámbito aplicable.
* `version_ids`: versiones del procedimiento.
* `current_published_version_id`: referencia a la versión publicada vigente, si se necesita para facilitar la selección.

Las líneas no se almacenan directamente en este modelo: pertenecen a una versión concreta.

### 4.5. `workshop.procedure.version` — Versión del procedimiento

**Responsabilidad:** conservar una definición concreta y reproducible del procedimiento.

| Campo            | Tipo                                 | Regla o finalidad                           |
| ---------------- | ------------------------------------ | ------------------------------------------- |
| `procedure_id`   | Many2one → `workshop.procedure`      | Procedimiento propietario.                  |
| `version_number` | Integer                              | Número secuencial dentro del procedimiento. |
| `state`          | Selection                            | Preparación, publicada o retirada.          |
| `line_ids`       | One2many → `workshop.procedure.line` | Líneas de la versión.                       |
| `created_by`     | Many2one → `res.users`               | Autor de la versión.                        |
| `created_at`     | Datetime                             | Fecha de creación.                          |
| `published_by`   | Many2one → `res.users`               | Usuario que publica.                        |
| `published_at`   | Datetime                             | Fecha de publicación.                       |
| `change_summary` | Text                                 | Resumen de cambios.                         |
| `company_id`     | Many2one → `res.company`             | Compañía, cuando corresponda.               |

#### Restricciones

* La combinación de procedimiento y número de versión es única.
* Solo las versiones en preparación pueden editarse.
* La publicación valida la integridad de sus líneas.
* Una versión publicada no puede modificarse ni eliminarse mediante las operaciones ordinarias.
* Retirar una versión impide nuevas aplicaciones según la política definida, pero no invalida órdenes históricas.
* La orden conservará la referencia a la versión exacta aplicada.
* La inmutabilidad se garantiza en el servidor, no únicamente deshabilitando campos en la interfaz.

### 4.6. `workshop.procedure.line` — Línea de procedimiento

**Responsabilidad:** definir una instrucción de una versión concreta.

Campos esenciales:

* `version_id`: versión propietaria.
* `sequence`: orden de presentación o ejecución.
* `line_type`: operación, material, servicio, mano de obra, prueba de calidad o subprocedimiento.
* `name`: descripción breve.
* `description`: instrucciones detalladas.
* `required`: indica si la línea es obligatoria.
* `product_id`: producto estándar de Odoo, cuando corresponda.
* `quantity`: cantidad prevista.
* `product_uom_id`: unidad de medida.
* `estimated_minutes`: tiempo estimado, si aplica.
* `subprocedure_version_id`: versión concreta del subprocedimiento.
* Parámetros de calidad necesarios para definir si una prueba es obligatoria o bloqueante.

#### Validaciones

* Las unidades de medida deben ser compatibles con el producto.
* Los tipos de línea deben tener los campos obligatorios que les correspondan.
* Una línea de subprocedimiento debe apuntar a una versión publicada concreta.
* Deben impedirse referencias circulares entre procedimientos compuestos.
* No se implementarán reglas condicionales avanzadas en el MVP.
* Las diferencias de comportamiento entre tipos de línea se resolverán mediante validaciones claras, sin crear un modelo independiente por cada tipo salvo necesidad demostrada.

### 4.7. `workshop.order.procedure` — Aplicación de procedimiento

**Responsabilidad:** registrar la aplicación de una versión concreta a una orden.

Campos esenciales:

* `order_id`: orden de trabajo.
* `procedure_id`: procedimiento de origen.
* `procedure_version_id`: versión exacta aplicada.
* `applied_by`: usuario que la aplicó.
* `applied_at`: fecha y hora.
* Referencia a la aplicación de origen cuando se trate de un subprocedimiento expandido, si resulta necesaria.
* `company_id`: compañía.

Al aplicar una versión se crean las líneas ejecutables correspondientes. La aplicación conserva su procedencia, incluida la versión exacta de los subprocedimientos.

Una orden puede tener varias aplicaciones de procedimientos.

### 4.8. `workshop.order.line` — Línea ejecutable

**Responsabilidad:** representar una instrucción aplicada a la orden y registrar su ejecución real.

| Campo                      | Tipo                                  | Regla o finalidad                                    |
| -------------------------- | ------------------------------------- | ---------------------------------------------------- |
| `order_id`                 | Many2one → `workshop.order`           | Orden propietaria.                                   |
| `procedure_application_id` | Many2one → `workshop.order.procedure` | Aplicación de origen, opcional para líneas manuales. |
| `source_procedure_line_id` | Many2one → `workshop.procedure.line`  | Referencia de procedencia.                           |
| `sequence`                 | Integer                               | Orden de ejecución.                                  |
| `line_type`                | Selection                             | Tipo de instrucción.                                 |
| `name` / `description`     | Char / Text                           | Copia de la descripción aplicada.                    |
| `required`                 | Boolean                               | Obligatoriedad copiada.                              |
| `product_id`               | Many2one → `product.product`          | Producto, cuando corresponda.                        |
| `product_uom_id`           | Many2one → `uom.uom`                  | Unidad de medida.                                    |
| `planned_quantity`         | Float                                 | Cantidad prevista.                                   |
| `actual_quantity`          | Float                                 | Cantidad real.                                       |
| `estimated_minutes`        | Float                                 | Tiempo previsto, si aplica.                          |
| `actual_minutes`           | Float                                 | Tiempo real, cuando corresponda.                     |
| `state`                    | Selection                             | Pendiente, realizada o no aplicable.                 |
| `assigned_user_id`         | Many2one → `res.users`                | Técnico asignado, si corresponde.                    |
| `started_at`               | Datetime                              | Inicio de ejecución, cuando se registre.             |
| `completed_at`             | Datetime                              | Finalización.                                        |
| `not_applicable_reason`    | Text                                  | Motivo cuando no se realiza una línea.               |

Los campos de sustitución y autorización se añadirán a esta estructura cuando corresponda a la línea y al flujo definido.

#### Reglas

* Los datos funcionales aplicados son una instantánea. Los cambios en la plantilla no los actualizan.
* La cantidad real puede diferir de la prevista conforme a los requisitos cerrados.
* Las líneas ejecutadas no se eliminan para corregir errores.
* Una línea manual debe poder identificarse como tal y no fingir que procede de un procedimiento.
* La ejecución técnica no genera automáticamente cargos comerciales.
* Las relaciones con movimientos de inventario deben identificar la operación física correspondiente sin duplicar sus datos.

### 4.9. `workshop.quality.attempt` — Intento de prueba de calidad

**Responsabilidad:** conservar cada intento de una prueba realizada durante una orden.

Campos esenciales:

* `order_line_id`: línea ejecutable de tipo prueba.
* `attempt_number`: número secuencial del intento.
* `result`: aprobado, rechazado o no aplicable.
* `performed_by`: técnico responsable.
* `performed_at`: fecha y hora.
* `notes`: observaciones.
* `is_current`: indica si representa el resultado vigente.
* `company_id`: compañía, cuando corresponda.

#### Reglas

* Todos los intentos se conservan.
* Cada prueba tendrá como máximo un intento marcado como vigente.
* Un nuevo intento no elimina ni modifica el anterior.
* La finalización técnica comprueba los resultados vigentes de las pruebas obligatorias y bloqueantes.
* Los adjuntos y evidencias utilizan los mecanismos estándar de Odoo.

### 4.10. `workshop.removed.component` — Componente retirado

**Responsabilidad:** documentar componentes extraídos del equipo durante una reparación.

Campos esenciales:

* `order_id`: orden relacionada.
* `product_id`: producto estándar, si se identifica.
* `lot_id`: lote o serie, cuando corresponda.
* `description`: descripción del componente.
* `quantity`: cantidad, cuando se requiera.
* `product_uom_id`: unidad de medida.
* `disposition`: reutilizable, desechado o pendiente de evaluación.
* `recorded_by`: usuario que registra.
* `recorded_at`: fecha y hora.
* `notes`: observaciones.
* Referencia al movimiento estándar de inventario, si existe.

#### Reglas

* Clasificar un componente no crea automáticamente un movimiento de inventario.
* La clasificación técnica no determina por sí sola su facturación.
* Las operaciones físicas utilizan Stock.
* Los componentes pueden documentarse aunque no sean productos inventariables.

### 4.11. `workshop.billing.proposal` — Propuesta facturable

**Responsabilidad:** preparar y revisar los conceptos que pueden cobrarse por una orden.

Campos esenciales:

* `name`: número o referencia.
* `order_id`: orden relacionada.
* `company_id`: compañía.
* `partner_id`: cliente.
* `currency_id`: moneda.
* `state`: borrador, en revisión cuando aplique, confirmada o cancelada/sustituida según el flujo aprobado.
* `line_ids`: líneas de propuesta.
* `created_by`, `created_at`: creación.
* `reviewed_by`, `reviewed_at`: revisión.
* `confirmed_by`, `confirmed_at`: confirmación.
* `sale_order_id`: pedido de venta relacionado, cuando exista.

#### Reglas

* La propuesta se genera a partir de la ejecución real y queda pendiente de revisión.
* Un usuario autorizado revisa y confirma antes de crear o actualizar los documentos comerciales.
* La propuesta no es una factura ni un asiento contable.
* Los movimientos de inventario no generan cargos automáticamente.
* Las propuestas confirmadas conservan su historial y no se reescriben silenciosamente.

### 4.12. `workshop.billing.proposal.line` — Línea de propuesta

Campos esenciales:

* `proposal_id`: propuesta propietaria.
* `sequence`: orden.
* `name`: concepto.
* `product_id`: producto, cuando corresponda.
* `quantity`: cantidad facturable propuesta.
* `product_uom_id`: unidad de medida.
* `price_unit`: precio unitario propuesto.
* `tax_ids`: impuestos estándar de Odoo.
* `currency_id`: moneda.
* `source_order_line_id`: línea ejecutada de origen, cuando corresponda.
* `sale_order_line_id`: línea comercial estándar relacionada, cuando exista.
* Campos para identificar ajustes manuales autorizados, cuando corresponda.

La confirmación debe utilizar las API estándar de Ventas y evitar duplicar líneas si se reintenta la operación. La facturación posterior seguirá el flujo estándar de Odoo.

## 5. Relaciones entre modelos

Las relaciones principales son:

* Un cliente puede tener muchos equipos y órdenes.
* Un equipo puede estar asociado a muchas órdenes.
* Un tipo de reparación puede utilizarse en muchas órdenes y sugerir varios procedimientos.
* Un procedimiento tiene muchas versiones.
* Una versión tiene muchas líneas de definición.
* Una orden tiene muchas aplicaciones de procedimientos y líneas ejecutables.
* Cada aplicación referencia una versión concreta.
* Una línea ejecutable de calidad puede tener muchos intentos.
* Una orden puede registrar varios componentes retirados y propuestas comerciales.
* Una propuesta tiene muchas líneas y puede enlazarse con un pedido de venta.
* Las líneas ejecutables pueden relacionarse con movimientos de inventario.
* Los pedidos, líneas comerciales y facturas conservan los modelos estándar de Odoo.

## 6. Integración con modelos estándar

| Necesidad                   | Modelo estándar                        |
| --------------------------- | -------------------------------------- |
| Clientes                    | `res.partner`                          |
| Usuarios                    | `res.users`                            |
| Compañías                   | `res.company`                          |
| Monedas                     | `res.currency`                         |
| Productos                   | `product.product` y `product.template` |
| Unidades de medida          | `uom.uom`                              |
| Lotes y series              | Modelos estándar de Stock              |
| Movimientos físicos         | `stock.move` y `stock.move.line`       |
| Operaciones de almacén      | `stock.picking`, cuando corresponda    |
| Pedidos de venta            | `sale.order`                           |
| Líneas comerciales          | `sale.order.line`                      |
| Facturas y notas de crédito | `account.move`                         |
| Mensajería y seguimiento    | `mail.thread`, `mail.activity.mixin`   |
| Adjuntos                    | `ir.attachment`                        |

El módulo propio debe mantener referencias y trazabilidad, no replicar la responsabilidad de estos modelos.

## 7. Integridad, permisos e historial

1. Las transiciones de estado se validan en el servidor.
2. Las versiones publicadas se protegen contra modificación y eliminación ordinarias.
3. Las líneas aplicadas conservan sus datos históricos.
4. Los intentos de calidad se conservan y se identifica el resultado vigente.
5. Los movimientos completados no se revierten mediante cambios en la orden.
6. Las devoluciones se realizan con el flujo estándar de Stock.
7. La confirmación comercial requiere autorización.
8. Los costes internos se restringen mediante permisos, no solo ocultando campos en vistas.
9. Las correcciones posteriores al cierre deben ser restringidas y auditables.
10. Los controles críticos no pueden debilitarse desde la configuración.

## 8. Decisiones que no deben improvisarse

Si la especificación funcional no resuelve una situación, el agente debe identificarla y solicitar una decisión antes de introducir un comportamiento nuevo.

Los puntos especialmente sensibles son:

* Tratamiento comercial de componentes retirados que no se instalan.
* Modificación o sustitución de propuestas ya confirmadas.
* Sincronización con pedidos comerciales preexistentes.
* Permisos concretos de campos sensibles que no estén definidos.
* Comportamiento exacto de las API de inventario en Odoo 20.

Estas cuestiones no autorizan a ampliar el alcance ni a cambiar unilateralmente las decisiones funcionales cerradas.

## 9. Criterios de aceptación del diseño lógico

El diseño se considera suficiente para comenzar la implementación cuando:

1. Cada requisito funcional tiene un modelo o mecanismo responsable identificable.
2. Las relaciones y la conservación de datos históricos están definidas.
3. No se duplica la autoridad de Odoo sobre inventario, ventas o contabilidad.
4. Las reglas de publicación, ejecución, calidad y confirmación comercial pueden probarse.
5. Los puntos aún pendientes son detalles de implementación identificados, no requisitos nuevos.
6. Los agentes pueden implementar tareas acotadas sin tener que reinterpretar la arquitectura.

Este documento define el diseño lógico propuesto. No demuestra por sí mismo que la implementación sea compatible con Odoo 20; esa compatibilidad se verificará mediante inspección de la versión objetivo y pruebas reales.
