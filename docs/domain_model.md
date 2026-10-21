# Modelo de dominio preliminar

**Propósito:** definir los conceptos que Workshop necesita para la primera versión sin imponer una implementación técnica no validada.

## 1. Entidades

### Orden de servicio

Representa un trabajo para un cliente y un artículo/equipo atendido. Conserva número, ubicación operativa, origen (tienda o taller), persona que recibió al cliente, estado, fechas/eventos relevantes, notas, servicios, componentes, procedimientos aplicados y referencias a operaciones de Odoo.

### Ubicación operativa

Representa una tienda o un taller dentro de la operación del negocio. Una orden pertenece a una ubicación responsable. La ubicación no crea por sí sola una compañía ni un inventario separado. Su relación con las ubicaciones físicas de Odoo se determinará según la configuración de la instalación.

### Persona responsable

Se utiliza el usuario/empleado correspondiente de Odoo cuando esté disponible:

- persona que recibe al cliente;
- persona que ejecuta un servicio de mano de obra.

No se asigna forzosamente a una persona única cada componente compartido; se registra ubicación o equipo responsable.

### Procedimiento publicado

Cada revisión es un registro identificable de procedimiento. Registros con el mismo código base representan la evolución de un mismo servicio. La identidad visible incluye código y revisión; el ID interno del registro identifica exactamente la definición aplicada. No se requiere una entidad técnica de versión separada.

Ejemplo:

| Código base | Revisión | Identidad visible | Definición |
|---|---:|---|---|
| CAM-ACEITE | 1 | CAM-ACEITE-001 | Aceite X, 2 L; limpieza de filtros |
| CAM-ACEITE | 2 | CAM-ACEITE-002 | Aceite Y, 3 L; limpieza de filtros; cambio de tapa |

Una revisión publicada no se modifica. Una nueva revisión se crea como nuevo registro y la anterior permanece consultable.

Una revisión representa un cambio permanente a lo largo del tiempo, no una opción antigua disponible para elegir rutinariamente. Si dos servicios distintos o dos recetas alternativas deben ofrecerse al mismo tiempo, no se debe seleccionar una revisión obsoleta como sustituto de una variante. La representación de variantes simultáneas —códigos propios o alternativas explícitas— queda pendiente de confirmación.

### Línea de procedimiento

Describe una operación, material/componente o servicio de mano de obra como valor de referencia. Incluye nombre, instrucciones opcionales, cantidad/unidad de referencia cuando corresponde, producto sugerido si existe y si es opcional.

### Línea de orden

Representa lo que se hizo en una reparación. Puede proceder de una línea de procedimiento o ser una adición manual. Conserva una copia histórica de la descripción y la referencia prevista, junto con el dato real cuando se registra.

Tipos mínimos:

- componente identificable;
- material gastable;
- servicio de mano de obra;
- operación o nota de trabajo.

Una línea de mano de obra puede asignarse a una persona. Una línea de material se asocia a la orden y ubicación y puede enlazarse a producto/movimiento de inventario.

### Asignación de consumibles

Representa una asignación periódica de uno o varios materiales gastables desde la disponibilidad central a un taller. Conserva producto, cantidad, unidad, fecha, ubicación destino y referencia a la operación estándar de inventario que materializa la asignación. No representa el consumo por reparación.

### Referencia comercial

Vínculo a una venta, línea de venta, operación de Punto de Venta, factura o cobro existente de Odoo, según los mecanismos que la instalación permita validar. La referencia relaciona el servicio con la operación comercial; no replica el documento ni crea un cargo automáticamente.

### Evento de orden

Registra cambios significativos de estado y eventos de negocio como recepción, presupuesto, entrega, cierre, cancelación y reapertura. Guarda acción, usuario, fecha y motivo cuando aplique. Los datos automáticos no se solicitan manualmente.

## 2. Relaciones y reglas

- Una ubicación operativa tiene muchas órdenes.
- Una orden tiene una persona que recibió al cliente y puede tener varias personas ejecutoras de servicios.
- Una orden puede aplicar cero o más procedimientos publicados.
- Una aplicación referencia exactamente un registro/revisión publicada.
- Una orden tiene líneas ejecutadas, tanto derivadas de procedimientos como agregadas manualmente.
- Una línea de mano de obra puede tener un responsable individual.
- Una línea de componente puede relacionarse con una operación de inventario o con una venta preexistente; no debe provocar el mismo efecto de existencias dos veces.
- Una asignación de consumibles pertenece a una ubicación de taller y se registra separadamente del uso informativo en órdenes.
- Una orden puede relacionarse con más de un documento comercial si el proceso usa ventas separadas para producto y mano de obra.
- La reapertura conserva los eventos anteriores y requiere motivo de garantía o retrabajo.

## 3. Identidad e inmutabilidad de procedimientos

El código base identifica la familia del servicio; la revisión identifica la definición concreta, por ejemplo `CAM-ACEITE` + `2`. Debe existir unicidad para la combinación código/revisión. La aplicación a una orden guarda la referencia exacta, no una búsqueda dinámica del procedimiento más reciente.

La nueva revisión puede iniciarse copiando la anterior, pero los cambios solo afectan al nuevo registro. Un cambio puntual de cantidad o una tarea excepcional se registra en la orden y no incrementa automáticamente la revisión.

## 4. Referencias a modelos de Odoo

Clientes, usuarios/empleados, productos, unidades, ubicaciones y operaciones comerciales o de inventario deben reutilizar modelos estándar cuando estén disponibles y sean compatibles. Los nombres de modelos, campos y métodos concretos quedan sujetos a inspección de Odoo 20 Community y de los módulos realmente instalados.

Workshop no mantendrá copias independientes de clientes, productos, facturas, ventas, movimientos de existencias ni caja.
