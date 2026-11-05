# Definition of Done — FIX&GO

Una historia o tarea puede marcarse “Terminada” únicamente cuando cumple todos los criterios aplicables. Si falta una validación externa, debe quedar “Implementada, pendiente de aceptación”.

## Código y datos

- La implementación cumple sus criterios de aceptación y las reglas de roles y estados.
- El backend mantiene la autoridad sobre permisos, importes y transiciones; el móvil no decide estados sensibles.
- Los cambios del modelo incluyen una migración versionada y `makemigrations --check --dry-run` no detecta migraciones faltantes.
- No se versionan secretos, credenciales privadas, bases de datos, dependencias instaladas ni datos personales reales.
- Los errores esperables entregan mensajes comprensibles y no exponen trazas, tokens o detalles internos.

## Experiencia móvil

- Existe un siguiente paso visible y comprensible para cliente o prestador.
- Los controles importantes tienen texto, estado deshabilitado y tamaño adecuado para interacción táctil.
- Se verifican estados de carga, error, vacío, éxito y reintento.
- El flujo funciona en el navegador móvil; la validación en iOS y Android físicos se registra por separado y no se presupone.

## Calidad

- Pasan las pruebas automatizadas relacionadas con el cambio y la revisión de tipos del móvil.
- Se ejecuta el recorrido manual afectado con datos sintéticos y se registra el resultado.
- Los permisos se prueban con ambos roles y con un tercero sin acceso.
- En pagos se comprueban aprobación, rechazo/anulación o reintento, idempotencia y coincidencia del monto calculado por el servidor.
- Los defectos bloqueantes quedan resueltos o documentados como impedimento antes de presentar el incremento.

## Documentación y entrega

- README, manual técnico, arquitectura, requisitos o guía de QA se actualizan cuando cambia su contrato.
- El Product/Sprint Backlog refleja el estado real y no declara aceptación que no haya ocurrido.
- El código queda en un commit identificable y se publica en el repositorio de desarrollo.
- La copia académica registra el commit de origen y actualiza su manifiesto SHA-256.
- Otro integrante puede localizar los archivos y ejecutar el proyecto siguiendo instrucciones versionadas.

## Criterio de incremento entregable

El incremento completo debe permitir recorrer: inicio de sesión → selección en mapa → solicitud → cotización → materiales → pago de prueba → chat → inicio → evidencia → confirmación → valoración. Los reclamos y reembolsos se demuestran como un flujo administrativo separado. La operación con cobros reales, publicación en tiendas y aceptación legal no pertenecen a esta Definition of Done del MVP académico.
