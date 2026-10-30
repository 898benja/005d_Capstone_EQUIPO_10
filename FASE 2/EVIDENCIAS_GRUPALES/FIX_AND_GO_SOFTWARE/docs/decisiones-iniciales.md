# Decisiones iniciales — 16 de septiembre de 2026

## Alcance

MVP académico móvil para servicios técnicos del hogar en Santiago: gas, electricidad y agua. Recorrido de cliente y prestador, con persistencia compartida. Desembolso adicional previsto: cero usando recursos existentes.

## Implementación

Una sola app móvil, una API Django organizada por módulos y una base SQLite local. Pagos y certificaciones profesionales serán demostrativos. La API debe autorizar cada operación según identidad, rol y pertenencia al recurso.

## Decisiones de datos pendientes

1. Una cuenta con ambos roles o un rol por cuenta; personas o empresas.
2. Solicitud dirigida a un prestador o abierta a varias cotizaciones.
3. Precio total o visita y presupuesto posterior.
4. Datos de ubicación, fotos y agenda.
5. Confirmación de cierre, cancelaciones y valoraciones.

## Primer objetivo técnico

Conectar dos teléfonos con la API local y demostrar un recorrido mínimo: solicitar, cotizar, aceptar y completar un servicio. Después ampliar búsqueda y perfiles. No se declara este objetivo implementado todavía.

## Versionado

Repositorio independiente del portafolio académico. Mantener documentación técnica junto al código y publicar avances comprobados; no incluir documentos personales ni credenciales.
