# Plan de pruebas — Módulo de taller Odoo 20 Community

**Estado:** Plan propuesto
**Versión:** 1.0
**Módulo:** `workshop_service`
**Plataforma objetivo:** Odoo 20 Community

## 1. Objetivo

Definir cómo verificar que el módulo cumple la especificación funcional, respeta la arquitectura aprobada y se integra correctamente con Odoo 20 Community.

Las pruebas deben detectar errores funcionales, pérdida de trazabilidad, accesos no autorizados, duplicación de operaciones e inconsistencias entre las órdenes y los documentos estándar de Odoo.

Este documento complementa `docs/plan_implementacion.md`. No introduce requisitos funcionales nuevos.

## 2. Principios de prueba

1. Probar las reglas de negocio en el servidor, no únicamente la interfaz.
2. Verificar tanto los casos válidos como los inválidos.
3. Priorizar los controles que protegen datos, inventario, permisos y documentos comerciales.
4. Utilizar los mecanismos de prueba compatibles con Odoo 20.
5. No sustituir integraciones reales por simulaciones cuando se esté validando su comportamiento real.
6. No afirmar que una prueba pasó si no se ejecutó.
7. Mantener las pruebas existentes al modificar el código.
8. Evitar pruebas frágiles que dependan de textos visuales o detalles internos irrelevantes.
9. Asegurar que los datos de prueba sean reproducibles y no dependan de información externa.
10. Corregir la causa de un fallo; no debilitar la prueba para ocultarlo.

## 3. Niveles de prueba

### 3.1. Pruebas unitarias o de modelo

Comprueban reglas específicas de los modelos propios:

* Validación de campos y relaciones.
* Restricciones de versiones.
* Transiciones de estado.
* Reglas de cantidades y unidades.
* Selección del resultado vigente de una prueba.
* Permisos de acciones críticas.

### 3.2. Pruebas de integración

Comprueban la interacción con modelos estándar de Odoo:

* Productos y unidades de medida.
* Movimientos de inventario.
* Reservas y devoluciones.
* Pedidos y líneas de venta.
* Monedas e impuestos cuando correspondan.
* Usuarios, compañías y permisos.

### 3.3. Pruebas de flujo completo

Verifican escenarios de principio a fin, utilizando la interfaz o las operaciones de modelo que correspondan:

* Recepción, diagnóstico, presupuesto y aceptación.
* Aplicación de procedimientos y ejecución.
* Pruebas de calidad.
* Consumos y devoluciones.
* Terminación, entrega y cierre.
* Generación, revisión y confirmación de propuestas comerciales.

## 4. Preparación del entorno

Antes de ejecutar las pruebas:

* Confirmar que se utiliza Odoo 20 Community.
* Confirmar las dependencias instaladas.
* Instalar o actualizar el módulo en una base de datos de prueba.
* Verificar que las pruebas utilizan usuarios con permisos definidos.
* Preparar productos, unidades de medida, ubicaciones y datos comerciales adecuados para cada escenario.
* Evitar depender de registros creados manualmente en una sesión anterior.
* Registrar los comandos utilizados y los resultados obtenidos.

Las pruebas de instalación deben poder repetirse en una base de datos limpia.

## 5. Pruebas de instalación

| ID      | Caso                                                  | Resultado esperado                                                 |
| ------- | ----------------------------------------------------- | ------------------------------------------------------------------ |
| INST-01 | Instalar el módulo en una base limpia compatible.     | Instalación satisfactoria.                                         |
| INST-02 | Cargar modelos, vistas, datos y seguridad.            | No se producen errores de carga.                                   |
| INST-03 | Comprobar las dependencias declaradas.                | Todas existen y son compatibles.                                   |
| INST-04 | Actualizar el módulo después de un cambio de esquema. | Actualización satisfactoria y datos conservados según corresponda. |
| INST-05 | Comprobar los menús con distintos perfiles.           | Cada usuario ve únicamente las funciones permitidas.               |

## 6. Pruebas de procedimientos y versiones

| ID      | Caso                                        | Resultado esperado                                                          |
| ------- | ------------------------------------------- | --------------------------------------------------------------------------- |
| PROC-01 | Crear un procedimiento y un borrador.       | Se crean correctamente.                                                     |
| PROC-02 | Modificar un borrador válido.               | Los cambios se guardan.                                                     |
| PROC-03 | Publicar una versión válida.                | La publicación queda registrada.                                            |
| PROC-04 | Publicar una versión incompleta o inválida. | La operación se rechaza con un error comprensible.                          |
| PROC-05 | Modificar una versión publicada.            | La modificación ordinaria se rechaza en el servidor.                        |
| PROC-06 | Crear una versión nueva.                    | La versión anterior se conserva.                                            |
| PROC-07 | Retirar una versión.                        | Se impide su uso nuevo según la política acordada, sin perder el historial. |
| PROC-08 | Aplicar una versión a una orden.            | Se conserva la versión exacta utilizada.                                    |
| PROC-09 | Cambiar posteriormente la plantilla.        | Las líneas ya aplicadas no cambian.                                         |
| PROC-10 | Crear una composición de procedimientos.    | Se conservan las versiones concretas de los componentes.                    |
| PROC-11 | Introducir una referencia circular.         | La operación se rechaza.                                                    |
| PROC-12 | Intentar publicar sin permisos.             | La operación se rechaza.                                                    |

Las pruebas de inmutabilidad deben intentar modificar la versión por las operaciones de modelo, no solo comprobar que la interfaz oculta el botón de edición.

## 7. Pruebas de órdenes y estados

| ID     | Caso                                                              | Resultado esperado                                         |
| ------ | ----------------------------------------------------------------- | ---------------------------------------------------------- |
| ORD-01 | Crear una orden con los datos mínimos válidos.                    | Orden creada con numeración correcta.                      |
| ORD-02 | Registrar un diagnóstico.                                         | El diagnóstico queda asociado a la orden.                  |
| ORD-03 | Avanzar por una transición válida.                                | El cambio se realiza y conserva su trazabilidad.           |
| ORD-04 | Intentar una transición no permitida.                             | La operación se rechaza.                                   |
| ORD-05 | Aplicar varios procedimientos.                                    | Se crean las líneas correspondientes sin perder su origen. |
| ORD-06 | Añadir una línea manual.                                          | Se registra sin fingir que procede de un procedimiento.    |
| ORD-07 | Cambiar la plantilla de un procedimiento ya aplicado.             | La orden conserva su copia histórica.                      |
| ORD-08 | Cancelar sin motivo.                                              | La cancelación se rechaza.                                 |
| ORD-09 | Cancelar con motivo válido.                                       | Se conserva el motivo y el historial.                      |
| ORD-10 | Intentar cerrar una orden sin cumplir las condiciones necesarias. | El cierre se rechaza.                                      |
| ORD-11 | Corregir una orden cerrada sin autorización.                      | La operación se rechaza.                                   |
| ORD-12 | Ejecutar una acción con prioridad urgente.                        | Se mantienen los controles críticos.                       |
| ORD-13 | Registrar una orden de garantía o retrabajo.                      | La relación con la orden original queda conservada.        |

Las pruebas deben cubrir todas las transiciones definidas en la especificación funcional y sus precondiciones.

## 8. Pruebas de cantidades y unidades de medida

| ID     | Caso                                                         | Resultado esperado                                           |
| ------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| QTY-01 | Registrar una cantidad real igual a la prevista.             | Se conserva correctamente.                                   |
| QTY-02 | Registrar una cantidad real distinta de la prevista.         | Ambas cantidades permanecen diferenciadas.                   |
| QTY-03 | Utilizar unidades compatibles.                               | La conversión respeta la configuración y precisión de Odoo.  |
| QTY-04 | Intentar utilizar unidades incompatibles.                    | La operación se rechaza o se solicita una corrección válida. |
| QTY-05 | Registrar cantidades fraccionarias válidas.                  | Se respeta la precisión de la unidad.                        |
| QTY-06 | Registrar una cantidad inválida según las reglas aplicables. | Se rechaza sin corromper los datos.                          |

No se deben introducir conversiones propias que contradigan las unidades y reglas de precisión de Odoo.

## 9. Pruebas de calidad

| ID    | Caso                                                     | Resultado esperado                                                   |
| ----- | -------------------------------------------------------- | -------------------------------------------------------------------- |
| QA-01 | Registrar un intento aprobado.                           | El intento queda registrado como vigente.                            |
| QA-02 | Registrar un intento rechazado.                          | El rechazo queda conservado.                                         |
| QA-03 | Repetir una prueba.                                      | Se crea un nuevo intento sin borrar el anterior.                     |
| QA-04 | Registrar otro intento como vigente.                     | Solo uno queda identificado como vigente para esa prueba.            |
| QA-05 | Terminar una orden con una prueba bloqueante rechazada.  | La terminación se impide.                                            |
| QA-06 | Repetir una prueba y obtener un resultado válido.        | La terminación se permite si se cumplen todas las demás condiciones. |
| QA-07 | Registrar una prueba no aplicable cuando esté permitido. | Se conserva el resultado y su trazabilidad.                          |
| QA-08 | Intentar modificar el historial sin autorización.        | La operación se rechaza.                                             |

## 10. Pruebas de inventario

Estas pruebas deben ejecutarse con los modelos estándar de Stock y las configuraciones reales de una base de pruebas.

| ID     | Caso                                               | Resultado esperado                                    |
| ------ | -------------------------------------------------- | ----------------------------------------------------- |
| STK-01 | Crear una orden con material previsto.             | No se produce consumo físico automáticamente.         |
| STK-02 | Reservar material cuando corresponda.              | La reserva queda diferenciada del consumo.            |
| STK-03 | Completar un movimiento de salida.                 | El movimiento queda registrado en Stock.              |
| STK-04 | Registrar consumo real distinto del previsto.      | La diferencia queda trazada correctamente.            |
| STK-05 | Registrar material no inventariable.               | No se crea un movimiento ficticio.                    |
| STK-06 | Devolver material.                                 | Se utiliza el flujo estándar de devolución.           |
| STK-07 | Cancelar una orden con un movimiento pendiente.    | Se trata según el estado y las reglas estándar.       |
| STK-08 | Cancelar una orden con un movimiento completado.   | No se borra ni revierte implícitamente el movimiento. |
| STK-09 | Registrar un producto con lote o serie.            | Se conserva la trazabilidad exigida por Stock.        |
| STK-10 | Clasificar un componente retirado.                 | No se crea automáticamente un movimiento ni un cargo. |
| STK-11 | Intentar una operación de inventario sin permisos. | La operación se rechaza.                              |

Debe verificarse que la relación entre orden y movimiento sea inequívoca y no genere movimientos duplicados en reintentos.

## 11. Pruebas comerciales

| ID     | Caso                                                        | Resultado esperado                                             |
| ------ | ----------------------------------------------------------- | -------------------------------------------------------------- |
| COM-01 | Generar una propuesta después de la ejecución técnica.      | Se crea una propuesta revisable.                               |
| COM-02 | Revisar y ajustar un concepto.                              | El ajuste queda registrado conforme a los permisos.            |
| COM-03 | Intentar confirmar sin autorización.                        | La confirmación se rechaza.                                    |
| COM-04 | Confirmar una propuesta válida.                             | Se crea o actualiza el documento comercial previsto.           |
| COM-05 | Repetir la confirmación.                                    | No se duplican pedidos ni líneas.                              |
| COM-06 | Revisar la trazabilidad de un concepto.                     | Se identifica la línea ejecutada de origen cuando corresponda. |
| COM-07 | Procesar una propuesta con impuestos o moneda configurados. | Se respetan los mecanismos estándar de Odoo.                   |
| COM-08 | Registrar consumo de material.                              | No se genera automáticamente un cargo por el movimiento.       |
| COM-09 | Gestionar un componente retirado no instalado.              | No se inventa un tratamiento comercial no aprobado.            |
| COM-10 | Intentar consultar costes internos sin permisos.            | El acceso se deniega.                                          |

La factura y el asiento contable no deben crearse mediante una implementación paralela a las funciones estándar de Odoo.

## 12. Pruebas de seguridad

Crear usuarios de prueba representativos de cada grupo.

Comprobar, como mínimo:

* Lectura y modificación de órdenes.
* Registro de ejecución.
* Publicación y retirada de procedimientos.
* Consulta de costes internos.
* Confirmación de propuestas comerciales.
* Operaciones de inventario.
* Correcciones posteriores al cierre.
* Acceso entre compañías cuando la configuración lo haga relevante.

Las pruebas deben verificar accesos por interfaz y por operaciones de modelo. Ocultar un botón no basta para considerar protegida una operación.

## 13. Pruebas de flujo completo

### FLUJO-01: reparación estándar

1. Registrar una orden.
2. Identificar cliente y equipo cuando corresponda.
3. Registrar el diagnóstico.
4. Preparar el presupuesto.
5. Registrar su aceptación según la configuración.
6. Aplicar un procedimiento publicado.
7. Ejecutar las líneas.
8. Registrar consumos reales.
9. Completar las pruebas de calidad necesarias.
10. Terminar la reparación.
11. Generar y revisar la propuesta facturable.
12. Confirmar la propuesta con un usuario autorizado.
13. Registrar la entrega y el cierre según las reglas aplicables.

**Resultado esperado:** la orden completa el flujo permitido, conserva la trazabilidad y se integra con los documentos estándar de Odoo.

### FLUJO-02: prueba rechazada

1. Crear una orden válida.
2. Ejecutar las operaciones necesarias.
3. Registrar una prueba bloqueante rechazada.
4. Intentar terminar la orden.
5. Registrar un nuevo intento aprobado.
6. Volver a intentar la terminación.

**Resultado esperado:** el primer intento de terminación se bloquea; el segundo puede avanzar si se cumplen las demás condiciones. El historial conserva ambos intentos.

### FLUJO-03: cancelación con movimiento realizado

1. Crear una orden con material inventariable.
2. Registrar y completar el movimiento físico correspondiente.
3. Cancelar la orden mediante el flujo autorizado.
4. Consultar la orden y el movimiento.

**Resultado esperado:** la cancelación conserva su motivo e historial. El movimiento completado permanece íntegro y cualquier devolución se realiza mediante el flujo estándar.

### FLUJO-04: propuesta comercial repetida

1. Completar una orden.
2. Generar la propuesta.
3. Revisar y confirmar.
4. Repetir la acción de confirmación de forma controlada.
5. Consultar los documentos comerciales.

**Resultado esperado:** no se duplican pedidos ni líneas y la relación con la orden se mantiene.

## 14. Pruebas de regresión

Después de modificar una función existente:

* Ejecutar las pruebas relacionadas con esa función.
* Ejecutar las pruebas de los componentes dependientes.
* Ejecutar la suite completa antes de una entrega importante.
* Comparar el resultado con la última ejecución conocida.
* Investigar cualquier fallo nuevo.

No se debe marcar una regresión como aceptable sin documentar su causa y obtener la decisión correspondiente.

## 15. Registro de resultados

Cada tarea debe dejar constancia de:

* Pruebas ejecutadas.
* Resultado de cada prueba.
* Errores detectados.
* Correcciones realizadas.
* Pruebas pendientes o imposibles de ejecutar.
* Limitaciones del entorno.
* Decisiones pendientes del responsable del proyecto.

El informe de una tarea debe diferenciar claramente:

* **Correcto:** probado y satisfactorio.
* **Fallido:** ejecutado y no satisfactorio.
* **No ejecutado:** no se dispone de evidencia de ejecución.
* **Bloqueado:** falta una dependencia o decisión necesaria.

## 16. Criterio de aceptación del MVP

El MVP se podrá considerar validado cuando:

1. El módulo se instale y actualice en el entorno objetivo.
2. Los flujos funcionales incluidos en el alcance estén cubiertos.
3. Las pruebas críticas de versionado, estados, calidad, permisos, inventario y propuestas comerciales pasen.
4. Las integraciones utilicen correctamente los modelos estándar de Odoo.
5. No existan fallos críticos conocidos sin resolver o aceptar expresamente.
6. Las limitaciones pendientes estén documentadas.
7. Los resultados puedan reproducirse en el entorno de pruebas.

La ausencia de errores observados durante una prueba manual no sustituye la verificación de los criterios anteriores.
