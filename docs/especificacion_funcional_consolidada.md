# Especificación funcional consolidada

## Módulo genérico de taller y servicios — Odoo 20 Community

**Estado:** Requisitos funcionales consolidados preliminarmente. Pendiente de validación técnica y definición del MVP definitivo.

## 1. Objetivo y alcance

Desarrollar un módulo reutilizable para gestionar reparaciones y servicios técnicos en talleres de automoción, electrónica, electricidad, maquinaria, electrodomésticos y otras actividades similares.

El elemento central será la **orden de trabajo**, apoyada por procedimientos de servicio reutilizables y versionados.

El sistema debe permitir estandarizar reparaciones mediante listas predefinidas de operaciones, componentes, materiales, consumibles y servicios, sin impedir que se registren trabajos manuales cuando no exista un procedimiento apropiado.

### Principios de diseño

* Utilizar Odoo 20 Community como plataforma.
* Reutilizar los modelos estándar cuando sean adecuados.
* Desarrollar modelos propios para las necesidades específicas del taller.
* Mantener separadas la gestión técnica, la logística de inventario y la gestión comercial y contable.
* Evitar duplicar la lógica de existencias, impuestos, facturación y contabilidad de Odoo.
* Mantener trazabilidad de las órdenes, procedimientos aplicados y correcciones.
* Evitar complejidad innecesaria y funcionalidades avanzadas fuera del MVP.

## 2. Orden de trabajo

Cada orden corresponderá a un artículo o equipo que deba repararse o recibir un servicio.

### Información principal

La orden podrá incluir:

* Número de orden.
* Cliente.
* Artículo o equipo, tipo de reparación, marca, modelo, número de serie y otros identificadores pertinentes.
* Equipo registrado del cliente, cuando exista.
* Técnico responsable único.
* Estado, prioridad y fechas relevantes.
* Diagnóstico y observaciones en texto libre.
* Presupuesto, aceptación del cliente y cambios autorizados.
* Procedimientos y versiones aplicados.
* Operaciones ejecutadas.
* Materiales, componentes, consumibles y servicios realizados.
* Pruebas de calidad, evidencias y documentos.
* Comunicaciones relacionadas con la orden.
* Historial de intervenciones vinculadas.
* Información de garantía, entrega y cierre.

Los campos de identificación serán opcionales según el caso. No se exigirá número de serie cuando el artículo no disponga de él.

### Varias órdenes por recepción

* Una recepción podrá agrupar varias órdenes.
* Cada artículo tendrá su propia orden.
* No se permitirá una única orden para reparar varios artículos distintos en el MVP.

### Lista principal de órdenes

La vista operativa mostrará número, cliente, artículo/equipo, tipo de reparación, estado, prioridad, técnico responsable, fecha prometida e indicador de retraso.

Se podrán filtrar y ordenar las órdenes por estos criterios.

## 3. Ciclo de vida

El flujo general propuesto es:

**Solicitud → Diagnóstico → Presupuesto → Aprobada → En reparación → Terminada → Entregada → Cerrada.**

También se contemplará la cancelación antes de la entrega, conservando la orden y su historial.

### Reglas de transición

* Las transiciones serán controladas y tendrán permisos definidos.
* Se podrán exigir datos, operaciones, consumos, autorizaciones o evidencias antes de avanzar.
* Los requisitos serán configurables según el tipo de reparación y la etapa.
* Las validaciones críticas de inventario, trazabilidad, permisos y auditoría no podrán omitirse mediante una simple configuración de urgencia.
* La exigencia de presupuesto y aceptación previa a la reparación será configurable.
* La prioridad podrá ser normal, alta o urgente. La urgencia solo modifica la priorización operativa, no las reglas de control.

### Terminación, entrega y cierre

Son hitos diferentes:

* **Terminada:** se han ejecutado los trabajos y confirmado los consumos; deben satisfacerse las validaciones aplicables.
* **Entregada:** se registra quién entrega, cuándo y la confirmación de recepción del cliente.
* **Cerrada:** se completa el cierre administrativo.

La firma del cliente será opcional por defecto, aunque podrá configurarse como obligatoria.

Las condiciones de pago podrán permitir la entrega con saldo pendiente o exigir un pago determinado antes de entregar.

### Cancelaciones

Se podrá cancelar una orden antes de la entrega, registrando el motivo y gestionando adecuadamente materiales retirados, trabajos realizados y movimientos de inventario. La orden cancelada conservará su historial.

## 4. Procedimientos de servicio

Esta será una de las funciones centrales y diferenciales del módulo.

Un procedimiento representará una plantilla estandarizada de un trabajo habitual, reutilizable en distintas órdenes.

### Contenido

Un procedimiento podrá incluir:

* Nombre, descripción y tipo de reparación.
* Instrucciones.
* Operaciones o tareas.
* Componentes y materiales.
* Consumibles.
* Servicios y mano de obra.
* Cantidades esperadas y unidades de medida.
* Líneas obligatorias u opcionales.
* Alternativas de componentes previamente autorizadas.
* Subprocedimientos.
* Pruebas de calidad.
* Requisitos de recepción y evidencias.
* Validaciones aplicables antes de completar determinadas etapas.

No habrá activación automática de líneas condicionada a otras líneas en el MVP.

### Aplicación a una orden

* Una orden podrá utilizar uno o varios procedimientos.
* También podrá crearse sin procedimiento, introduciendo manualmente operaciones, materiales, consumibles y servicios.
* Se podrán omitir las líneas opcionales.
* Las modificaciones realizadas en una orden no alterarán el procedimiento publicado.
* Se conservará la versión aplicada a la orden.
* Los subprocedimientos conservarán las versiones elegidas para esa ejecución.

### Versiones y publicación

* Los procedimientos tendrán versiones.
* Una versión publicada será inmutable.
* Cualquier modificación requerirá una nueva versión que deberá publicarse antes de utilizarse.
* Las órdenes existentes conservarán la versión que utilizaron.
* Los procedimientos podrán suspenderse, reactivarse o archivarse para impedir su uso en nuevas órdenes sin perder el historial.

### Permisos

Los administradores y responsables autorizados podrán crear, revisar y publicar procedimientos. Los técnicos podrán ejecutarlos, pero no modificar ni publicar sus versiones.

La importación y exportación utilizará las herramientas estándar de Odoo cuando sean compatibles con los modelos propios y sus validaciones.

## 5. Operaciones y pruebas de calidad

### Lista de operaciones

Cada procedimiento podrá incluir tareas que se registrarán en la orden como:

* Pendientes.
* Realizadas.
* No aplicables.

Se permitirán observaciones opcionales por tarea. Las tareas configuradas como obligatorias deberán completarse antes de avanzar cuando así lo establezca la validación de la etapa.

No habrá seguimiento detallado de inicio, fin, duración y responsable individual por tarea en el MVP.

### Pruebas de calidad

* Las pruebas podrán registrar resultado aprobado, rechazado o no aplicable.
* Podrán ser obligatorias y, además, bloqueantes.
* Una prueba rechazada bloqueará la finalización cuando esté configurada como obligatoria y bloqueante.
* Se podrán repetir pruebas y registrar el resultado final.
* Las pruebas y sus resultados quedarán asociados a la orden ejecutada, sin modificar el procedimiento publicado.
* No se incluirá un sistema avanzado de metrología, tolerancias o instrumentos en el MVP.

## 6. Materiales, componentes e inventario

La gestión logística se apoyará en los movimientos estándar de Odoo.

### Componentes y repuestos

* El inventario se descontará cuando el componente salga físicamente del almacén, aunque finalmente no se instale.
* Se podrán reservar componentes previstos al aprobar el presupuesto, si el taller activa esa opción.
* La reserva no descontará existencias.
* El sistema respetará el seguimiento estándar por lotes y números de serie cuando corresponda.
* Se podrán exigir requisitos adicionales de trazabilidad según el tipo de reparación o procedimiento.

### Consumibles

Se admitirán dos modalidades:

1. Consumibles controlados mediante inventario: el técnico registrará la cantidad realmente utilizada y se generarán los movimientos correspondientes.
2. Materiales menores sin control individual de existencias: se registrarán en la orden sin movimientos de inventario.

### Cantidades reales

* Las cantidades reales podrán diferir de las previstas, incluso superarlas.
* No se exigirá autorización adicional únicamente por superar la cantidad esperada.
* Se respetarán los permisos, la trazabilidad y las reglas de inventario.
* El técnico registrará los consumos durante el trabajo y confirmará el conjunto al marcar la orden como terminada.

### Sustituciones

* Se podrán definir alternativas autorizadas en los procedimientos.
* El técnico podrá seleccionar una alternativa preaprobada.
* Una alternativa no prevista requerirá autorización según los permisos configurados.
* Se registrará el producto realmente utilizado sin modificar el procedimiento.

### Devoluciones al almacén

Cuando se devuelva un componente retirado y no utilizado:

1. El técnico registrará el producto y la cantidad devuelta.
2. El responsable del almacén confirmará la recepción física.
3. Solo después de la confirmación se reincorporará la cantidad aceptada al inventario.

La devolución quedará vinculada a la orden y a los movimientos correspondientes.

### Unidades de medida

Se admitirán unidades de medida compatibles, conversiones a la unidad de inventario del producto y cantidades fraccionarias con precisión apropiada. No se permitirán conversiones entre unidades incompatibles.

## 7. Mano de obra, servicios y precios

Las líneas de servicio podrán utilizar uno de estos métodos de valoración:

* Precio fijo.
* Horas reales multiplicadas por una tarifa.

El método se elegirá según la configuración del taller o del servicio. No será obligatorio registrar horas en todas las reparaciones.

Los importes finales se calcularán a partir de los materiales consumidos, los componentes instalados y los servicios o trabajos realizados, respetando los precios acordados y sus cambios autorizados.

### Presupuestos y trabajos adicionales

* El presupuesto inicial será indicativo.
* Se podrán añadir trabajos y materiales adicionales a la misma orden.
* Se podrán configurar reglas que exijan revisar o autorizar cambios según el importe o tipo de trabajo.
* Se registrará quién aceptó el presupuesto, cuándo y por qué canal, con evidencia opcional.
* La aceptación previa a la reparación podrá ser obligatoria o no, según la configuración.

### Integración comercial y contable

La orden conservará el detalle técnico. Los documentos comerciales se gestionarán mediante los flujos estándar de ventas y facturación de Odoo.

Se reutilizarán las monedas, tipos de cambio, impuestos y redondeos estándar. No se desarrollará lógica fiscal o contable propia.

Los precios de venta, descuentos, costes internos y márgenes tendrán permisos de visibilidad separados. Solo los usuarios autorizados podrán modificar precios y descuentos o consultar costes internos.

Las correcciones de facturas y otros documentos contables se realizarán mediante los mecanismos estándar de Odoo.

## 8. Clientes, equipos y garantías

### Equipos del cliente

Se permitirá registrar equipos o activos vinculados al cliente y mantener su historial de intervenciones. También se admitirán reparaciones de artículos sin un activo registrado.

Se evaluará la reutilización del modelo estándar `maintenance.equipment` antes de desarrollar uno propio.

### Garantías y retrabajos

* Se registrará manualmente si una orden tiene garantía y su fecha de vencimiento.
* Las intervenciones posteriores serán nuevas órdenes vinculadas a la original.
* Se clasificarán como garantía, retrabajo o devolución.
* La orden original no se reabrirá.
* Al registrar una intervención por garantía, se mostrará la orden original y su vencimiento.
* Si el plazo ha vencido, se advertirá al usuario.
* Un usuario autorizado podrá continuar excepcionalmente, dejando constancia de la justificación.

## 9. Recepción y evidencias

Se podrá configurar un formulario de recepción que registre:

* Estado físico inicial.
* Accesorios recibidos.
* Observaciones.
* Fotografías y otros documentos.

Los campos y evidencias obligatorios dependerán del tipo de reparación y de las reglas configuradas por etapa.

Las evidencias podrán exigirse antes de avanzar en el flujo. Se reutilizará el mismo mecanismo para la recepción, la ejecución, las pruebas y la entrega, siempre que el diseño técnico lo permita.

## 10. Comunicaciones y auditoría

### Comunicaciones

Se mantendrá un historial de llamadas, mensajes, correos y acuerdos vinculados a la orden. Se utilizarán las capacidades estándar de Odoo cuando sean adecuadas.

Las notificaciones automáticas y las integraciones específicas con servicios externos quedan fuera del MVP.

### Auditoría

Las correcciones de órdenes cerradas requerirán autorización y registrarán:

* Valor anterior y nuevo.
* Motivo.
* Usuario.
* Fecha.

Las sustituciones y los cambios sujetos a autorización conservarán su registro de autorización.

El historial operativo no necesita almacenar cada modificación intermedia de todas las líneas, salvo cuando las reglas de auditoría lo exijan.

## 11. Configuración y permisos

El MVP se orientará a **un taller por instalación de Odoo**, con configuración y catálogo compartidos.

Los tipos de reparación podrán definir:

* Procedimientos sugeridos.
* Requisitos de recepción.
* Validaciones por etapa.
* Reglas de presupuesto y aceptación.
* Requisitos operativos particulares.

Los tipos no tendrán ciclos de estados independientes.

La configuración deberá ser suficientemente flexible para adaptar el módulo a distintos talleres, sin permitir que se desactiven controles críticos de inventario, trazabilidad, permisos o auditoría.

Los permisos deberán distinguir, como mínimo, la ejecución técnica, las autorizaciones operativas, la gestión de procedimientos, el acceso a información comercial y el acceso a costes internos.

## 12. Informes y consultas

El MVP incluirá:

* Órdenes por estado, cliente, técnico, fechas y tipo de reparación.
* Duración básica de las reparaciones.
* Consumo previsto frente al real.
* Órdenes agrupadas por estado.
* Filtros y exportaciones estándar de Odoo.

Los análisis avanzados de rentabilidad, márgenes y productividad detallada quedan fuera del MVP.

## 13. Funciones expresamente fuera del MVP

* Multiempresa operativa o aislamiento entre sucursales/talleres.
* Varios artículos reparables dentro de una única orden.
* Seguimiento horario detallado por tarea y por colaborador.
* Planificación avanzada de capacidad y asignación automática.
* Flujos de estados independientes por tipo de reparación.
* Activación condicional automática de líneas de procedimientos.
* Sistema avanzado de metrología.
* Automatizaciones de notificaciones y conexiones específicas con plataformas externas.
* Sistema propio de impuestos, contabilidad o facturación.
* Importador/exportador personalizado de paquetes de procedimientos.
* Análisis avanzado de márgenes y productividad.

## 14. Validaciones técnicas pendientes

Antes de programar se debe comprobar en el código fuente real de Odoo 20 Community:

1. Qué modelos y campos estándar conviene reutilizar para productos, unidades de medida, inventario, movimientos, ventas, facturación, equipos y comunicaciones.
2. Cómo integrar de forma correcta los movimientos de stock, las devoluciones y las reservas, evitando duplicar o alterar la lógica estándar.
3. Cómo enlazar la orden técnica con los documentos comerciales sin duplicar líneas contables.
4. Qué modelo estándar de equipos satisface los requisitos del historial de activos.
5. Cómo implementar permisos, reglas de acceso, auditoría y restricciones sobre versiones publicadas.
6. Qué dependencias y módulos estándar deben declararse en el manifiesto.
7. Qué vistas y mecanismos estándar de Odoo permiten implementar las listas, filtros, formularios y evidencias requeridas.

La revisión de código fuente no sustituye las pruebas de instalación y funcionamiento en una instancia real.

## 15. Ambigüedades que deben resolverse antes de cerrar el diseño

1. **Consumos y cobro:** definir el tratamiento comercial de un componente retirado que no se instala y tampoco puede devolverse como material utilizable.
2. **Repetición de pruebas:** precisar si se conservará cada intento con su resultado o solo el resultado final, además de la trazabilidad necesaria.
3. **Configuración:** concretar qué parámetros serán globales del taller y cuáles pertenecerán a cada tipo de reparación.
4. **Transiciones:** convertir las reglas generales de estados y validaciones en una matriz de transición con permisos y requisitos verificables.
5. **Presupuesto y facturación:** determinar cómo se reflejarán las cantidades y servicios reales en el documento comercial cuando difieran del presupuesto aprobado.
6. **Cierre y correcciones:** precisar qué cambios técnicos posteriores al cierre pueden afectar al stock o a documentos comerciales ya generados.

Estas cuestiones deben resolverse sin reabrir decisiones ya tomadas, salvo que se detecte una incompatibilidad real.

## 16. Criterio para pasar a implementación

El módulo estará preparado para comenzar su desarrollo cuando existan:

* Requisitos funcionales consolidados y sin contradicciones importantes.
* Modelo de entidades y relaciones.
* Mapa de reutilización de modelos estándar y modelos propios.
* Ciclo de vida con transiciones, permisos y validaciones.
* Definición del MVP.
* Criterios de aceptación y casos de prueba.
* Dependencias técnicas verificadas en Odoo 20 Community.

## Decisión funcional n.º 54 — Destino de componentes retirados

**Decisión seleccionada: tres destinos posibles.**

Cuando se retire un componente de un equipo o producto durante una reparación, el técnico deberá registrar su destino:

* **Reutilizable:** componente recuperado que puede volver a utilizarse.
* **Desechado:** componente declarado como residuo o no apto para reutilización.
* **Pendiente de evaluación:** componente cuyo estado o destino definitivo todavía no se ha determinado.

El destino registrado determinará el tratamiento logístico correspondiente, respetando los controles de inventario de Odoo. La reincorporación al inventario, cuando proceda, deberá registrarse mediante el movimiento correspondiente.

El destino físico del componente no determinará automáticamente si se factura al cliente. La decisión comercial se gestionará de forma independiente según las reglas de facturación del taller.

**Criterio de aceptación:** el sistema permite registrar el destino de cada componente retirado y mantiene separados su tratamiento logístico y su tratamiento comercial.

---

## Decisión funcional n.º 55 — Historial de pruebas de calidad repetidas

**Decisión seleccionada: conservar todos los intentos.**

Cuando una prueba de calidad se ejecute varias veces, el sistema conservará un registro independiente de cada intento, incluyendo:

* Resultado: aprobado, rechazado o no aplicable.
* Fecha y hora.
* Usuario que registró el resultado.
* Observaciones opcionales.

El sistema identificará el resultado vigente sin eliminar ni sobrescribir los intentos anteriores. La repetición de una prueba no requerirá autorización adicional por defecto; cualquier restricción futura deberá configurarse expresamente.

**Criterio de aceptación:** se pueden repetir pruebas y consultar su historial completo, identificando el resultado más reciente sin perder los registros anteriores.

---

## Decisión funcional n.º 56 — Determinación de importes facturables según ejecución real

**Decisión seleccionada: propuesta automática revisable.**

Al finalizar la reparación, el sistema generará una propuesta de conceptos facturables basada en la ejecución real de la orden. Un usuario autorizado deberá revisar y confirmar la propuesta antes de crear o actualizar los documentos comerciales correspondientes.

### Reglas funcionales

1. La propuesta considerará los materiales y componentes utilizados, los servicios realizados y la mano de obra registrada, según corresponda.
2. Se respetarán los precios acordados, descuentos, condiciones comerciales y autorizaciones registradas.
3. Los movimientos de inventario no generarán cargos comerciales automáticamente.
4. Los componentes retirados que no hayan sido instalados no se cobrarán automáticamente por el solo hecho de haber sido retirados.
5. Los trabajos y materiales adicionales respetarán las reglas de autorización definidas para el taller y el tipo de reparación.
6. Un usuario autorizado podrá revisar y confirmar la propuesta antes de generar o actualizar los documentos comerciales.
7. La orden de trabajo conservará el detalle técnico de la ejecución real. Las cotizaciones, pedidos de venta y facturas se gestionarán mediante los mecanismos estándar de Odoo, sin duplicar su lógica comercial o contable.
8. La propuesta facturable y los movimientos de inventario serán procesos relacionados, pero independientes.

**Criterio de aceptación:** al terminar una reparación, el sistema propone los conceptos facturables a partir de los datos reales de ejecución, permite su revisión por un usuario autorizado y requiere confirmación antes de generar o actualizar los documentos comerciales.

---

## Decisión funcional n.º 57 — Alcance de la configuración del taller

**Estado: pendiente de selección.**

Se debe determinar cómo se distribuye la configuración entre el taller y los tipos de reparación.

* **Opción A — Configuración general mínima (recomendada):** el taller define los parámetros comunes y cada tipo de reparación configura únicamente sus requisitos específicos. Las reglas críticas de inventario, permisos, trazabilidad y auditoría se mantienen protegidas.
* **Opción B — Configuración amplia por tipo:** cada tipo de reparación puede redefinir gran parte del comportamiento operativo, incluidas reglas generales.
* **Opción C — Configuración general únicamente:** todos los tipos de reparación comparten las mismas reglas; las diferencias se gestionan mediante los procedimientos y los datos de cada orden.

**Criterio de aceptación pendiente:** definir el alcance de la configuración general y específica antes de cerrar esta decisión.

