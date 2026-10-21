# Arquitectura técnica preliminar

**Objetivo:** implementar el seguimiento de reparaciones como módulo de Odoo, dejando inventario, ventas, facturación, punto de venta y caja bajo sus flujos estándar.

## 1. Principios

1. Workshop es dueño de la orden, sus líneas de ejecución, sus procedimientos y la trazabilidad propia del servicio.
2. Odoo es dueño de productos, existencias, movimientos, ventas, facturas, pagos y sesiones/cierres de Punto de Venta.
3. Registrar una línea de servicio o material no crea por sí solo un documento financiero.
4. Un movimiento físico se ejecuta por los mecanismos estándar de inventario; Workshop guarda su relación, no reproduce ni modifica estados internos de Stock.
5. El mismo usuario puede asumir varias responsabilidades y una instalación puede contener varias tiendas y talleres sin aislamiento multiempresa en esta fase.
6. La interfaz debe minimizar pasos: registrar una vez, asignar usuario/fecha automáticamente y no bloquear por datos no disponibles en recepción.
7. Las validaciones esenciales se aplican en servidor; vistas y botones no son controles de seguridad.

## 2. Componentes funcionales

### Órdenes

Gestiona creación, consulta, estado simple, hitos/eventos, ubicación, recepción, reapertura, cancelación y enlaces con referencias de Odoo.

Estados funcionales previstos: `open`, `closed` y `cancelled`. El archivado es una marca de archivo independiente del estado. Reabrir una cerrada vuelve al estado abierto y añade un evento de reapertura, preservando la fecha y usuario del cierre anterior.

### Procedimientos

Un registro representa una revisión concreta publicada. Código base y revisión visible identifican la variante. No se crea un modelo de versión separado. La orden conserva el ID exacto de la revisión aplicada y una copia histórica de las líneas necesarias para la ejecución.

### Ejecución

Mantiene líneas de componentes, consumibles, servicios, operaciones y adicionales. Las líneas permiten distinguir referencia prevista y resultado real sin exigir que el usuario complete valores iguales dos veces. Los servicios de mano de obra permiten asignar una persona.

### Integraciones Odoo

Las integraciones se limitan a relaciones y acciones estándar validadas para la versión instalada:

- Venta en tienda/Punto de Venta: relacionar la operación o línea existente con la orden, sin duplicar producto ni cargo.
- Stock: relacionar un movimiento estándar cuando un componente sale para una reparación; registrar asignaciones periódicas de consumibles a una ubicación de taller.
- Venta/facturación/cobro: consultar o enlazar documentos comerciales existentes. No crear una contabilidad o caja propias.

No fijar nombres de APIs o dependencias de módulos hasta verificar la instalación real de Odoo 20 Community. Si el enlace deseado no es posible con el estándar disponible, documentar el límite y consultar antes de crear una integración alternativa.

## 3. Modelo de datos de referencia

El modelo de dominio completo está descrito en [domain_model.md](../domain_model.md). A nivel técnico, se esperan conceptos equivalentes a:

- orden de servicio;
- ubicación operativa;
- procedimiento/revisión publicada;
- línea de procedimiento;
- línea de orden;
- evento de orden;
- asignación de consumibles;
- vínculo a operación comercial o de inventario estándar.

Estos son conceptos de diseño, no nombres de modelos Odoo ya verificados. La implementación debe seguir los prefijos y patrones existentes en el addon cuando no contradigan el comportamiento requerido.

## 4. Integridad e historial

- La revisión de procedimiento usada por una orden queda fijada al aplicar el procedimiento.
- Una revisión publicada no se edita; se crea otra revisión para cambios permanentes.
- Cambios puntuales, cantidades reales y adicionales son locales a la orden.
- La reapertura y la cancelación generan eventos trazables; nunca borran el cierre previo ni las líneas históricas.
- El enlace a una venta ya contabilizada impide volver a consumir o cobrar el mismo componente por la orden.
- No se cambia inventario mediante escrituras directas de cantidades disponibles.
- Las correcciones y reintentos deben ser explícitos e idempotentes donde impliquen una operación estándar.

## 5. Acceso

El MVP debe incluir permisos básicos por operación y datos comerciales. Como mínimo, un usuario autorizado puede crear/actualizar órdenes operativas; publicar procedimientos y realizar correcciones sensibles se restringe a usuarios con permiso gerencial. El acceso a costos internos no se añade salvo decisión aprobada.

La configuración de ubicación debe evitar registros sin ubicación responsable una vez que la orden esté operativa. La matriz exacta de acceso por tienda/taller se valida antes de introducir reglas de registro restrictivas.

## 6. Compatibilidad y validación técnica

Antes de usar una integración crítica:

1. confirmar versión y módulos instalados de Odoo Community;
2. inspeccionar el modelo y flujo estándar real para POS, stock y documentos comerciales;
3. confirmar si puede crearse un vínculo seguro sin duplicar movimientos o documentos;
4. probar creación, reintento, cancelación y límites de permisos en una instancia de prueba.

La presencia de un modelo en el código fuente de Odoo no demuestra que el módulo esté instalado ni que una API sea compatible. Si un flujo no se verifica, no presentar la integración como terminada ni sustituirla por lógica propia silenciosamente.

## 7. Secuencia de implementación recomendada

1. Orden simple, ubicaciones y responsables.
2. Estados y eventos trazables.
3. Procedimientos con código/revisión y líneas ejecutables.
4. Componentes y mano de obra en la orden.
5. Relación de ventas/POS preexistentes y prevención de duplicados.
6. Flujo de componente directo a reparación y asignación periódica de consumibles, una vez verificados los mecanismos estándar de Stock.
7. Seguridad, pruebas integrales y validación con escenarios reales.

La secuencia no autoriza ampliar el alcance. Cualquier dependencia de una API no disponible o una decisión de negocio pendiente debe detener únicamente la parte afectada y elevar la decisión.
