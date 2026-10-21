# Plan de pruebas de la versión preliminar

**Propósito:** comprobar que Workshop mejora la continuidad del trabajo sin duplicar operaciones estándar de Odoo ni exigir pasos rutinarios innecesarios.

## 1. Pruebas funcionales prioritarias

### Dashboard

- Seleccionar un día en el selector de rango y confirmar que ese día se incluye; seleccionar dos días y confirmar que ambos extremos se incluyen en las métricas, los talleres y las órdenes recientes.
- Confirmar que el filtro de taller sigue combinándose con el rango de fechas.
- Rechazar un rango cuya fecha inicial sea posterior a la fecha final.

### Recepción y estados

- Crear una orden desde una tienda y otra directamente desde un taller.
- Abrir una orden con información mínima y completar diagnóstico después.
- Verificar que la orden puede cerrarse sin presupuesto formal cuando no se usa.
- Cancelar y verificar motivo, usuario, fecha e historial.
- Reabrir una orden cerrada por garantía y retrabajo y verificar que el cierre previo sigue visible.
- Archivar una orden sin cambiar su estado ni eliminarla.

### Ubicación y responsabilidad

- Registrar múltiples ubicaciones de tienda/taller y filtrar las órdenes por ubicación.
- Separar a quien recibió al cliente de quien ejecutó el servicio.
- Registrar varios servicios con responsables distintos.
- Confirmar que un componente compartido no exige un único técnico como responsable personal.

### Procedimientos

- Crear una primera revisión de un procedimiento y aplicarla a una orden.
- Crear la siguiente revisión con cambios de producto, cantidad o tareas.
- Confirmar que la orden anterior conserva la revisión y los datos originales.
- Registrar cantidad real superior a la referencia sin alterar el procedimiento ni solicitar aprobación innecesaria.
- Añadir un servicio puntual y comprobar que no modifica la revisión publicada.
- Ejecutar una orden sin procedimiento.

### Productos, inventario y documentos comerciales

- Relacionar una venta de tienda con una instalación en taller y comprobar que no se duplica el cargo ni el movimiento de stock.
- Registrar un componente tomado directamente para una reparación y comprobar su relación con el movimiento estándar correspondiente.
- Asignar consumibles al taller y comprobar que su disponibilidad central se actualiza una vez.
- Anotar consumible usado en varias órdenes y comprobar que no genera nuevas salidas.
- Reintentar la asociación de un documento comercial y confirmar que no se crea una relación o documento duplicado.
- Confirmar que Workshop no genera facturas, pagos ni caja por registrar una ejecución.

## 2. Seguridad e integridad

- Usuario sin permiso no publica ni altera procedimientos protegidos.
- Usuario sin permiso no accede a órdenes o ubicaciones restringidas, si se configura esa restricción.
- Las validaciones se prueban a nivel de servidor, no solo en las vistas.
- No se permite modificar directamente estados/cantidades de movimientos estándar para hacer pasar pruebas.
- La corrección de una orden cerrada conserva los valores previos y la autoría requerida.

## 3. Prueba de usabilidad operativa

Recorrer casos reales de recepción, reparación y entrega midiendo:

- campos obligatorios que el usuario no conoce en el momento de recepción;
- cambios de pantalla y acciones manuales repetidas;
- cantidad de datos que se vuelven a escribir y que ya existen en Odoo;
- pausas para buscar autorizaciones o productos;
- capacidad de gerencia para identificar responsable, servicios, componentes y documento comercial relacionado.

Registrar fricciones observadas y priorizar primero las que impiden completar el trabajo o causan duplicidad/error. No añadir controles únicamente para producir más datos.

## 4. Verificación técnica

- Ejecutar pruebas unitarias e integración disponibles del addon.
- Instalar y actualizar el módulo en la versión objetivo de Odoo 20 Community con los módulos realmente usados.
- Probar flujos POS, Stock y facturación en una base de pruebas representativa.
- Informar por separado pruebas ejecutadas, fallidas y no disponibles por falta de entorno o módulos.
