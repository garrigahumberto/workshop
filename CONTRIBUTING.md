# Proceso de contribución

Define cómo colaboran las personas y los agentes. No establece requisitos del producto ni decisiones técnicas. Las decisiones de alcance, negocio y arquitectura corresponden al responsable humano. Las instrucciones particulares para agentes están en [`AGENTS.md`](./AGENTS.md).

El solicitante o responsable define el resultado y acepta los cambios. Quien contribuye —persona o agente— ejecuta la tarea, comunica bloqueos y no aprueba ni integra su propio trabajo por el mero hecho de haberlo realizado.

## 1. Flujo común

1. **Acordar:** confirmar objetivo, alcance y criterios de aceptación. Para análisis, acordar la pregunta y la evidencia esperada.
2. **Orientarse:** identificar el tipo de tarea, consultar las fuentes pertinentes y revisar rama, estado del árbol y cambios existentes.
3. **Resolver bloqueos:** si falta una decisión o hay contradicciones, describir el problema, alternativas y consecuencias; pedir decisión antes de implementar la parte afectada.
4. **Trabajar:** usar una rama dedicada para cambios; preservar todo cambio ajeno y limitarse al alcance acordado.
5. **Verificar:** ejecutar comprobaciones proporcionales, inspeccionar el resultado y distinguir lo probado de lo no verificado.
6. **Entregar:** resumir resultado, archivos, comprobaciones, limitaciones, decisiones pendientes y estado de publicación.

Si el árbol contiene cambios ajenos, no limpiarlos, moverlos, incluirlos en commits ni sobrescribirlos. Si interfieren con la tarea y no pueden preservarse con seguridad, detenerse y consultar. No aplicar, eliminar ni modificar stashes o ramas existentes sin autorización expresa.

## 2. Procedimiento según la tarea

### Análisis o investigación

1. Responder la pregunta acordada usando evidencia pertinente.
2. Separar hechos, inferencias y recomendaciones.
3. Entregar hallazgos con referencias y límites de verificación.
4. No cambiar archivos salvo que se haya pedido un entregable documental.

### Documentación

1. Identificar la fuente canónica del tema.
2. Cambiar esa fuente; enlazar otras fuentes en vez de duplicar contenido.
3. No convertir propuestas o pendientes en decisiones aprobadas.
4. Revisar enlaces, consistencia y diff; informar si el cambio altera significado o solo corrige presentación.

### Código o pruebas

1. Revisar el código, patrones y pruebas relacionados.
2. Implementar solo el resultado acordado.
3. Añadir o actualizar pruebas para el comportamiento afectado.
4. Ejecutar las pruebas y validaciones pertinentes; informar resultados y fallos reales.

### Revisión

1. Comparar el cambio con el objetivo, criterios y decisiones aprobadas.
2. Presentar primero los hallazgos, ordenados por impacto, con evidencia y ubicación.
3. Distinguir problemas confirmados de dudas o recomendaciones.
4. No corregir el cambio revisado salvo que también se haya encargado su implementación.

### Trabajo bloqueado o con conflicto

1. Detener solo la parte afectada; preservar los cambios y el estado actual.
2. Describir el bloqueo o conflicto y por qué impide avanzar con seguridad.
3. Proponer alternativas y consecuencias cuando haya más de una salida razonable.
4. Esperar la decisión necesaria; continuar las partes independientes solo si no comprometen el trabajo bloqueado.

## 3. Ramas

`main` es la rama de integración. Todo cambio destinado a integrarse se trabaja en una rama dedicada, creada desde una base apropiada y actualizada.

Usar el formato `<tipo>/<resumen-kebab>`:

- `feat/<resumen>` — funcionalidad.
- `fix/<resumen>` — corrección.
- `docs/<resumen>` — documentación.
- `test/<resumen>` — pruebas.
- `refactor/<resumen>` — reestructuración sin cambio funcional intencional.
- `chore/<resumen>` — mantenimiento.
- `review/<resumen>` — rama compartida solo para evaluación, no lista para integrar.

El resumen debe ser corto, descriptivo, en minúsculas y con palabras separadas por guiones. Ejemplo: `docs/contribution-process`.

No trabajar directamente en `main`, hacer push a `main`, integrar Pull Requests, reescribir historia ni borrar ramas compartidas sin autorización expresa. Publicar ramas y abrir Pull Requests solo cuando se solicite o autorice.

## 4. Commits

Usar el formato **Conventional Commits**:

```text
<tipo>(<alcance opcional>): <resumen>
```

Tipos permitidos:

- `feat`: funcionalidad nueva.
- `fix`: corrección de comportamiento.
- `docs`: documentación.
- `test`: pruebas.
- `refactor`: reestructuración sin cambio funcional intencional.
- `chore`: mantenimiento sin cambio funcional.

Reglas del resumen:

- Escribirlo en español, en minúsculas y en modo imperativo.
- No terminar con punto y limitar el asunto completo a 72 caracteres.
- El límite de 72 caracteres cuenta toda la línea del asunto, incluidos tipo, alcance, dos puntos y espacios.
- El alcance, si se usa, debe ser breve y en minúsculas, por ejemplo `stock` o `orden`.
- Si el cambio rompe compatibilidad, usar `!` después del tipo o alcance y añadir al cuerpo `BREAKING CHANGE: <impacto>`.
- Añadir cuerpo solo cuando haga falta explicar el motivo, contexto o impacto; mantenerlo breve.

Ejemplos:

```text
feat(orden): registrar materiales utilizados
fix(stock): evitar duplicar una devolución
docs: aclarar el flujo de contribución
test(procedimiento): comprobar versiones publicadas
```

Un commit debe representar una sola intención lógica. Antes de confirmar, revisar el diff preparado y asegurar que contiene solo cambios relacionados con esa intención. Separar cambios independientes en commits distintos. No incluir archivos ajenos, secretos ni configuración local. No enmendar ni reescribir commits publicados sin autorización.

## 5. Verificación, publicación y aceptación

- Ejecutar las comprobaciones pertinentes al tipo y riesgo del cambio. No debilitar pruebas para ocultar fallos.
- No afirmar que algo está verificado si solo se revisó visualmente. Nombrar las pruebas no ejecutadas.
- Revisar el diff final y confirmar que no contiene cambios ajenos o sensibles.
- Presentar mediante Pull Request los cambios destinados a `main`. La descripción incluye objetivo, enfoque, verificaciones, limitaciones y decisiones pendientes.
- Atender los comentarios de revisión con cambios y nuevas verificaciones, o responder con la justificación si no se aplican. No ignorar comentarios pendientes en silencio.
- La revisión humana determina si el cambio satisface la necesidad y puede integrarse. Un commit o Pull Request no equivale a aceptación; solo el responsable autorizado aprueba la integración.
- Entregar un resumen breve: resultado, archivos, verificaciones y resultados, limitaciones, decisiones requeridas y si el trabajo quedó local, publicado o en Pull Request.

### Lista antes de publicar

- [ ] Estoy en la rama de tarea correcta, no en `main`.
- [ ] El diff incluye solo cambios previstos para esta tarea.
- [ ] Cada commit tiene una sola intención y cumple el formato acordado.
- [ ] No incluí cambios ajenos, secretos, configuración local ni archivos temporales.
- [ ] Ejecuté las verificaciones pertinentes y anoté las que no pude ejecutar.
- [ ] La descripción de la Pull Request explica el objetivo, los cambios y su estado de verificación.
