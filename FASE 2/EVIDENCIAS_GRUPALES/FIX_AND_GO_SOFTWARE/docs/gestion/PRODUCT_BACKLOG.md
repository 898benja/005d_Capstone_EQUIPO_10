# Product Backlog — FIX&GO

Corte: 28-10-2026. Estado respaldado por código y pruebas locales; no implica aceptación docente ni verificación en teléfono físico. Sustituye como planificación vigente el backlog inicial de septiembre, que se conserva como antecedente.

P0: bloquea recorrido; P1: estabilidad/entrega; P2: extensión. «Implementado» requiere todavía validación de aceptación del equipo. Desarrollo: Benjamín; apoyo documental/QA: Felipe y Daniel, propuesto.

| ID | Prioridad | Historia / resultado | Criterio de aceptación | Estado / evidencia |
|---|---|---|---|---|
| PB-01 | P0 | Como usuario, crear cuenta e iniciar sesión por rol | Token válido; errores claros; tercero sin acceso | Implementado, accounts/tests.py |
| PB-02 | P0 | Como cliente, conservar mis datos | Dirección/comuna reutilizable y editable | Implementado, billing/tests.py |
| PB-03 | P0 | Como prestador, publicar mi perfil | Foto propia, descripción, categoría, comuna y punto voluntario | Implementado, accounts/test_avatar.py y catalog/test_geo.py |
| PB-04 | P0 | Como cliente, elegir prestador en mapa | Tocar marcador abre ficha; foto, promedio y número de reseñas; sin reseñas no inventa estrellas | Implementado; UI web revisada, aceptación en teléfono pendiente |
| PB-05 | P0 | Solicitar y cotizar trabajo | Cobertura validada, cotización única activa, permisos por parte | Implementado, services/tests.py |
| PB-06 | P0 | Aprobar materiales y pagar demo | Pendientes bloquean pago; rechazados no suman; reintento no duplica | Implementado, billing/tests.py |
| PB-07 | P0 | Guardar tarjeta ficticia | Sin PAN/CVV; referencia por cliente, eliminable | Implementado, billing/test_wallet.py |
| PB-08 | P0 | Conversar después de pagar | Bloqueado antes de pago y después de reembolso | Implementado, billing/tests.py y test_disputes.py |
| PB-09 | P0 | Respaldar y confirmar trabajo | Fotos privadas; tercero bloqueado; cliente confirma tras foto | Implementado, services/test_evidence.py |
| PB-10 | P0 | Resolver incumplimientos | Reclamo no sanciona automáticamente; revisión, reembolso demo idempotente | Implementado, billing/test_disputes.py |
| PB-11 | P1 | Alertar y deshabilitar reincidentes | Tres alertas confirmadas revocan acceso conservando historial | Implementado, billing/test_disputes.py |
| PB-12 | P1 | Inicio del prestador | Resumen, trabajos y clientes propios, mapa privado | Implementado, services/test_dashboard.py |
| PB-13 | P1 | Informar comisión y privacidad | 30% servicio, no materiales; total no aumenta por comisión | Implementado, information.tsx y pruebas de importes |
| PB-14 | P1 | Instalar con Docker | Compose construye, API saludable, app accesible y datos persistentes | Verificado: construcción, salud, web y persistencia; PRUEBAS.md |
| PB-15 | P1 | Validar iOS/Android físicos | Login, mapa, foto, sesión, pago demo y recuperación de red en ambos | Pendiente |
| PB-16 | P1 | Validar uso con adultos mayores | 4/5 completan solicitud sin ayuda; registrar dificultades | Pendiente, objetivo no medido |
| PB-17 | P1 | Respaldar y restaurar | Recuperar SQLite + fotos en entorno aislado | Respaldo local realizado; restauración integral pendiente |
| PB-18 | P1 | Revisar dependencias y configuración | Resolver/justificar avisos; HTTPS si se publica | Pendiente; auditoría vigente |
| PB-19 | P2 | Pasarela real y tarjeta tokenizada | Comercio, checkout alojado, webhooks firmados, conciliación | Fuera del MVP actual |
| PB-20 | P2 | Cobertura geográfica exacta | Polígono administrativo y pruebas de límites | Pendiente; MVP usa caja aproximada y catálogo |

## Definition of Ready
Historia comprendida, rol y criterio claros, dependencias identificadas, datos sintéticos disponibles y alcance compatible con el sprint.

## Definition of Done
Código revisado, migraciones versionadas, pruebas pertinentes aprobadas, UI revisada, documentación actualizada, sin secretos en Git, commit publicado y aceptación del equipo registrada. «Implementado» no se convierte en «aceptado» hasta registrar esa revisión.

## Cambios de alcance
El flujo previo de cobro posterior al trabajo fue reemplazado por pago tras cotización/materiales y antes de comenzar. Se mantiene una sola orden; no se admite agregar materiales después de congelar el total. Cambios posteriores requieren una nueva decisión de producto.
