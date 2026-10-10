## 1. Objetivo

Desarrollar un módulo personalizado para Odoo 20 Community que permita gestionar talleres de distintos tipos mediante procedimientos de servicio configurables, integrados con productos, inventario, ventas, facturación y usuarios de Odoo.

El sistema debe reducir la introducción manual de datos, registrar el consumo real, mantener un historial auditable y permitir adaptar los procedimientos sin modificar código.

## 2. Procedimientos de servicio

Cada procedimiento podrá contener:

* Componentes y materiales descriptivos, sin obligar a seleccionar una marca o referencia comercial concreta.
* Servicios y mano de obra.
* Consumibles con cantidades y unidades de medida.
* Elementos obligatorios y opcionales.
* Cantidades estándar, rangos e instrucciones.
* Procedimientos subordinados reutilizables.

Los procedimientos serán configurables por el gerente desde la interfaz.

### Regla de integridad

Una reparación utilizará una versión identificable del procedimiento. Los cambios posteriores no alterarán los trabajos históricos ni sus cantidades o precios acordados.

## 3. Ejecución del servicio

Una orden de trabajo podrá incorporar uno o varios procedimientos.

Cada línea descriptiva permitirá seleccionar el producto comercial concreto del almacén o tienda. Por ejemplo, el procedimiento indica «Batería de 12 V», mientras que el responsable selecciona la batería disponible, con su marca, modelo, precio y número de serie cuando corresponda.

El sistema distinguirá:

* Cantidad prevista por el procedimiento.
* Producto concreto seleccionado.
* Cantidad realmente utilizada.
* Elementos adicionales no previstos.
* Servicios y mano de obra ejecutados.

Las adiciones no modificarán el procedimiento original. El consumo real será el que se utilice para descontar existencias.

## 4. Inventario y unidades de medida

La solución deberá integrarse con el inventario estándar de Odoo.

* Admitir cantidades fraccionarias: gramos, mililitros, metros, etc.
* Permitir conversiones compatibles entre unidades.
* Registrar movimientos reales de existencias.
* Identificar lotes y números de serie cuando corresponda.
* Conservar la trazabilidad del material utilizado en cada trabajo.

Los consumibles —grasa, estaño, lubricantes, productos de limpieza, entre otros— se gestionarán como productos inventariables cuando sea necesario controlar sus existencias, o como consumibles no inventariables cuando la política del taller lo justifique.

## 5. Precios, costos y presupuesto

El sistema distinguirá costo interno y precio de venta.

* Los procedimientos podrán definir precios de venta para servicios y referencias descriptivas.
* El precio de venta podrá ajustarse según las necesidades comerciales y los permisos del usuario.
* El precio acordado con el cliente quedará congelado en la orden, aunque cambie después el precio del producto.
* El técnico no tendrá acceso a los costos internos por defecto.
* Inicialmente, gerente y vendedor autorizado podrán decidir precios y descuentos.

### Presupuesto y autorización

1. Se registra el servicio y su diagnóstico inicial.
2. Se prepara un presupuesto orientativo.
3. El cliente autoriza el inicio del trabajo.
4. Durante la ejecución pueden aparecer fallas o necesidades adicionales.
5. Los adicionales se registran en la orden, con sus materiales, servicios, cantidades y precios.
6. Se determina el importe final con los elementos realmente utilizados y los servicios ejecutados.

El proceso no exigirá una nueva aprobación formal del presupuesto por cada variación. El taller comunicará las variaciones al cliente conforme a su práctica comercial.

## 6. Orden de trabajo

La orden deberá permitir registrar:

* Cliente y equipo o activo del cliente.
* Tipo de equipo y sus datos identificativos.
* Diagnóstico y falla encontrada.
* Procedimientos aplicados.
* Técnico responsable.
* Materiales y servicios utilizados.
* Adicionales.
* Observaciones y evidencias fotográficas o documentales opcionales.
* Estados y fechas relevantes.
* Precios, importes y situación de cobro.

El flujo inicial propuesto será:

Solicitud → Diagnóstico → Presupuesto → Aprobado → En reparación → Terminado → Entregado → Cerrado.

Los estados y sus transiciones deberán validarse durante el diseño.

## 7. Documento para el cliente

La documentación final podrá incluir:

* Identificación del cliente y del equipo.
* Diagnóstico y trabajo realizado.
* Materiales realmente utilizados.
* Servicios y mano de obra.
* Adicionales.
* Cantidades, precios e importe total.
* Responsable del trabajo.

No mostrará los materiales meramente previstos por el procedimiento.

## 8. Usuarios y permisos

Roles iniciales:

* **Administrador:** control técnico y administrativo de la instalación.
* **Gerente:** control del negocio, inventario, procedimientos, usuarios operativos y datos comerciales.
* **Almacenero:** recepción, almacenamiento, movimientos y control de existencias.
* **Vendedor:** atención comercial, selección de productos, precios autorizados y ventas.
* **Técnico:** consulta de procedimientos, ejecución de trabajos, registro de consumos, diagnóstico y adicionales.

Los permisos exactos del técnico quedan pendientes de definir. La configuración deberá permitir adaptar los roles a distintos talleres.

## 9. Auditoría e historial

Se conservará, según corresponda:

* Usuario que realizó cada operación.
* Fechas de creación y modificación.
* Versiones de procedimientos.
* Cantidades previstas y reales.
* Productos y números de serie utilizados.
* Precios acordados y adicionales.
* Cambios de estado.
* Correcciones posteriores mediante operaciones trazables.

No se permitirán modificaciones silenciosas de trabajos cerrados.

## 10. Alcance y restricciones

* Odoo 20 Community.
* Instalación destinada a una sola empresa.
* Integración con módulos estándar siempre que resulte conveniente.
* Desarrollo personalizado limitado a las necesidades que Odoo no cubra.
* Configuración de nuevos procedimientos desde la interfaz, sin programar cada servicio.
* Diseño incremental, con pruebas por funcionalidad.
* Sin implementación hasta aprobar el diseño conceptual y comprobar las capacidades reales de Odoo 20.

## 11. Criterios iniciales de aceptación

El módulo deberá demostrar que:

1. Un gerente puede crear y versionar procedimientos.
2. Una orden puede combinar varios procedimientos.
3. Se pueden seleccionar productos comerciales concretos a partir de componentes descriptivos.
4. El procedimiento no cambia cuando se ejecuta o se modifica posteriormente.
5. Se registran cantidades previstas y reales.
6. El inventario descuenta el consumo real y mantiene trazabilidad.
7. Los precios acordados permanecen en el historial.
8. Se pueden registrar adicionales no previstos.
9. Los permisos impiden acciones no autorizadas.
10. Las reparaciones cerradas conservan su historial y permiten auditoría.
11. Se puede obtener la documentación final del servicio.
12. Las operaciones se verifican mediante pruebas reproducibles.
