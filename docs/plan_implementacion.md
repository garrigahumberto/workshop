# Plan de implementación — Módulo de taller Odoo 20 Community

**Estado:** Plan propuesto
**Versión:** 1.0
**Módulo técnico:** `workshop_service`
**Documento de arquitectura:** `docs/arquitectura_tecnica.md`

## 1. Objetivo

Implementar el MVP del módulo de taller de forma incremental, verificable y compatible con Odoo 20 Community.

Cada incremento debe producir un resultado concreto, permitir comprobar su funcionamiento y limitar los cambios a una tarea definida.

Este plan no autoriza cambios en los requisitos ni sustituye la especificación funcional consolidada.

## 2. Reglas de ejecución

1. Trabajar en una tarea acotada cada vez.
2. Leer `AGENTS.md` y los documentos relevantes antes de implementar.
3. Verificar las API y dependencias contra Odoo 20.
4. Mantener el módulo instalable durante los incrementos, siempre que las dependencias del incremento lo permitan.
5. Añadir pruebas junto con la funcionalidad.
6. No comenzar un incremento si sus dependencias están incompletas.
7. No ocultar fallos de pruebas ni modificar requisitos para hacerlas pasar.
8. No implementar funciones fuera del MVP.
9. Detenerse y consultar ante una decisión funcional no resuelta.
10. No considerar una tarea terminada solo porque el código se haya escrito.

## 3. Fase 0 — Verificación del entorno

**Objetivo:** confirmar dónde y cómo se desarrollará el módulo antes de modificar el repositorio.

### Tareas

* Identificar el repositorio y su rama de trabajo.
* Revisar `AGENTS.md`, documentación y estructura existente.
* Identificar la versión efectiva de Odoo y PostgreSQL utilizada para las pruebas.
* Confirmar cómo se carga el directorio de módulos personalizados.
* Comprobar si existen módulos, configuraciones o cambios previos que deban preservarse.
* Verificar que las dependencias necesarias estén disponibles en la instalación objetivo.

### Criterios de aceptación

* El repositorio y la rama de trabajo están identificados.
* La versión objetivo de Odoo está confirmada.
* Se conoce el procedimiento de instalación o actualización del módulo.
* No se han sobrescrito cambios previos.
* Las limitaciones del entorno están documentadas.

**No comenzar la implementación funcional si no se ha confirmado el entorno de pruebas.**

## 4. Fase 1 — Esqueleto instalable

**Objetivo:** crear la estructura mínima del módulo y comprobar que Odoo puede instalarlo.

### Tareas

1. Crear `__manifest__.py` con las dependencias verificadas.
2. Crear los archivos `__init__.py` necesarios.
3. Crear los modelos mínimos y sus imports.
4. Crear los grupos de seguridad iniciales.
5. Crear la secuencia de numeración de órdenes.
6. Crear un menú y una vista mínima para comprobar la instalación.
7. Añadir pruebas básicas de carga e instalación.

### Criterios de aceptación

* Odoo reconoce el módulo.
* El módulo se instala sin errores.
* Los modelos y menús iniciales se cargan correctamente.
* No existen dependencias Enterprise involuntarias.
* Las pruebas básicas pasan.
* Se documenta el procedimiento de instalación y actualización.

No se incorporará todavía la lógica completa de procedimientos, inventario o facturación.

## 5. Fase 2 — Procedimientos versionados

**Objetivo:** implementar el sistema de recetas reutilizables, su publicación y la composición de procedimientos.

### Tareas

1. Crear los modelos de procedimiento, versión y línea.
2. Implementar la numeración de versiones.
3. Implementar edición de borradores.
4. Implementar validaciones previas a la publicación.
5. Impedir modificaciones ordinarias de versiones publicadas.
6. Implementar retirada de versiones.
7. Implementar procedimientos compuestos mediante referencias a versiones concretas.
8. Impedir referencias circulares.
9. Crear las vistas necesarias para gestionar procedimientos.
10. Añadir pruebas de integridad y permisos.

### Criterios de aceptación

* Es posible crear y editar un borrador.
* Una versión válida puede publicarse.
* Una versión publicada no puede alterarse mediante operaciones ordinarias.
* Se puede crear una nueva versión sin destruir la anterior.
* Las composiciones conservan las versiones concretas utilizadas.
* Los ciclos se rechazan.
* Los permisos de edición y publicación funcionan en el servidor.

**Dependencia:** Fase 1 completada.

## 6. Fase 3 — Órdenes de trabajo y ejecución

**Objetivo:** implementar el ciclo de vida de las órdenes y la aplicación de procedimientos.

### Tareas

1. Crear `workshop.order`.
2. Crear `workshop.equipment` y `workshop.repair.type`.
3. Implementar los estados y las transiciones autorizadas.
4. Implementar las validaciones de recepción, diagnóstico y presupuesto.
5. Registrar la aceptación del presupuesto conforme a la especificación funcional.
6. Crear el modelo de aplicación de procedimiento.
7. Crear las líneas ejecutables de la orden.
8. Implementar la copia de los datos de la versión aplicada.
9. Permitir líneas manuales cuando corresponda.
10. Registrar cantidades y tiempos previstos y reales.
11. Implementar cancelación controlada y relación con órdenes originales.
12. Crear las vistas de órdenes, equipos y tipos de reparación.
13. Añadir pruebas del flujo de estados y de aplicación de procedimientos.

### Criterios de aceptación

* Se puede crear y consultar una orden.
* Las transiciones válidas funcionan y las inválidas se rechazan.
* Se puede aplicar uno o varios procedimientos.
* Las líneas ejecutables conservan los datos históricos.
* Los cambios en las plantillas no alteran las órdenes existentes.
* Las cantidades reales pueden diferir de las previstas.
* La cancelación conserva la trazabilidad.
* Los permisos se validan en el servidor.

**Dependencia:** Fases 1 y 2 completadas.

## 7. Fase 4 — Calidad

**Objetivo:** registrar pruebas técnicas y controlar la terminación según los requisitos configurados.

### Tareas

1. Crear el modelo de intentos de calidad.
2. Implementar resultados aprobado, rechazado y no aplicable.
3. Registrar usuario, fecha y observaciones.
4. Conservar todos los intentos.
5. Garantizar un único resultado vigente por prueba.
6. Implementar validaciones de terminación técnica.
7. Incorporar evidencias adjuntas cuando existan.
8. Añadir pruebas de resultados, permisos y bloqueos.

### Criterios de aceptación

* Los intentos anteriores permanecen disponibles.
* El resultado vigente es identificable.
* Una prueba obligatoria y bloqueante impide la terminación cuando no cumple los requisitos.
* Un nuevo intento no elimina el historial.
* Las restricciones no dependen exclusivamente de la interfaz.

**Dependencia:** Fase 3 completada.

## 8. Fase 5 — Integración con Inventario

**Objetivo:** conectar la ejecución de las órdenes con las operaciones físicas reales de Stock.

### Tareas

1. Confirmar las API de Odoo 20 para las operaciones necesarias.
2. Definir y probar la relación entre órdenes, líneas y movimientos.
3. Implementar el tratamiento de materiales inventariables.
4. Diferenciar reserva y consumo físico.
5. Registrar las cantidades realmente utilizadas.
6. Implementar la gestión de devoluciones mediante el flujo estándar.
7. Respetar unidades de medida, lotes y series.
8. Registrar componentes retirados y su clasificación.
9. Verificar el comportamiento ante cancelaciones.
10. Añadir pruebas de integración con Stock.

### Criterios de aceptación

* Los movimientos físicos se registran mediante los mecanismos estándar.
* La reserva no se confunde con el consumo.
* Las cantidades previstas y reales permanecen diferenciadas.
* Los materiales no inventariables no generan movimientos ficticios.
* Los movimientos completados no se revierten mediante cambios directos en la orden.
* Las devoluciones mantienen la trazabilidad.
* La clasificación de componentes retirados no genera automáticamente cargos.
* Las pruebas de integración pasan en Odoo 20.

**Dependencia:** Fases 1 y 3 completadas. La Fase 4 puede avanzar en paralelo únicamente si no modifica las mismas áreas de código.

## 9. Fase 6 — Propuestas comerciales

**Objetivo:** preparar conceptos facturables a partir de la ejecución real y permitir su confirmación autorizada.

### Tareas

1. Crear el modelo de propuesta comercial y sus líneas.
2. Implementar la generación inicial desde la ejecución real.
3. Permitir revisión y ajustes autorizados.
4. Registrar quién revisa y confirma.
5. Integrar la confirmación con Ventas.
6. Relacionar propuestas con pedidos y líneas comerciales.
7. Evitar duplicaciones al repetir la confirmación.
8. Mantener la facturación dentro del flujo estándar.
9. Respetar las reglas de visibilidad de costes internos.
10. Añadir pruebas de autorización, idempotencia y documentos comerciales.

### Criterios de aceptación

* Se genera una propuesta revisable.
* La propuesta permite identificar el origen de sus conceptos.
* La confirmación exige permisos.
* Los reintentos no duplican documentos ni líneas.
* Los documentos comerciales utilizan los modelos estándar.
* La ejecución de inventario no genera cargos automáticos.
* Las pruebas comerciales pasan.

**Dependencia:** Fases 3 y 5 completadas para la integración completa. El diseño y las pruebas aisladas de propuestas pueden prepararse antes, sin simular como completada la integración real.

## 10. Fase 7 — Interfaz y reportes básicos

**Objetivo:** hacer operativas las funciones implementadas y proporcionar las consultas básicas acordadas.

### Tareas

1. Completar las vistas de órdenes.
2. Completar las vistas de procedimientos y versiones.
3. Completar las vistas de equipos y tipos de reparación.
4. Completar las vistas de propuestas comerciales.
5. Añadir filtros por estado, cliente, técnico, fechas y tipo.
6. Incorporar los informes básicos de órdenes y duración.
7. Incorporar la comparación de consumos previstos y reales.
8. Verificar la exportación estándar.
9. Revisar la visibilidad de campos y acciones por grupo.

### Criterios de aceptación

* Las operaciones principales pueden ejecutarse desde la interfaz.
* Los filtros corresponden a datos reales.
* Los usuarios ven únicamente las funciones y datos autorizados.
* Los reportes presentan información coherente con los registros.
* No se han añadido informes avanzados fuera del MVP.

**Dependencia:** las funciones que cada vista exponga deben estar implementadas y probadas.

## 11. Fase 8 — Validación integral del MVP

**Objetivo:** verificar el sistema completo en una instalación limpia y detectar regresiones.

### Tareas

1. Instalar el módulo desde cero.
2. Actualizarlo desde una instalación existente de prueba.
3. Ejecutar la suite de pruebas.
4. Verificar los permisos de cada grupo.
5. Ejecutar un caso completo desde la recepción hasta el cierre.
6. Verificar una orden con procedimiento compuesto.
7. Verificar una prueba rechazada seguida de un nuevo intento aprobado.
8. Verificar consumos, devoluciones y cancelaciones.
9. Verificar una propuesta comercial y su confirmación.
10. Revisar errores de servidor y registros relevantes.
11. Actualizar el README con el procedimiento real de instalación.
12. Registrar limitaciones conocidas y resultados.

### Criterios de aceptación

* La instalación limpia funciona.
* El flujo completo cumple la especificación funcional.
* Las pruebas críticas pasan.
* No existen errores críticos conocidos sin documentar.
* Las limitaciones pendientes están identificadas.
* La documentación describe el comportamiento realmente probado.

## 12. Orden de dependencias

La secuencia general es:

```text
Fase 0: Entorno verificado
           |
           v
Fase 1: Esqueleto instalable
           |
           v
Fase 2: Procedimientos versionados
           |
           v
Fase 3: Órdenes y ejecución
          / \
         v   v
Fase 4: Calidad    Fase 5: Inventario
          \          /
           v        v
           Fase 6: Propuestas comerciales
                     |
                     v
              Fase 7: Interfaz e informes
                     |
                     v
              Fase 8: Validación integral
```

La interfaz básica puede desarrollarse junto con cada incremento; no es necesario esperar hasta la Fase 7 para disponer de vistas de prueba. El diagrama representa las dependencias funcionales principales, no una prohibición de trabajo paralelo cuando los límites estén claros.

## 13. Formato de cada tarea de implementación

Antes de entregar una tarea a un agente, definir:

* **ID:** identificador breve.
* **Objetivo:** un resultado concreto.
* **Referencias:** documentos y código que debe consultar.
* **Alcance:** archivos o componentes que puede modificar.
* **Restricciones:** decisiones que debe respetar.
* **Pruebas:** verificaciones exigidas.
* **Criterios de aceptación:** condiciones objetivas de finalización.

Cada tarea debe ser lo bastante pequeña para revisar sus cambios y entender sus fallos sin reconstruir el proyecto completo.

El agente debe informar de los archivos modificados, las pruebas ejecutadas, las limitaciones y las decisiones pendientes. Debe detenerse si descubre una ambigüedad funcional que impida completar el objetivo correctamente.

## 14. Gestión de fallos y cambios de alcance

Cuando una tarea falle:

1. Identificar el fallo reproducible.
2. Determinar si es un error del código, del entorno, de una dependencia o de una especificación.
3. Corregir únicamente la causa dentro del alcance autorizado.
4. Repetir las pruebas relevantes.
5. Informar si el fallo requiere una decisión externa.

No se debe ampliar una tarea indefinidamente para solucionar problemas ajenos. Si una incompatibilidad exige un cambio arquitectónico o funcional, debe elevarse al responsable.

## 15. Criterio de finalización del MVP

El MVP se considerará implementado cuando las funciones incluidas en la especificación funcional estén disponibles, se respeten los permisos y controles críticos, las integraciones con Odoo funcionen y las pruebas acordadas pasen.

No forman parte de este criterio las funciones expresamente excluidas del MVP, como planificación avanzada, productividad detallada, rentabilidad avanzada, metrología, automatizaciones externas, importadores especializados o aislamiento avanzado entre instalaciones.

La finalización debe basarse en evidencia de ejecución y pruebas, no en el volumen de código producido.
