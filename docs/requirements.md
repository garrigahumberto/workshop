# Requisitos del producto

**Producto:** versión preliminar del módulo Workshop para Odoo 20 Community
**Estado:** baseline de trabajo para implementación y validación con el negocio. Las decisiones marcadas como pendientes no deben resolverse por suposición.

## 1. Objetivo y prioridad

Workshop debe permitir seguir una reparación desde la recepción hasta el cierre, identificar quién atendió al cliente, qué servicios se realizaron y qué componentes se utilizaron, y relacionar el trabajo con las operaciones existentes de Odoo. Debe aportar utilidad desde una configuración sencilla, sin exigir que el negocio adopte un proceso administrativo más complejo que el que ya realiza.

Orden de prioridad:

1. Mantener una orden fácil de abrir y actualizar durante el trabajo.
2. Conservar información confiable sobre atención, ubicación, mano de obra y componentes.
3. Evitar duplicar ventas, inventario, facturación o caja de Odoo.
4. Preservar historial suficiente para que gerencia pueda reconstruir qué pasó.
5. Permitir mejorar procedimientos sin alterar órdenes anteriores.

## 2. Usuarios y responsabilidades

Una persona puede tener más de una responsabilidad. El sistema no debe exigir cuentas de usuario distintas por función.

- **Atención/recepción:** crea la orden y registra quién recibió al cliente.
- **Tienda:** registra la venta de productos mediante Odoo y puede relacionarla con una orden de instalación o servicio.
- **Técnico:** registra la ejecución y los servicios de mano de obra que realiza.
- **Responsable de tienda o taller:** mantiene la ubicación y supervisa los registros de su ámbito.
- **Gerencia:** consulta actividad, responsables, servicios, componentes relacionados y operaciones comerciales enlazadas.
- **Almacén:** realiza las operaciones de existencias y asignaciones mediante Odoo.

## 3. Requisitos funcionales

### 3.1 Orden y recorrido

| ID | Requisito | Aceptación |
|---|---|---|
| RF-01 | El sistema permitirá abrir una orden de servicio desde una tienda o directamente desde un taller. | Se puede crear una orden por ambas vías y se conserva su origen. |
| RF-02 | Cada orden identificará al cliente cuando se conozca, el artículo o equipo atendido con los datos disponibles, la tienda o taller responsable y la persona que recibió al cliente. | Se puede localizar la orden sin número de serie; ubicación y responsable de recepción son consultables. |
| RF-03 | Los campos no conocidos en recepción —como diagnóstico completo o producto concreto— podrán completarse después; no impedirán abrir la orden. | Una orden básica se crea con la información mínima disponible y admite completar los datos durante la ejecución. |
| RF-04 | La orden tendrá solo tres estados operativos principales: abierta, cerrada y cancelada. El archivado será un indicador administrativo, no un estado de trabajo. | No se requieren estados separados para diagnóstico, presupuesto, aprobación, servicio, terminación, entrega o cobro. Una orden archivada conserva su estado e historial. |
| RF-05 | La orden conservará fechas y eventos relevantes de recepción, presupuesto si lo hubo, ejecución, entrega y cierre. Estos datos no obligarán a realizar transiciones separadas. | Se pueden consultar hitos que ocurrieron sin que el usuario tenga que completar pasos vacíos o duplicar información. |
| RF-06 | Una orden cerrada podrá reabrirse por garantía o retrabajo, conservando su historial de cierre, usuario, fecha y motivo de reapertura. | La reapertura no elimina ni sobrescribe los datos previos; se identifica si fue por garantía o retrabajo. |
| RF-07 | La orden permitirá cancelar un trabajo, conservando quién lo canceló, cuándo y un motivo breve. | La orden cancelada sigue consultable y sus registros relacionados no se borran. |
| RF-08 | El usuario podrá registrar observaciones de recepción, diagnóstico y trabajo realizado sin duplicar la misma información en campos obligatorios distintos. | Se puede empezar con una nota de recepción y completar diagnóstico o ejecución cuando se conozcan. |

### 3.2 Ubicaciones, responsables y mano de obra

| ID | Requisito | Aceptación |
|---|---|---|
| RF-09 | El sistema permitirá configurar y seleccionar una o varias tiendas y uno o varios talleres como ubicaciones operativas. | Cada orden y registro de servicio identifica la ubicación correspondiente. |
| RF-10 | El sistema permitirá registrar quién atendió al cliente, independientemente de quién ejecutó el trabajo. | La consulta de la orden identifica a la persona de recepción. |
| RF-11 | Cada servicio de mano de obra podrá indicar la persona que lo ejecutó. No se exigirá registrar inicio, fin ni duración por tarea. | Una reparación con varios servicios puede atribuir cada servicio a su responsable, sin partes horarios obligatorios. |
| RF-12 | Los componentes compartidos podrán quedar atribuidos al taller o equipo responsable, sin exigir un único trabajador como responsable individual del material. | Un componente utilizado queda asociado a la orden y ubicación, aunque el trabajo de materiales fuera compartido. |

### 3.3 Componentes, materiales y movimientos

| ID | Requisito | Aceptación |
|---|---|---|
| RF-13 | La orden permitirá registrar componentes identificables utilizados, incluyendo producto y cantidad cuando corresponda. | La gerencia puede consultar los componentes relacionados con la reparación. |
| RF-14 | Si un componente se vendió previamente en tienda, la orden podrá relacionarse con la venta existente de Odoo. La relación no volverá a vender ni descontar el componente. | Una instalación posterior a una venta conserva un único cargo y una única salida de existencias para esa venta. |
| RF-15 | Un componente retirado directamente de existencias para una reparación deberá vincularse con la operación de inventario estándar que corresponda, evitando descontarlo dos veces. | La orden se puede reconciliar con el movimiento real; no se modifican cantidades de existencias directamente desde Workshop. |
| RF-16 | El sistema permitirá registrar materiales gastables utilizados en una orden y distinguirlos de componentes individualizados. | El uso informativo por reparación no provoca una segunda salida si el material fue asignado periódicamente al taller. |
| RF-17 | Una asignación periódica de materiales gastables a un taller deberá reflejar la salida de la disponibilidad central mediante el mecanismo estándar de inventario aprobado para la instalación. Las órdenes podrán registrar su uso sin volver a descontar esos materiales. | La asignación es trazable por producto, cantidad, fecha y taller; las anotaciones de uso en órdenes no crean otra salida. |
| RF-18 | Workshop no creará movimientos ficticios para materiales que no se controlan mediante existencias. | Los materiales descriptivos se pueden registrar sin alterar inventario. |
| RF-19 | La cantidad realmente utilizada podrá diferir de una cantidad orientativa sin cambiar el procedimiento y sin pedir autorización solo por excederla. | La orden conserva la cantidad de referencia y la cantidad real por separado cuando ambas sean aplicables. |

### 3.4 Procedimientos de servicio

| ID | Requisito | Aceptación |
|---|---|---|
| RF-20 | Un responsable podrá crear procedimientos en borrador, publicarlos y reutilizarlos desde la interfaz. Una revisión publicada no se editará; una modificación permanente se publicará como otro registro. No será necesario configurar todos los servicios antes de usar Workshop. | Se puede abrir y completar una orden sin procedimiento; una definición publicada conserva su contenido. |
| RF-21 | Cada definición publicada de procedimiento se identificará mediante un código estable y una revisión visible, por ejemplo `CAM-ACEITE-001` y `CAM-ACEITE-002`. Cada revisión será un registro identificable por su propio ID; no se exigirá al usuario gestionar una entidad de versión separada. | Se pueden consultar ambas revisiones como evolución histórica del mismo servicio y aplicar una revisión concreta a una orden. |
| RF-22 | Una revisión publicada no se modificará para cambiar el servicio. Para cambios permanentes se creará una nueva revisión, preservando las anteriores. | Órdenes previas conservan exactamente la revisión aplicada; las órdenes nuevas pueden usar la revisión vigente. |
| RF-23 | Una orden podrá cambiar la cantidad real, omitir una línea opcional o añadir un trabajo/material puntual sin alterar la revisión publicada. | Una desviación de una orden no cambia otras órdenes ni la definición reutilizable. |
| RF-24 | Un adicional puntual podrá anotarse en la orden. Si un cambio se vuelve una práctica permanente, un responsable podrá incorporarlo a una nueva revisión del procedimiento. | El uso extra de aceite en un caso no fuerza una nueva revisión; un cambio permanente de producto o tareas puede publicarse como revisión nueva. |
| RF-25 | El procedimiento podrá describir operaciones, materiales/componentes, servicios de mano de obra, instrucciones y cantidades de referencia. La aplicación copiará esos datos a la orden para preservar el historial. | Una orden histórica mantiene sus datos aunque se edite o archive el procedimiento. |
| RF-26 | Para un mismo código base, la revisión publicada más reciente será la opción predeterminada en órdenes nuevas. Las revisiones anteriores se conservan para historial, no como opciones rutinarias. Si dos variantes deben seguir utilizándose simultáneamente, no se elegirá automáticamente una revisión histórica como si fuera vigente. | Al aplicar un procedimiento nuevo se propone la revisión vigente y se conserva su identidad; una revisión antigua no se selecciona por defecto. |

### 3.5 Comercial y caja

| ID | Requisito | Aceptación |
|---|---|---|
| RF-27 | La orden podrá relacionarse con ventas, facturas o cobros existentes en Odoo cuando estén asociados al servicio. | Desde la orden se puede identificar el documento comercial correspondiente y desde el vínculo entender qué servicio cubre. |
| RF-28 | Workshop no mantendrá una caja paralela ni sustituirá punto de venta, ventas, facturación o contabilidad de Odoo. | El cierre diario de caja se realiza con la herramienta estándar de Odoo; Workshop no crea un saldo de caja independiente. |
| RF-29 | La venta de un componente y el cobro de mano de obra podrán ser operaciones distintas y ambas relacionarse con el mismo servicio cuando corresponda. | El componente vendido no se cobra de nuevo al facturar el servicio de instalación. |
| RF-30 | Un presupuesto, su aceptación y los cambios de importe podrán registrarse cuando el negocio los utilice, sin exigirlos universalmente para abrir o ejecutar una orden. | Un servicio sin presupuesto formal puede completarse; cuando se registra un acuerdo, queda consultable. |
| RF-31 | Registrar ejecución, consumo o movimiento físico no genera por sí solo un cargo. Los documentos comerciales se originan o actualizan por el proceso comercial autorizado de Odoo. | Las pruebas verifican que registrar datos de ejecución no duplica cargos. |

### 3.6 Historial, consulta y seguridad

| ID | Requisito | Aceptación |
|---|---|---|
| RF-32 | El sistema conservará el historial de reaperturas, cancelaciones y cambios relevantes, identificando usuario y fecha automáticamente. | Una revisión gerencial permite distinguir el estado actual y los eventos previos sin depender de notas manuales. |
| RF-33 | Gerencia podrá consultar y filtrar órdenes por número, cliente, ubicación, estado, persona de recepción, técnico, fecha, servicios y productos relacionados. | Los filtros devuelven órdenes coherentes y no exigen campos que el negocio no registre. |
| RF-34 | El acceso a órdenes y datos comerciales se controlará en servidor según permisos; ocultar un botón no será suficiente. | Un usuario no autorizado no puede leer ni cambiar datos fuera de su permiso usando una llamada directa al modelo. |
| RF-35 | El registro de usuario/fecha y la copia histórica de datos se realizará automáticamente siempre que el sistema pueda hacerlo. | El usuario no vuelve a capturar datos de auditoría que Odoo o Workshop puedan asignar automáticamente. |

## 4. Exclusiones de la versión preliminar

- Reemplazar la aplicación de inventario, Punto de Venta, Ventas, Facturación, Contabilidad o caja de Odoo.
- Un sistema propio de facturación, pagos o conciliación de caja.
- Estados obligatorios para cada etapa de diagnóstico, presupuesto, aprobación, ejecución, entrega y cobro.
- Partes horarios detallados por tarea.
- Aprobaciones manuales por cada exceso de cantidad o adicional menor.
- Configuración avanzada de reglas por tipo de reparación.
- Subprocedimientos, automatización condicional y planificación de capacidad.
- Informes avanzados de costos, márgenes, productividad o rentabilidad.
- Notificaciones automáticas e integraciones con plataformas externas.
- Pruebas de calidad configurables y flujos metrológicos avanzados, salvo que el responsable del producto priorice un caso bloqueante concreto.
- Aislamiento multiempresa. Las ubicaciones de varias tiendas y talleres operan dentro de una instalación/empresa, con inventario compartido conforme a la configuración estándar de Odoo.

## 5. Criterios de aceptación de la versión preliminar

La versión preliminar demuestra utilidad cuando los siguientes escenarios funcionan de extremo a extremo:

1. **Venta más instalación:** se vende un repuesto en la tienda, se abre o relaciona una orden de instalación, se registra quién recibió al cliente y quién hizo el servicio; el repuesto no se cobra ni descuenta por segunda vez.
2. **Servicio directo:** el cliente llega al taller para un mantenimiento sin repuestos; se crea la orden, se registran los servicios y responsables, se entrega y se relaciona el cobro existente si lo hubo.
3. **Componente usado en taller:** un componente retirado de existencias se vincula a la orden y al movimiento estándar correspondiente, sin modificar inventario directamente.
4. **Consumible asignado:** una asignación de material gastable a un taller afecta la disponibilidad central una vez; anotarlo en varias órdenes no repite ese descuento.
5. **Variación puntual:** el consumo real excede la referencia o se añade una tarea puntual; la orden conserva el resultado sin cambiar el procedimiento.
6. **Cambio permanente:** se publica una nueva revisión del procedimiento; las órdenes antiguas siguen mostrando la revisión anterior.
7. **Reapertura:** una orden cerrada se reabre por garantía o retrabajo, conservando el cierre previo, motivo, usuario y fechas.
8. **Conciliación:** gerencia puede recorrer de una orden al documento de venta/facturación enlazado y confirmar que Workshop no duplicó el cargo ni mantuvo caja propia.

## 6. Decisiones pendientes que no deben inventarse

Antes de cerrar el diseño detallado o implementar la operación afectada, el responsable debe confirmar:

1. Qué documento de Odoo se vincula a la orden en una venta de tienda que luego requiere instalación, y si el vínculo se hace con el pedido, la sesión/orden de Punto de Venta, el ticket o sus líneas.
2. Qué operación estándar de inventario debe usarse para componentes tomados directamente para una reparación.
3. Si asignar consumibles al taller significa moverlos a una ubicación interna del taller, consumirlos contra una ubicación de producción/gasto u otra operación estándar; no se debe simular una pérdida de existencias.
4. Si se permite cerrar una orden con cobro pendiente y qué significa “cerrada” administrativamente.
5. Cómo representar variantes de un servicio que deban seguir vigentes simultáneamente: códigos distintos o alternativas explícitas dentro de un procedimiento.
6. Si el cliente puede llevar varios artículos en una sola recepción y cómo se agrupan sus órdenes.
7. Qué permisos mínimos distinguen recepción, técnico, tienda, almacén y gerencia.

Las integraciones de inventario, Punto de Venta y facturación deben comprobarse en la instalación real de Odoo 20 Community antes de declarar una API disponible o completar el flujo.
