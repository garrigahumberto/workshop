# Arquitectura técnica — Módulo de taller Odoo 20 Community

**Estado:** Arquitectura propuesta para implementación
**Versión:** 1.0
**Plataforma objetivo:** Odoo 20 Community
**Módulo técnico propuesto:** `workshop_service`
**Documento relacionado:** `docs/modelo_logico_datos.md`

## 1. Objetivo

Definir cómo implementar el módulo de taller sobre Odoo 20 Community, delimitando responsabilidades, dependencias, estructura de código, seguridad, integraciones y pruebas.

El módulo debe permitir gestionar órdenes de trabajo, ejecutar procedimientos reutilizables y versionados, registrar consumos y controles de calidad y preparar conceptos facturables a partir de la ejecución real.

La implementación debe ser incremental. No se desarrollarán funciones fuera del MVP ni se crearán abstracciones que no respondan a una necesidad identificada.

## 2. Decisiones arquitectónicas

### 2.1. Núcleo propio de órdenes de trabajo

La entidad principal será `workshop.order`.

No se utilizará `repair.order` como núcleo del flujo porque el ciclo funcional requerido es más amplio que el flujo estándar de Reparaciones. Tampoco se crearán estados personalizados mediante modificaciones innecesarias de módulos estándar.

El módulo propio gestionará:

* Recepción y diagnóstico.
* Presupuesto y aceptación.
* Ejecución de procedimientos.
* Consumos y componentes retirados.
* Pruebas de calidad.
* Terminación, entrega y cierre.
* Propuestas de conceptos facturables.

### 2.2. Procedimientos versionados

Los procedimientos se gestionarán mediante modelos propios.

Cada aplicación a una orden debe conservar la versión exacta utilizada y generar sus líneas ejecutables. La publicación de una versión la vuelve inmutable mediante validaciones del servidor.

Los cambios posteriores en una plantilla no deben modificar órdenes abiertas ni históricas.

### 2.3. Integración con Odoo estándar

El módulo no reemplazará las funciones existentes de Odoo:

* **Inventario:** movimientos físicos, reservas, devoluciones, lotes y series.
* **Ventas:** pedidos y líneas comerciales.
* **Facturación y contabilidad:** facturas, impuestos y asientos.
* **Productos:** productos, tipos y unidades de medida.
* **Contactos:** clientes y datos de contacto.
* **Mensajería:** seguimiento y comunicación vinculada a las órdenes.

Una operación técnica no equivale automáticamente a un movimiento físico ni a un cargo comercial.

### 2.4. Independencia de Reparaciones y Mantenimiento

No se declarará dependencia de los módulos `repair` o `maintenance` para el núcleo del MVP.

La incorporación futura de una integración con alguno de ellos requerirá una necesidad concreta y una decisión explícita. No se instalarán módulos adicionales solo porque parezcan relacionados con el concepto de taller.

## 3. Dependencias del módulo

El manifiesto debe declarar únicamente las dependencias necesarias para los modelos y funciones realmente implementados.

Como punto de partida:

| Módulo            | Motivo                                                                             |
| ----------------- | ---------------------------------------------------------------------------------- |
| `base`            | Modelos y servicios fundamentales de Odoo.                                         |
| `mail`            | Chatter, seguimiento y actividades cuando se utilicen.                             |
| `product`         | Productos y datos de producto.                                                     |
| `stock`           | Inventario, movimientos, reservas y devoluciones.                                  |
| `sale_management` | Pedidos de venta y líneas comerciales.                                             |
| `sale_stock`      | Integración entre ventas e inventario, si la integración implementada la requiere. |
| `account`         | Referencias o funcionalidades contables directas que justifiquen la dependencia.   |

**Regla de implementación:** verificar las dependencias efectivas y sus dependencias transitivas en la instalación objetivo de Odoo 20 antes de cerrar `__manifest__.py`. No añadir dependencias redundantes ni declarar módulos que el código no utilice.

No se debe depender de `repair` ni de `maintenance` sin una justificación aprobada.

## 4. Estructura de archivos

Estructura inicial propuesta:

```text
workshop_service/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── workshop_order.py
│   ├── workshop_equipment.py
│   ├── workshop_repair_type.py
│   ├── workshop_procedure.py
│   ├── workshop_order_line.py
│   ├── workshop_quality.py
│   ├── workshop_removed_component.py
│   └── workshop_billing_proposal.py
├── security/
│   ├── workshop_groups.xml
│   ├── ir.model.access.csv
│   └── workshop_rules.xml
├── data/
│   └── workshop_sequence.xml
├── views/
│   ├── workshop_menus.xml
│   ├── workshop_order_views.xml
│   ├── workshop_procedure_views.xml
│   ├── workshop_equipment_views.xml
│   ├── workshop_repair_type_views.xml
│   └── workshop_billing_views.xml
├── tests/
│   ├── __init__.py
│   ├── test_procedure_versioning.py
│   ├── test_workshop_order.py
│   ├── test_workshop_quality.py
│   ├── test_workshop_stock.py
│   └── test_workshop_billing.py
└── README.md
```

La estructura puede simplificarse o ajustarse cuando exista una razón técnica. No se crearán archivos vacíos ni capas adicionales para anticipar funcionalidades futuras.

`README.md` debe explicar instalación, dependencias, configuración mínima, pruebas y limitaciones conocidas. No sustituye la documentación funcional existente.

## 5. Responsabilidades de los componentes

### 5.1. Órdenes de trabajo

`workshop_order.py` será responsable de:

* Crear y gestionar órdenes.
* Validar transiciones entre estados.
* Controlar los requisitos de cada transición.
* Mantener fechas y trazabilidad.
* Aplicar las reglas de cancelación, terminación, entrega y cierre.
* Coordinar las operaciones con los demás modelos.

Las acciones importantes deben implementarse como métodos de modelo explícitos, con nombres coherentes y validaciones del lado del servidor.

No debe existir lógica crítica únicamente en botones, vistas o JavaScript.

### 5.2. Procedimientos y versiones

`workshop_procedure.py` será responsable de los procedimientos, sus versiones y las líneas de definición.

Debe implementar:

* Creación de borradores.
* Validación previa a publicación.
* Publicación controlada.
* Inmutabilidad de versiones publicadas.
* Retirada de versiones.
* Composición mediante referencias a versiones concretas.
* Prevención de ciclos en procedimientos compuestos.

La aplicación de un procedimiento a una orden debe generar líneas ejecutables con una copia de los datos necesarios para conservar el significado histórico.

### 5.3. Ejecución de líneas

`workshop_order_line.py` gestionará:

* Líneas procedentes de procedimientos y líneas manuales.
* Cantidades previstas y reales.
* Estado de ejecución.
* Tiempos previstos y reales, cuando correspondan.
* Sustituciones y autorizaciones necesarias.
* Trazabilidad de los movimientos de inventario relacionados.

No debe calcular automáticamente la facturación a partir de la mera existencia de una línea.

### 5.4. Calidad

`workshop_quality.py` gestionará los intentos de pruebas y sus resultados.

Debe garantizar:

* Conservación de todos los intentos.
* Identificación inequívoca del resultado vigente.
* Validación de pruebas obligatorias y bloqueantes al terminar técnicamente.
* Registro del usuario, fecha y observaciones.
* Conservación de las evidencias adjuntas cuando existan.

No se permitirá modificar el resultado histórico de un intento para ocultar un rechazo anterior.

### 5.5. Componentes retirados

`workshop_removed_component.py` registrará los componentes retirados y su clasificación.

La clasificación como reutilizable, desechado o pendiente de evaluación no debe crear automáticamente movimientos físicos ni cargos comerciales.

Si se requiere un movimiento de inventario, deberá ejecutarse mediante el flujo estándar correspondiente.

### 5.6. Propuestas comerciales

`workshop_billing_proposal.py` gestionará la propuesta revisable de conceptos facturables.

Debe:

1. Preparar una propuesta a partir de la ejecución real.
2. Permitir revisión y ajustes por usuarios autorizados.
3. Registrar quién confirma y cuándo.
4. Crear o actualizar los documentos comerciales mediante las API estándar correspondientes.
5. Evitar duplicaciones si la operación se reintenta.
6. Conservar la relación entre la propuesta, la orden y los documentos comerciales generados.

La propuesta no debe crear facturas directamente ni sustituir los controles de Ventas y Contabilidad.

## 6. Seguridad y permisos

La seguridad se implementará desde el inicio. No se dejará como una tarea final de presentación.

### 6.1. Grupos propuestos

| Grupo                    | Responsabilidad principal                                                               |
| ------------------------ | --------------------------------------------------------------------------------------- |
| Técnico de taller        | Consultar órdenes asignadas y registrar ejecución, cantidades y pruebas según permisos. |
| Supervisor de taller     | Gestionar órdenes y autorizar operaciones de su ámbito.                                 |
| Gestor de procedimientos | Crear, modificar, validar, publicar y retirar procedimientos según permisos.            |
| Administrador del módulo | Configuración y administración técnica del módulo.                                      |

La pertenencia a varios grupos debe funcionar de forma coherente con los permisos estándar de Odoo.

### 6.2. Reglas obligatorias

* Definir permisos de lectura, creación, modificación y eliminación mediante ACL.
* Añadir reglas de registro cuando sean necesarias para compañía y ámbito de acceso.
* Validar autorizaciones en las acciones del servidor.
* Restringir los costes internos mediante permisos adecuados de modelos y campos, además de las vistas.
* Evitar que un técnico pueda publicar procedimientos o confirmar operaciones comerciales si no está autorizado.
* Restringir las correcciones posteriores al cierre.
* No permitir que una configuración de usuario desactive los controles críticos.

Ocultar un botón o un campo no constituye una medida de seguridad suficiente.

Las reglas de compañía deben ser coherentes entre órdenes, equipos, procedimientos, movimientos y propuestas comerciales. El MVP no implementará aislamiento avanzado de múltiples instalaciones, pero tampoco ignorará las comprobaciones estándar de compañía de Odoo.

## 7. Integración con Inventario

### 7.1. Autoridad de los movimientos

Las cantidades previstas y reales se registran en las líneas de la orden. Los movimientos físicos se registran en los modelos estándar de Stock.

No deben crearse tablas propias para reproducir el estado de un movimiento de inventario.

### 7.2. Diferencias entre operaciones

El módulo debe distinguir entre:

* Material previsto en el procedimiento.
* Cantidad realmente utilizada.
* Cantidad retirada físicamente del almacén.
* Material reservado.
* Material devuelto.
* Material no inventariable.

No se debe asumir que estas cantidades son iguales.

### 7.3. Reglas de integración

* Utilizar productos y unidades de medida estándar.
* Validar la compatibilidad de unidades y las reglas de precisión.
* Utilizar los mecanismos estándar para reservas y movimientos.
* Registrar la relación entre la orden y los movimientos que le corresponden.
* No descontar físicamente materiales solo por crear una orden o aprobar un presupuesto.
* No convertir consumibles no inventariables en movimientos ficticios.
* Registrar las cantidades reales según los requisitos funcionales.
* Gestionar devoluciones mediante el flujo estándar de inventario.
* Respetar lotes y números de serie cuando correspondan.
* No modificar directamente los estados internos de movimientos completados.

Las API concretas de creación, reserva, validación y devolución se comprobarán en el código de Odoo 20. No se copiarán métodos de versiones anteriores sin verificarlos.

### 7.4. Reservas y cancelaciones

La reserva configurable en la aprobación del presupuesto debe permanecer diferenciada del consumo físico.

Al cancelar una orden, los movimientos que todavía no se hayan completado deben tratarse según su estado y las reglas estándar. Los movimientos completados no se borran ni revierten de manera implícita.

## 8. Integración comercial

### 8.1. Generación de la propuesta

Al completar el trabajo técnico, el sistema preparará una propuesta revisable de conceptos facturables.

La propuesta se basará en los datos reales de ejecución y en las reglas comerciales acordadas. La relación entre una línea ejecutada y un concepto facturable debe poder trazarse.

No todos los materiales utilizados o componentes retirados deben convertirse automáticamente en cargos.

### 8.2. Confirmación

Solo un usuario autorizado podrá confirmar la propuesta.

La confirmación utilizará los modelos y mecanismos estándar de Ventas para crear o actualizar el pedido y sus líneas, cuando corresponda.

### 8.3. Idempotencia

La confirmación debe diseñarse para evitar duplicaciones en reintentos, errores de conexión o acciones repetidas.

La implementación debe comprobar si ya existe un documento comercial relacionado antes de crear otro. No debe confiar exclusivamente en deshabilitar temporalmente un botón.

### 8.4. Facturación y pagos

Las facturas, impuestos, monedas, redondeos y pagos se gestionarán con las funcionalidades estándar de Odoo.

La entrega con saldo pendiente se controlará mediante la configuración y las validaciones de negocio aprobadas. No se implementará un sistema paralelo de contabilidad.

## 9. Seguimiento y auditoría

Se utilizarán `mail.thread`, seguimiento de campos y el chatter cuando aporten trazabilidad útil.

El chatter no sustituye los registros estructurados de:

* Aceptación del presupuesto.
* Cambios de estado.
* Aplicación de procedimientos.
* Intentos de calidad.
* Consumos y devoluciones.
* Autorizaciones.
* Confirmación comercial.
* Correcciones posteriores al cierre.

Cada operación crítica debe conservar los datos necesarios para reconstruir qué ocurrió, cuándo y quién fue responsable.

No se almacenarán datos duplicados únicamente para mostrar mensajes informativos.

## 10. Interfaz de usuario

La primera versión tendrá interfaces funcionales y sencillas.

### Órdenes de trabajo

Debe permitir:

* Consultar órdenes y filtrar por estado, cliente, técnico, fechas y tipo.
* Registrar la recepción y el diagnóstico.
* Preparar y registrar la aceptación del presupuesto.
* Aplicar procedimientos.
* Registrar ejecución y cantidades reales.
* Registrar pruebas de calidad.
* Consultar movimientos relacionados.
* Preparar y revisar propuestas comerciales.
* Ejecutar las acciones de terminación, entrega, cierre y cancelación autorizadas.

### Procedimientos

Debe permitir:

* Crear y editar borradores.
* Definir líneas y cantidades.
* Componer procedimientos.
* Validar y publicar versiones.
* Consultar versiones anteriores.
* Retirar versiones sin destruir su historial.

### Equipos y tipos de reparación

Se proporcionarán vistas sencillas para gestionar los equipos registrados y la configuración por tipo de reparación.

### Propuestas comerciales

Debe ser posible revisar los conceptos propuestos, identificar sus fuentes, confirmar la propuesta y consultar el pedido relacionado.

La interfaz no debe exponer información sensible a usuarios no autorizados ni sustituir las validaciones del servidor.

## 11. Pruebas técnicas y funcionales

Las pruebas deben acompañar a la implementación, no dejarse para el final.

### 11.1. Versionado de procedimientos

Verificar que:

* Una versión en borrador puede editarse.
* Una versión publicada no puede alterarse mediante operaciones ordinarias.
* Una aplicación conserva la versión utilizada.
* Cambiar una plantilla no modifica las órdenes existentes.
* Los procedimientos compuestos conservan las versiones de sus componentes.
* Se rechazan referencias circulares.

### 11.2. Órdenes y estados

Verificar que:

* Las transiciones válidas funcionan.
* Las transiciones inválidas se rechazan en el servidor.
* La terminación respeta las pruebas bloqueantes.
* La cancelación exige el motivo correspondiente.
* Las correcciones posteriores al cierre están restringidas.
* La prioridad urgente no omite controles.

### 11.3. Inventario

Verificar que:

* Las cantidades previstas y reales son independientes.
* Las reservas no se confunden con consumos.
* Los movimientos completados conservan su integridad.
* Las devoluciones utilizan el mecanismo estándar.
* Se respetan las unidades de medida, los lotes y las series aplicables.

### 11.4. Seguridad

Verificar permisos de técnico, supervisor, gestor de procedimientos y administrador.

Las pruebas deben comprobar las operaciones del servidor, no únicamente la visibilidad de botones.

### 11.5. Propuestas comerciales

Verificar que:

* La propuesta puede revisarse antes de confirmarse.
* Los conceptos conservan su trazabilidad.
* La confirmación exige autorización.
* Los reintentos no duplican documentos ni líneas.
* La facturación continúa utilizando el flujo estándar de Odoo.

Las pruebas se ejecutarán contra una instalación de Odoo 20 compatible con las dependencias declaradas.

## 12. Reglas para los agentes de desarrollo

Los agentes que implementen el módulo deberán cumplir lo siguiente:

1. Trabajar exclusivamente en el alcance de la tarea asignada.
2. Leer la especificación funcional y los documentos de diseño relevantes antes de modificar código.
3. No cambiar requisitos, estados, permisos o reglas de negocio sin autorización.
4. No introducir dependencias adicionales sin justificación.
5. Verificar las API contra el código de Odoo 20.
6. Mantener cambios pequeños, revisables y verificables.
7. Añadir pruebas para las reglas críticas implementadas.
8. No afirmar que una función está terminada si no se ha probado.
9. Informar de incompatibilidades, ambigüedades y decisiones pendientes en lugar de improvisar.
10. No modificar documentos ajenos a la tarea asignada.
11. No introducir abstracciones, automatizaciones ni módulos adicionales que no estén justificados por el MVP.
12. Mantener la trazabilidad de los cambios y seguir el flujo Git establecido por el proyecto.

## 13. Secuencia recomendada de implementación

La implementación se dividirá en incrementos pequeños:

1. **Esqueleto instalable:** manifiesto, imports, modelos mínimos, grupos y secuencia.
2. **Procedimientos versionados:** definición, validación, publicación, composición y pruebas.
3. **Órdenes y ejecución:** ciclo de estados, líneas ejecutables y aplicación de procedimientos.
4. **Calidad:** intentos, resultados vigentes y bloqueos de terminación.
5. **Inventario:** relación con movimientos, consumos, reservas y devoluciones.
6. **Propuestas comerciales:** revisión, confirmación e integración con Ventas.
7. **Interfaz y reportes básicos:** vistas funcionales y filtros acordados.
8. **Validación integral:** instalación limpia, permisos, pruebas de regresión y documentación.

No se debe iniciar un incremento si sus dependencias funcionales y técnicas no están satisfechas. Cada incremento debe dejar el módulo en un estado comprobable.

## 14. Criterios de aceptación arquitectónica

La arquitectura estará lista para guiar la implementación cuando:

* El núcleo propio esté claramente separado de los modelos estándar de Odoo.
* Las dependencias sean explícitas y justificadas.
* Las reglas críticas se validen en el servidor.
* La seguridad se aplique mediante mecanismos estándar.
* Los procedimientos versionados y las líneas ejecutables conserven el historial.
* Inventario y documentos comerciales permanezcan bajo la autoridad de Odoo.
* Exista una secuencia incremental de desarrollo y pruebas.
* Los agentes tengan instrucciones claras para detenerse y consultar cuando falte una decisión funcional.

## 15. Limitaciones y decisiones pendientes de verificación

Este documento no certifica que el módulo ya sea instalable ni que todas las API descritas estén verificadas en Odoo 20.

Durante la implementación se deberán comprobar:

* Las dependencias definitivas del manifiesto.
* Las firmas y el comportamiento de las API de Stock y Ventas.
* Los mecanismos concretos para proteger versiones publicadas.
* Los permisos efectivos sobre campos sensibles.
* La estrategia exacta de sincronización con pedidos de venta existentes.
* La compatibilidad de las pruebas con la instalación real.

Cualquier hallazgo técnico debe documentarse y resolverse sin reabrir decisiones funcionales cerradas, salvo que se demuestre una incompatibilidad que requiera consultar al responsable del proyecto.
