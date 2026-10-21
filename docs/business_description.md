# Descripción del negocio

**Estado:** contexto operativo informado por el responsable del proyecto; algunos detalles siguen pendientes de validación en el negocio.

## Actividad

El negocio combina un almacén central, una o varias tiendas y uno o varios talleres. El almacén abastece tanto la venta de productos en tienda como los componentes y materiales necesarios para prestar servicios en el taller. Odoo ya proporciona las capacidades generales de inventario, punto de venta, ventas y facturación; Workshop debe cubrir el seguimiento del trabajo de reparación y enlazarlo con esas operaciones, no reemplazarlas.

## Recorridos de servicio

Un cliente puede iniciar un trabajo por dos vías:

1. **Desde una tienda:** el cliente solicita un componente o repuesto; la tienda puede venderlo. Si también necesita instalación o reparación, el trabajo pasa al taller con la venta ya registrada. La orden debe permitir relacionar la venta existente con el servicio para evitar cobrar de nuevo el mismo componente.
2. **Directamente en un taller:** el cliente entrega el equipo al técnico. Si se trata de un mantenimiento o servicio que no requiere repuestos, el trabajo se puede atender y cobrar como servicio sin pasar por una venta de componente en tienda.

Una orden puede incluir servicios de mano de obra, componentes identificados, materiales gastables o una combinación. El origen del trabajo y la ubicación donde se atiende deben quedar visibles.

## Ubicaciones y existencias

Puede haber varias tiendas y varios talleres, con operación comercial centralizada en la instalación y el inventario de Odoo configurado para el negocio. Gerencia necesita identificar qué tienda o taller atendió cada operación y quién fue responsable.

Los componentes identificables utilizados en una reparación deben quedar asociados a la orden. Si ya se vendieron en la tienda, la orden referencia esa venta y no genera una segunda salida ni un segundo cargo.

Los materiales gastables —por ejemplo, aceite, grasa, estaño, combustible o cable— pueden asignarse periódicamente al taller para un conjunto de trabajos. La salida de existencias se registra al hacer esa asignación, no de nuevo en cada orden que anota su uso. El tratamiento exacto de la asignación dentro de inventario estándar debe validarse para la instalación del negocio.

## Responsabilidades

Una misma persona puede atender varios aspectos del negocio, pero el sistema debe permitir identificar:

- quién recibió o atendió al cliente;
- qué tienda o taller fue responsable de la atención;
- qué servicios individuales de mano de obra ejecutó cada trabajador;
- qué componentes se relacionaron con la reparación y en qué taller se utilizaron.

La responsabilidad sobre componentes puede corresponder al taller o a un equipo y no requiere asignar artificialmente una única persona a un material compartido. La ejecución de cada servicio de mano de obra sí debe poder atribuirse a una persona.

## Ciclo del trabajo y control comercial

El flujo operativo es recepción, presupuesto cuando corresponda, servicio, entrega y cobro con los documentos y mecanismos estándar disponibles en Odoo. No todos los negocios o trabajos necesariamente requieren un presupuesto formal ni una aprobación previa.

Los estados visibles de la orden deben mantenerse sencillos: abierta, cerrada o cancelada; una orden cerrada puede reabrirse por garantía o retrabajo conservando el historial. El archivado es una acción administrativa para ocultar órdenes antiguas de las listas de trabajo, no un paso adicional que el personal deba completar en cada servicio.

El cobro y el cierre diario de caja se realizan en Odoo. Workshop debe permitir relacionar la orden con la operación comercial pertinente, pero no mantener una caja paralela ni duplicar ventas o facturas. La gerencia necesita poder conciliar el servicio realizado con los registros de venta y cobro existentes.

## Problema que motiva el producto

La información puede perderse entre tienda, almacén y taller: una pieza vendida puede no asociarse con la instalación; un componente o servicio realizado puede quedar fuera del cobro; y la gerencia puede no saber quién recibió al cliente, qué se utilizó ni quién ejecutó la mano de obra.

Workshop debe reducir esas pérdidas de continuidad con el mínimo registro adicional posible. Los datos que el sistema pueda obtener de Odoo —como la persona y hora de una operación o la referencia de una venta enlazada— no deben pedirse nuevamente al usuario.

## Límites conocidos

- Workshop gestiona el servicio y su trazabilidad; no sustituye inventario, punto de venta, ventas, facturación o caja de Odoo.
- El alcance inicial debe servir a un negocio pequeño y permitir identificar varias tiendas y talleres sin diseñar aislamiento multiempresa.
- La operación exacta de transferencia de componentes y asignación de consumibles debe respetar los flujos estándar de inventario disponibles.
- El producto debe poder utilizarse sin configurar procedimientos para todos los servicios.
- El alcance aún debe validarse con ejemplos operativos reales; las reglas comerciales no universales no se impondrán como controles obligatorios.
