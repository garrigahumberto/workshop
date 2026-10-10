# Modelo conceptual de datos
## Módulo de gestión de servicios y talleres para Odoo 20 Community

**Estado:** Propuesta conceptual v0.1  
**Fecha:** 8 de octubre de 2026  
**Propósito:** Definir las entidades de negocio, sus responsabilidades y relaciones antes del diseño técnico y la implementación.

---

## 1. Objetivo y principios

El módulo permitirá gestionar servicios y trabajos de talleres de distintos tipos mediante procedimientos configurables, órdenes de trabajo, registro del consumo real, integración con inventario y documentos comerciales de Odoo.

Principios de diseño:

1. **Procedimiento y ejecución son entidades distintas.** El procedimiento es una definición reutilizable; la orden registra lo que ocurrió en un trabajo concreto.
2. **El historial no cambia retroactivamente.** Las órdenes conservan la versión de procedimiento y los datos comerciales que se utilizaron.
3. **Las modificaciones de una orden son locales.** Agregar, retirar o sustituir líneas durante un trabajo no altera el procedimiento ni otras órdenes.
4. **El inventario refleja el consumo real.** Las cantidades previstas sirven como referencia; las salidas de stock se basan en lo efectivamente consumido.
5. **Los precios acordados se preservan.** Los cambios posteriores en los precios del catálogo no reescriben importes ya acordados en una orden.
6. **Se reutiliza Odoo.** Productos, categorías, unidades de medida, existencias, movimientos, contactos, ventas, facturas y pagos se apoyarán en los modelos estándar adecuados. El módulo no duplicará esas entidades sin una necesidad comprobada.
7. **Configuración desde la interfaz.** El gerente podrá mantener procedimientos y sus versiones sin solicitar programación para cada nuevo servicio.
8. **Una instalación por empresa.** No se requiere aislamiento multiempresa dentro de una misma instalación.
9. **Diseño incremental.** El modelo conceptual no implica implementar todas las entidades en el primer incremento.

## 2. Alcance funcional

El módulo contempla:

- Procedimientos de servicio reutilizables, versionados y publicables por el gerente.
- Procedimientos compuestos por líneas de materiales, componentes descriptivos, consumibles, servicios y otros procedimientos.
- Órdenes de trabajo basadas en uno o varios procedimientos, o creadas libremente.
- Identificación del cliente y del equipo o activo atendido, cuando corresponda.
- Diagnóstico, ejecución, estados, asignación de técnicos y evidencias opcionales.
- Selección del producto comercial concreto a partir de una descripción y una categoría de producto.
- Registro separado de cantidades previstas y cantidades realmente utilizadas.
- Registro de trabajos, materiales y servicios adicionales no previstos.
- Integración con movimientos de inventario, ventas, facturación y cobros.
- Control de acceso por roles y trazabilidad de operaciones.

## 3. Entidades conceptuales

### 3.1 Procedimiento de servicio

Representa una definición reutilizable de un trabajo, por ejemplo, «Mantenimiento eléctrico de moto».

**Atributos conceptuales:**

- Identificador.
- Nombre y descripción.
- Categoría o familia de servicio.
- Tipos de equipo o ámbito de aplicación, cuando se configure.
- Estado: borrador, publicado, archivado.
- Versión publicada vigente.
- Responsable de la definición.
- Fechas de creación y modificación.

Un procedimiento tiene una identidad estable y una o varias versiones. No se modifica una versión publicada que ya pueda ser utilizada por órdenes históricas: el gerente prepara y publica una versión nueva de forma expresa.

### 3.2 Versión de procedimiento

Es una definición inmutable publicada de un procedimiento.

**Atributos conceptuales:**

- Procedimiento al que pertenece.
- Número o identificador de versión.
- Estado de publicación.
- Fecha de publicación.
- Usuario que preparó y usuario que publicó.
- Notas del cambio.
- Líneas que forman parte de esa versión.

Una orden basada en un procedimiento debe referenciar la versión concreta que se aplicó. La publicación de una versión nueva no cambia las órdenes anteriores.

### 3.3 Línea de procedimiento

Define un elemento previsto dentro de una versión de procedimiento.

**Tipos conceptuales de línea:**

- Componente o material descriptivo.
- Consumible.
- Servicio o mano de obra.
- Subprocedimiento.
- Instrucción u otro elemento de trabajo, si se justifica durante el diseño detallado.

**Atributos conceptuales:**

- Descripción que permita reconocer qué se necesita.
- Tipo de línea.
- Categoría de producto asociada, cuando corresponda.
- Cantidad prevista o valor de referencia.
- Unidad de medida.
- Carácter obligatorio u opcional.
- Cantidad mínima o máxima, si aplica.
- Instrucciones y notas.
- Orden de presentación.
- Precio de venta de referencia, cuando corresponda y se defina para esa línea.

La línea descriptiva no tiene que identificar una marca o referencia comercial específica. Por ejemplo, puede indicar «Batería de 12 V» y asociarse a la categoría correspondiente. El producto concreto se selecciona durante la ejecución.

La versión publicada de un procedimiento y sus líneas no se alteran al ejecutar una orden.

### 3.4 Relación entre procedimientos

Un procedimiento puede incluir otros procedimientos reutilizables, por ejemplo, «Mantenimiento eléctrico de moto» puede componerse de «Diagnóstico eléctrico», «Revisión de batería» y «Revisión de cableado».

La relación debe conservar la identidad del subprocedimiento y evitar ciclos de composición. Al crear una orden, se debe resolver y preservar la versión concreta de cada procedimiento subordinado utilizado. Los cambios posteriores de cualquiera de ellos no alterarán la ejecución histórica.

### 3.5 Orden de trabajo

Representa un servicio concreto prestado a un cliente.

**Atributos conceptuales:**

- Número único de orden.
- Cliente.
- Equipo o activo atendido, cuando corresponda.
- Fecha de recepción y fechas relevantes.
- Diagnóstico inicial.
- Falla encontrada.
- Trabajo realizado y observaciones.
- Técnico o responsables asignados.
- Estado del trabajo.
- Procedimientos aplicados y versiones correspondientes, si los hay.
- Líneas de ejecución.
- Evidencias opcionales.
- Referencias a presupuesto, pedido de venta, factura y cobro, cuando correspondan.

Una orden puede tener una de estas modalidades:

1. **Basada en procedimientos:** utiliza uno o varios procedimientos publicados.
2. **Libre:** se crea sin procedimiento predefinido y sus líneas se introducen durante el diagnóstico o la ejecución.

Ambas modalidades comparten el mismo flujo de trabajo, registro de materiales y servicios, controles de permisos, auditoría y conexión comercial.

### 3.6 Procedimiento aplicado

Representa la utilización de una versión de procedimiento dentro de una orden.

Conserva la referencia a la versión de origen y el contexto de aplicación. Si una orden utiliza varios procedimientos, cada uno tendrá su propio registro de aplicación.

Las modificaciones particulares realizadas durante la ejecución se registran en las líneas de la orden; no modifican el procedimiento de origen.

### 3.7 Línea de ejecución

Representa un material, producto, servicio, mano de obra, subtrabajo o adicional dentro de una orden.

**Atributos conceptuales:**

- Orden de trabajo.
- Procedimiento aplicado y línea de origen, si existe.
- Tipo de línea.
- Descripción histórica.
- Categoría de producto de referencia, si corresponde.
- Producto concreto seleccionado, cuando corresponda.
- Cantidad prevista, si procede.
- Cantidad real utilizada o ejecutada.
- Unidad de medida.
- Precio unitario acordado.
- Descuento e importe de línea, si corresponden.
- Indicador de elemento adicional no previsto.
- Motivo o nota del adicional, cuando corresponda.
- Estado de ejecución.
- Referencia al movimiento de inventario, lote o número de serie, si aplica.

La línea debe distinguir entre la descripción genérica que solicitaba el procedimiento y el producto concreto que terminó utilizándose. La selección del producto no modifica el procedimiento.

Para líneas de materiales, la cantidad real consumida es la base del descuento de inventario. Para líneas de servicio o mano de obra, se registra el trabajo ejecutado y su precio de venta. El costo interno de la mano de obra no se distribuye inicialmente por orden; se tratará posteriormente en la gestión laboral y contable correspondiente.

### 3.8 Adicionales no previstos

Los adicionales son líneas de ejecución incorporadas a una orden cuando se detectan necesidades que no estaban contempladas en el procedimiento o en la orden inicial.

Se registran separadamente de las líneas originadas en procedimientos, pero forman parte del importe final del trabajo. No exigen modificar el procedimiento.

El flujo comercial acepta que el presupuesto inicial sea orientativo y que puedan aparecer adicionales durante la ejecución. No se exigirá una nueva aprobación formal dentro del sistema por cada variación; el taller comunicará los cambios al cliente conforme a su práctica comercial.

### 3.9 Cliente

Se utilizará el modelo estándar de contactos de Odoo. La orden referenciará al cliente y no mantendrá una copia independiente de su ficha maestra.

### 3.10 Equipo o activo del cliente

Identifica el objeto atendido: vehículo, motocicleta, generador, computadora, máquina, electrodoméstico u otro equipo.

**Atributos conceptuales posibles:**

- Cliente propietario o responsable.
- Tipo y categoría de equipo.
- Marca, modelo y otros datos de identificación.
- Número de serie, placa u otro identificador.
- Observaciones e historial de servicios.

Un cliente puede tener varios equipos y un equipo puede acumular múltiples órdenes históricas. La necesidad de permitir cambios de propietario deberá definirse en el diseño detallado.

### 3.11 Evidencia

Permite adjuntar fotografías y documentos antes, durante o después del trabajo.

Las evidencias son opcionales y se relacionan con una orden o con una etapa concreta. Deben respetar los permisos de acceso y conservarse de acuerdo con la política de retención que se defina.

### 3.12 Auditoría

Registra las operaciones relevantes realizadas por usuarios.

Debe permitir identificar, según el tipo de operación:

- Usuario responsable.
- Fecha y hora.
- Entidad afectada.
- Acción realizada.
- Valores anteriores y nuevos, cuando sea necesario.
- Motivo de corrección, si corresponde.

El registro de auditoría debe cubrir las operaciones críticas del módulo y complementarse con los mecanismos estándar de Odoo donde resulten suficientes. Un historial visual genérico de cambios no sustituye la conservación explícita de versiones, precios acordados y cantidades ejecutadas.

## 4. Entidades estándar de Odoo que se reutilizarán

El diseño técnico debe comprobar los modelos y flujos disponibles en Odoo 20 Community antes de fijar nombres de modelos o relaciones.

| Necesidad | Fuente conceptual |
|---|---|
| Clientes y contactos | Contactos de Odoo |
| Productos y servicios comerciales | Productos de Odoo |
| Categorías de productos | Categorías de productos de Odoo |
| Unidades de medida y conversiones | Unidades de medida de Odoo |
| Existencias y movimientos reales | Inventario de Odoo |
| Lotes y números de serie | Trazabilidad estándar de Odoo |
| Pedidos de venta y precios comerciales | Ventas de Odoo, si se instala y valida |
| Facturas y pagos | Facturación/contabilidad disponibles en Community y configuradas para la instalación |
| Usuarios y grupos de acceso | Seguridad estándar de Odoo |

No se asumirá que una aplicación está instalada solo porque exista en el código fuente. Antes de implementar, se verificará qué módulos están disponibles, cuáles están instalados y qué restricciones tiene la distribución Community elegida.

## 5. Relaciones principales

- Un **procedimiento** tiene muchas **versiones**.
- Una **versión** tiene muchas **líneas de procedimiento**.
- Una **línea de procedimiento** puede referenciar una categoría de producto y, si corresponde, un subprocedimiento.
- Una **orden de trabajo** pertenece a un cliente y puede referenciar un equipo.
- Una **orden** contiene cero o muchos **procedimientos aplicados**; puede tener cero si es una orden libre.
- Cada **procedimiento aplicado** referencia la versión concreta utilizada.
- Una **orden** contiene muchas **líneas de ejecución**.
- Una **línea de ejecución** puede originarse en una línea de procedimiento o ser un adicional/línea libre.
- Una **línea de ejecución** puede referenciar un producto estándar de Odoo y el movimiento de inventario que materializa su consumo.
- Una **orden** puede tener muchas evidencias y registros de auditoría.
- Una **orden** puede enlazarse con documentos comerciales estándar, sin duplicar su información contable.

## 6. Reglas de integridad e historial

1. Una versión publicada de procedimiento no se edita directamente; cualquier cambio que deba convertirse en definición reutilizable se publica como una nueva versión por decisión expresa del gerente.
2. Una orden conserva la versión de cada procedimiento que aplicó.
3. Una modificación local de una orden no modifica procedimientos ni otras órdenes.
4. Los precios acordados en una orden no se actualizan automáticamente cuando cambia el precio del producto.
5. La descripción y los importes históricos necesarios deben conservarse aunque el producto o servicio del catálogo cambie posteriormente.
6. El inventario se descuenta según el consumo real confirmado, no según la cantidad prevista.
7. El consumo debe materializarse mediante movimientos trazables de inventario, evitando descontar existencias dos veces.
8. La selección de productos debe respetar las categorías y las unidades de medida compatibles.
9. Los lotes y números de serie se registran cuando el producto y la política de trazabilidad lo requieran.
10. Las correcciones de trabajos cerrados se harán mediante operaciones autorizadas y trazables, sin alterar silenciosamente el historial.
11. Los permisos de precio, costo, descuento, inventario, publicación de procedimientos y cierre de órdenes se aplicarán por rol.
12. La orden libre debe permitir ejecutar un servicio sin inventar un procedimiento permanente.

## 7. Estados conceptuales de la orden

Flujo inicial propuesto, sujeto a validación durante el diseño funcional:

**Solicitud → Diagnóstico → Presupuesto → Aprobado → En reparación → Terminado → Entregado → Cerrado**

Deben definirse las transiciones permitidas, quién puede realizarlas, cómo tratar órdenes canceladas y qué condiciones son necesarias para cerrar una orden. Los cambios de estado relevantes se auditarán.

El presupuesto inicial será orientativo. El documento comercial definitivo deberá reflejar los materiales realmente utilizados, los servicios ejecutados y los adicionales, no los materiales previstos que no se utilizaron.

## 8. Roles y permisos iniciales

- **Administrador:** administración técnica de la instalación y permisos de sistema.
- **Gerente:** control operativo y comercial del negocio, inventario, procedimientos y publicación de versiones.
- **Almacenero:** operaciones de almacén y trazabilidad de existencias.
- **Vendedor:** gestión comercial y modificación de precios/descuentos dentro de sus permisos.
- **Técnico:** consulta de procedimientos, diagnóstico, ejecución y registro de consumos y adicionales, sin acceso a costos internos por defecto.

Los permisos exactos para crear órdenes, seleccionar productos, proponer adicionales, editar precios, registrar consumos, validar movimientos y cerrar trabajos quedan por definir antes de la implementación.

## 9. Decisiones pendientes de diseño detallado

Estos puntos no deben resolverse mediante suposiciones del agente de código:

1. Política exacta para publicar versiones y tratar cambios de subprocedimientos compuestos.
2. Momento en que el consumo real se confirma y genera el movimiento de inventario.
3. Tratamiento de consumibles inventariables frente a gastos menores no controlados individualmente.
4. Fórmula del importe de líneas, descuentos, impuestos y redondeos según la configuración comercial de Odoo.
5. Cómo se representa y actualiza el presupuesto orientativo y cómo se generan los documentos comerciales finales.
6. Reglas exactas de permisos por rol.
7. Reglas para cancelaciones, devoluciones, garantías, retrabajos y correcciones posteriores.
8. Campos obligatorios del equipo del cliente según su tipo.
9. Tratamiento de productos sustitutos, números de serie, lotes y cantidades fraccionarias.
10. Aplicaciones y modelos concretos de Odoo 20 Community que se utilizarán, comprobados en el código real.

## 10. Criterios para aprobar el modelo conceptual

El modelo estará listo para pasar al diseño técnico cuando se confirme que:

- Separa claramente la definición reutilizable del trabajo ejecutado.
- Permite órdenes basadas en procedimientos y órdenes libres.
- Conserva las versiones históricas.
- Distingue componentes descriptivos de productos comerciales concretos.
- Registra cantidades previstas y reales sin alterar el procedimiento.
- Registra adicionales locales a una orden.
- Permite conservar precios acordados.
- Integra el consumo con movimientos reales de inventario.
- Soporta equipos de clientes, evidencias, estados, roles y auditoría.
- Reutiliza los modelos estándar de Odoo siempre que sea apropiado.
- No introduce dependencias innecesarias ni impone una arquitectura prematura.

---

**Siguiente fase:** inspeccionar la instalación y el código de Odoo 20 Community para contrastar este modelo con los modelos estándar disponibles. Después se diseñarán los modelos técnicos, relaciones, restricciones, permisos y pruebas del primer incremento. No se debe empezar a programar el módulo completo antes de esa validación.
