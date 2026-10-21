# Plan de implementación de la versión preliminar

**Estado:** secuencia de trabajo propuesta; cada etapa requiere revisión humana antes de ampliar el alcance.

## Preparación

- Confirmar rama, estado del árbol y cambios existentes.
- Revisar instrucciones del proyecto, requisitos, modelo de dominio y arquitectura.
- Inspeccionar la versión real de Odoo 20 Community y los módulos instalados antes de integrar POS, Stock, Ventas o facturación.
- Mantener separados requisitos confirmados, decisiones pendientes y limitaciones técnicas.

## Etapa 1: orden operativa mínima

- Orden con número, cliente opcional al inicio, artículo/equipo identificable por los datos disponibles, origen, ubicación, persona de recepción, notas y estado abierto/cerrado/cancelado.
- Registro automático de fechas/usuarios y eventos de cierre, cancelación y reapertura.
- Archivo como marca administrativa.
- Búsqueda y filtros operativos básicos.

**Salida:** recepción directa en taller y recepción originada en tienda pueden registrarse sin completar formularios extensos.

## Etapa 2: procedimientos y ejecución

- Catálogo de procedimientos con código base y revisión visible.
- Cada revisión es un registro identificable; no diseñar un modelo separado solo para administrar versiones.
- Líneas de procedimiento para operaciones, componentes, consumibles y mano de obra.
- Aplicación de una revisión fija a una orden con copia de datos relevantes.
- Diferenciar variaciones locales de una orden frente a cambios permanentes que requieren una nueva revisión.
- Asignar responsable individual a cada línea/servicio de mano de obra.

**Salida:** probar variación de cantidad, adicional puntual y publicación de una nueva revisión sin alterar órdenes antiguas.

## Etapa 3: componentes y relación comercial

- Registrar componentes usados con producto y cantidad cuando corresponda.
- Verificar y enlazar una venta/POS existente a la orden, manteniendo un único cargo y una única salida de inventario.
- Verificar enlace a documentos de servicio/facturación de Odoo sin crear caja o documentos paralelos.
- Probar reintentos y vínculos duplicados.

**Puerta de decisión:** detener integración si la instalación no ofrece un flujo estándar comprobable o si no está acordado qué documento/línea es la referencia canónica.

## Etapa 4: existencias de taller

- Verificar el flujo estándar para un componente retirado directamente del almacén para una reparación.
- Verificar asignaciones periódicas de consumibles a cada taller.
- Mantener el consumo por orden como dato operativo que no vuelve a descontar materiales ya asignados.
- Confirmar la ubicación destino y el tratamiento de inventario que refleja correctamente la política contable/operativa del negocio.

**Puerta de decisión:** no simular bajas, transferencias ni consumos mediante edición directa de existencias.

## Etapa 5: seguridad y validación de negocio

- Implementar permisos mínimos para operación, ubicación y edición sensible.
- Probar usuarios que representan atención, técnico, responsable de ubicación y gerencia; una persona puede tener varios roles.
- Recorrer todos los escenarios de aceptación con usuarios del negocio.
- Corregir fricciones de interfaz observadas antes de añadir estados, campos o automatizaciones.

## Fuera de esta versión

No añadir aprobación configurable de cada variación, partes horarios por tarea, flujo de calidad general, análisis avanzados, notificaciones externas, contabilidad propia ni multiempresa salvo decisión explícita posterior.
