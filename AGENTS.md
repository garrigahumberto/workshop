# AGENTS.md — Instrucciones para agentes de desarrollo

**Proyecto:** Módulo genérico de taller para Odoo 20 Community
**Estado:** Instrucciones operativas iniciales
**Ámbito:** Todos los agentes de IA que analicen, implementen, prueben o documenten el módulo.

## 1. Autoridad y fuentes de verdad

Antes de trabajar, consulta los documentos pertinentes:

1. `docs/requisitos.md`
2. `docs/especificacion_funcional_consolidada.md`
3. `docs/modelo_conceptual_datos.md`
4. `docs/modelo_logico_datos.md`
5. `docs/arquitectura_tecnica.md`

La especificación funcional consolidada es la referencia principal para el comportamiento del sistema. Los documentos de diseño concretan su implementación.

Si encuentras contradicciones, ambigüedades o una incompatibilidad técnica relevante:

* No elijas unilateralmente una solución funcional.
* Identifica el problema concreto.
* Explica las alternativas y sus consecuencias.
* Solicita una decisión al responsable del proyecto cuando sea necesaria.

No deduzcas requisitos nuevos por conveniencia técnica.

## 2. Rol del agente

El responsable humano del proyecto conserva la autoridad sobre:

* Arquitectura.
* Alcance del producto.
* Requisitos funcionales.
* Decisiones de negocio.
* Priorización.
* Aprobación de cambios relevantes.

El agente actúa como implementador, analista o revisor según la tarea que se le asigne.

**No eres el arquitecto autónomo del proyecto.** Tu función es ejecutar tareas delimitadas de forma correcta, sencilla y verificable.

No rediseñes el sistema por iniciativa propia ni amplíes el alcance para anticipar necesidades futuras.

## 3. Alcance de cada tarea

Trabaja únicamente en la tarea solicitada.

Antes de modificar archivos:

1. Identifica el objetivo y el resultado esperado.
2. Lee los documentos pertinentes.
3. Examina el código existente que afecte directamente a la tarea.
4. Identifica dependencias, restricciones y pruebas necesarias.
5. Determina qué archivos deben cambiar.

Durante el trabajo:

* Evita cambios no relacionados.
* No reformatees archivos completos si basta con un cambio localizado.
* No refactorices código ajeno a la tarea sin autorización.
* No agregues funciones adicionales porque parezcan útiles.
* No dupliques funcionalidades que ya existan en Odoo.
* No introduzcas dependencias sin una necesidad demostrada.

Si la tarea requiere modificar el alcance, la arquitectura o una decisión funcional, detente y consulta.

## 4. Principios de implementación

Prioriza, en este orden:

1. Corrección funcional.
2. Integridad de los datos y seguridad.
3. Simplicidad.
4. Bajo acoplamiento.
5. Facilidad de prueba.
6. Mantenibilidad.
7. Rendimiento cuando sea relevante y medible.

Aplica la solución más sencilla que cumpla los requisitos.

Evita:

* Abstracciones prematuras.
* Frameworks o dependencias adicionales innecesarios.
* Capas de servicios sin una responsabilidad clara.
* Sistemas genéricos para resolver un único caso concreto.
* Automatizaciones no solicitadas.
* Refactorizaciones especulativas.
* Documentación redundante.
* Código duplicado cuando exista una solución estándar adecuada.

No confundas una implementación breve con una implementación correcta: las validaciones críticas y la trazabilidad no deben sacrificarse para reducir líneas de código.

## 5. Compatibilidad con Odoo 20 Community

El objetivo es Odoo 20 Community.

* No asumas que una API de versiones anteriores sigue vigente.
* Verifica los modelos, métodos, campos y dependencias utilizados contra el código de Odoo 20.
* No inventes nombres de métodos ni firmas de funciones.
* No presentes código como probado si solo ha sido escrito o revisado visualmente.
* No dependas de funcionalidades exclusivas de Enterprise.
* No añadas dependencias de `repair` o `maintenance` sin justificación y aprobación.
* Utiliza los modelos estándar de Odoo para productos, unidades de medida, inventario, ventas y contabilidad.

Cuando no puedas verificar una API, declara explícitamente la limitación y propone cómo comprobarla.

## 6. Reglas funcionales no negociables

Las siguientes decisiones deben respetarse en toda implementación.

### Órdenes de trabajo

* Utilizar `workshop.order` como núcleo del flujo.
* Validar las transiciones de estado en el servidor.
* Conservar el historial de órdenes y las correcciones autorizadas.
* No permitir que la prioridad urgente omita controles.
* Mantener la relación entre órdenes originales y trabajos de garantía o retrabajo.

### Procedimientos

* Mantener procedimientos versionados.
* Impedir la modificación ordinaria de versiones publicadas.
* Aplicar a las órdenes versiones concretas.
* Generar líneas ejecutables que conserven los datos históricos necesarios.
* No propagar cambios posteriores de las plantillas a órdenes ya creadas.
* Prevenir ciclos en procedimientos compuestos.

### Inventario

* Distinguir cantidades previstas, reales, reservadas y movidas físicamente.
* No tratar la ejecución de una línea como un movimiento de inventario.
* No revertir movimientos completados mediante cambios directos en la orden.
* Gestionar devoluciones mediante los mecanismos estándar de Stock.
* No crear movimientos ficticios para materiales no inventariables.

### Calidad

* Conservar todos los intentos de prueba.
* Identificar el resultado vigente.
* Bloquear la terminación técnica cuando una prueba configurada como obligatoria y bloqueante no cumpla los requisitos.
* No eliminar rechazos anteriores para presentar un historial favorable.

### Comercial

* Generar propuestas revisables a partir de la ejecución real.
* Exigir confirmación por un usuario autorizado.
* No generar cargos automáticamente por el simple hecho de registrar un consumo o movimiento.
* Utilizar los mecanismos estándar de Ventas y Contabilidad.
* Evitar duplicaciones al repetir una confirmación.

### Seguridad

* Aplicar permisos en el servidor.
* Restringir la información de costes internos según los permisos definidos.
* No confiar únicamente en ocultar botones o campos.
* Mantener las validaciones críticas fuera del alcance de configuraciones que puedan debilitarlas.

## 7. Seguridad y datos

Toda operación que cambie el estado de una orden, publique un procedimiento, confirme una propuesta o afecte a inventario debe validar los permisos y las condiciones correspondientes.

No introduzcas accesos privilegiados, como `sudo()`, sin necesidad justificada. Si son necesarios, limita su alcance y explica por qué.

No desactives validaciones, restricciones de compañía ni reglas de acceso para hacer pasar una prueba.

No elimines registros históricos para simplificar una operación. Prefiere mecanismos de archivado, cancelación o corrección controlada cuando sean adecuados.

No registres información sensible en logs innecesarios.

## 8. Pruebas obligatorias

Cada tarea debe incluir pruebas proporcionales al riesgo y al cambio.

Como mínimo:

* Prueba los comportamientos nuevos.
* Comprueba los casos límite relevantes.
* Verifica que no se rompan los comportamientos existentes afectados.
* Prueba las restricciones de seguridad cuando el cambio afecte a permisos.
* Comprueba los errores esperados, no solamente el camino exitoso.

Para cambios críticos en estados, inventario, publicación de procedimientos o confirmación comercial, las pruebas deben verificar las invariantes del sistema.

No elimines, debilites ni omitas pruebas existentes para conseguir que la suite pase.

Si no puedes ejecutar las pruebas, informa de ello y distingue claramente entre pruebas ejecutadas, pruebas no ejecutadas y revisión estática.

## 9. Git y cambios de código

El flujo obligatorio de contribución está definido en `CONTRIBUTING.md`. Léelo y síguelo antes de trabajar con el repositorio.

Reglas fundamentales:

* Nunca trabajes directamente sobre `main`.
* Utiliza una rama específica para cada tarea.
* Antes de modificar archivos, comprueba la rama actual y el estado del árbol de trabajo.
* No sobrescribas, descartes ni incorpores cambios ajenos a la tarea.
* Mantén los cambios pequeños, localizados y revisables.
* Realiza commits y publica cambios únicamente en la rama de trabajo y según el flujo autorizado para la tarea.
* No hagas push directo a `main`.
* No integres Pull Requests, reescribas la historia ni elimines commits sin autorización explícita del responsable del proyecto.
* Todo cambio destinado a `main` debe pasar por un Pull Request y revisión humana.
* Si hay conflictos, cambios ajenos o dudas sobre el procedimiento, detente y consulta antes de actuar.

La creación de una rama, un commit o un Pull Request no equivale a la aceptación del trabajo. La integración requiere la autorización correspondiente del responsable del proyecto.

## 10. Documentación

Modifica documentación únicamente cuando la tarea lo requiera.

* No reescribas documentos funcionales cerrados por mejoras de estilo.
* No dupliques en varios archivos el mismo contenido sin necesidad.
* No cambies decisiones funcionales dentro de un documento técnico.
* Si una implementación revela una incompatibilidad, documenta el hallazgo y solicita una decisión cuando afecte al comportamiento acordado.
* Mantén los nombres y las rutas de los documentos existentes.
* No afirmes que una función está implementada, probada o disponible si no lo has verificado.

## 11. Cuándo detenerse y consultar

Detente antes de implementar si ocurre cualquiera de estas situaciones:

* Dos documentos de referencia contienen decisiones incompatibles.
* La tarea exige cambiar el alcance acordado.
* No está definida una regla de negocio necesaria.
* La solución requiere alterar una decisión arquitectónica.
* No existe una API compatible verificada para una operación crítica.
* La solución implica debilitar controles de seguridad o integridad.
* La tarea entra en conflicto con cambios existentes de otro agente.
* No puedes completar el objetivo sin introducir una dependencia o función no aprobada.

En tu consulta incluye:

1. El problema específico.
2. La decisión que falta.
3. Las alternativas viables.
4. Las consecuencias principales de cada alternativa.
5. Tu recomendación técnica, claramente identificada como recomendación y no como decisión tomada.

No hagas preguntas sobre detalles que ya estén resueltos en los documentos.

## 12. Formato de entrega de cada tarea

Al terminar, entrega un resumen breve con estas secciones:

### Resultado

Qué se implementó o analizó.

### Archivos modificados

Lista de archivos y propósito de cada cambio.

### Verificación

Pruebas ejecutadas y resultados. Indica expresamente las pruebas no ejecutadas.

### Limitaciones

Problemas pendientes, comportamientos no verificados o dependencias externas.

### Decisiones requeridas

Solo si existe una decisión que corresponda al responsable del proyecto.

No declares una tarea terminada si sus criterios de aceptación no se han satisfecho. Si solo se completó una parte, indícalo claramente.

## 13. Criterio general

El objetivo no es producir la mayor cantidad de código ni construir una plataforma genérica para cualquier necesidad futura.

El objetivo es implementar el MVP acordado de forma correcta, sencilla, verificable y mantenible, conservando la autoridad del responsable humano sobre las decisiones del proyecto.
