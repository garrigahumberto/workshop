# Decisión 055: historial de intentos de pruebas de calidad

**Estado:** conservada como decisión para una capacidad futura; fuera de la versión preliminar
**Tipo:** funcional
**Alcance:** registro de pruebas de calidad ejecutadas en un trabajo

## Decisión

Cada ejecución de una prueba conservará un intento independiente con:

- resultado: aprobado, rechazado o no aplicable;
- fecha y hora;
- usuario que registró el resultado;
- observaciones opcionales.

El sistema identificará el resultado más reciente como vigente sin sobrescribir ni eliminar los intentos anteriores. Repetir una prueba no requiere autorización adicional por defecto.

## Criterio de aceptación

Después de repetir una prueba, se pueden consultar todos sus intentos y determinar cuál es el resultado más reciente.

## Aplicación a la versión preliminar

La primera versión no incluye un sistema general de pruebas de calidad. Si se incorpora posteriormente, los intentos no se sobrescribirán y la aplicación de resultados vigentes deberá definirse para cada control que realmente requiera el negocio.
