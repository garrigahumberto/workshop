# Diagramas del flujo preliminar

## Recorrido desde tienda

```mermaid
flowchart LR
    A[Cliente en tienda] --> B{Compra repuesto}
    B -->|No| C[Registrar servicio si lo solicita]
    B -->|Sí| D[Venta en Odoo]
    D --> E{Necesita instalación o reparación}
    E -->|No| F[Fin de venta en Odoo]
    E -->|Sí| G[Crear o relacionar orden Workshop]
    C --> G
    G --> H[Registrar servicio y responsables]
    H --> I[Relacionar venta existente, sin duplicar cargo]
    I --> J[Entrega y cobro por flujo Odoo]
    J --> K[Cerrar orden]
```

## Recorrido directo al taller

```mermaid
flowchart LR
    A[Cliente llega al taller] --> B[Recepción y apertura de orden]
    B --> C{Presupuesto usado en este caso}
    C -->|Sí| D[Registrar presupuesto y acuerdo]
    C -->|No| E[Continuar sin paso de aprobación formal]
    D --> F[Ejecutar servicio]
    E --> F
    F --> G[Registrar mano de obra y responsables]
    F --> H[Registrar componentes y referencias de inventario]
    G --> I[Entrega]
    H --> I
    I --> J[Cobro en Odoo si corresponde]
    J --> K[Cerrar orden]
```

## Revisión de procedimiento

```mermaid
flowchart TD
    A[Aplicar revisión vigente a una orden] --> B[Copiar referencia a la orden]
    B --> C{Desviación en este trabajo}
    C -->|Cantidad distinta o adicional puntual| D[Registrar en la orden]
    C -->|Cambio permanente del servicio| E[Crear nueva revisión]
    D --> F[Historial de orden preservado]
    E --> G[Órdenes nuevas usan la revisión elegida]
    G --> F
```

Los diagramas resumen el comportamiento previsto; no sustituyen los requisitos ni resuelven las decisiones pendientes de inventario y documentos comerciales.
