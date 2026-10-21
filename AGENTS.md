# Instrucciones para agentes de desarrollo

## Fuentes vigentes

Antes de analizar o modificar el producto, consulta las fuentes actuales según el tema:

1. `docs/requirements.md`: comportamiento y alcance de la versión preliminar.
2. `docs/business_description.md`: contexto operativo.
3. `docs/domain_model.md`: conceptos y relaciones del dominio.
4. `docs/arch/architecture.md`: límites e integración técnica.
5. `docs/implementation_plan.md` y `docs/test_plan.md`: secuencia y verificación.
6. `CONTRIBUTING.md`: flujo de trabajo del repositorio.

Los archivos son borradores de trabajo salvo indicación expresa de aprobación. Los documentos funcionales no se sustituyen por inferencias a partir del código existente. Si difieren, identifica el conflicto y solicita decisión cuando afecte a una regla de negocio.

## Reglas de trabajo

- Implementa solo el objetivo asignado; no amplíes el alcance por anticipación.
- Antes de editar, verifica rama, árbol de trabajo y cambios ajenos. Presérvalos.
- No trabajes directamente en `main`, no hagas commits ni publiques salvo autorización.
- No inventes APIs de Odoo 20. Verifica la versión, módulos instalados, código fuente y pruebas reales para integraciones críticas.
- No dupliques en Workshop inventario, Punto de Venta, ventas, facturación, pagos o caja.
- No alteres existencias mediante escritura directa ni repitas una salida/cargo que ya se produjo en Odoo.
- Mantén los estados de orden simples y registra hitos/eventos sin convertirlos en pasos obligatorios no acordados.
- Mantén diferenciadas la revisión permanente de un procedimiento y la variación puntual de una orden.
- Automatiza usuario, fecha e historial cuando el sistema pueda obtenerlos; no pidas volver a registrar datos disponibles.
- Aplica permisos en servidor. No uses `sudo()` ni debilites controles sin necesidad justificada.
- Añade pruebas proporcionales al cambio y declara con precisión qué se ejecutó y qué no.
- Si falta una decisión de negocio o una API crítica no puede verificarse, describe el problema, alternativas, efectos y recomendación; detén solo el trabajo afectado.
- No cambies documentos de alcance por iniciativa propia. Propón la modificación y espera aprobación cuando cambie una decisión funcional.

## Entrega

Resume resultado, archivos cambiados, verificaciones realizadas, limitaciones y decisiones pendientes. Usa enlaces Markdown absolutos a los archivos del workspace en la respuesta.
