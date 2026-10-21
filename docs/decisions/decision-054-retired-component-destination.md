# Decisión 054: destino de componentes retirados

**Estado:** conservada como decisión para una capacidad futura; fuera de la versión preliminar
**Tipo:** funcional
**Alcance:** registro del destino de componentes retirados durante un trabajo

## Decisión

Cada componente retirado podrá clasificarse con uno de estos destinos:

- **Reutilizable:** recuperado y apto para volver a utilizarse.
- **Desechado:** declarado residuo o no apto para reutilización.
- **Pendiente de evaluación:** su estado o destino definitivo aún no está determinado.

El destino describe el tratamiento logístico del componente. No determina automáticamente si se cobra al cliente; el tratamiento comercial se decide por separado.

## Criterio de aceptación

Se puede registrar y consultar el destino de cada componente retirado, manteniendo separado ese dato de la decisión comercial.

## Aplicación a la versión preliminar

La primera versión no exige clasificar los componentes retirados. Si se implementa esta capacidad posteriormente, se conservará la separación entre el destino logístico y la decisión comercial. Cualquier movimiento físico seguirá el flujo estándar de inventario.
