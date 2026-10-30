# FIX&GO — Auditoría, implementación y QA del MVP

Fecha: 28 de octubre de 2026. Entorno: desarrollo local, SQLite, datos sintéticos.
Repositorio: https://github.com/898benja/fix-and-go

## Resultado y límites

Se revisaron modelos, serializadores, permisos, transiciones, pagos, navegación Expo, dependencias y configuración. Se implementaron mapa, inicio del prestador, billetera ficticia, cobro previo al trabajo, fotos privadas, reclamos revisados y alertas. Esto no constituye certificación de seguridad, accesibilidad o disponibilidad de producción.

El MVP no mueve dinero. No integra Transbank/Mercado Pago, no tokeniza tarjetas reales, no realiza transferencias ni emite documentos tributarios. La tarjeta DEMO 4242 representa una referencia ficticia generada por el servidor. Ningún formulario recibe PAN o CVV. El usuario confirmó una demostración completa sin cobros reales.

Decisiones de cierre: comisión de 30% sobre el servicio, excluidos materiales; reclamos revisados por administración; tres alertas confirmadas deshabilitan la cuenta y revocan tokens, conservando historial. Estas reglas están explícitas en Información y privacidad y pueden revisarse como decisiones de producto.

## Arquitectura implementada

- **App:** React Native 0.86.3, React 19.2.3, TypeScript 6, Expo SDK 57. Comparte pantallas web/iOS/Android; no es una aplicación React web independiente. `App.tsx` controla sesión, navegación y errores. `api.ts` transporta JSON y token al monolito.
- **Servidor:** Python 3.13, Django 5.2.17, Django REST Framework 3.16.1. Monolito modular: accounts, catalog, services, billing, core. Evita red interna entre microservicios y reduce carga operacional del Mac local.
- **Datos:** SQLite mediante ORM y migraciones. Importes enteros CLP. `transaction.atomic` y un UPDATE inicial serializan cambios por solicitud; no se confía en `select_for_update` en SQLite. No se ha medido concurrencia sostenida.
- **Mapa:** Leaflet 1.9.4 en documento `/map/`, iframe web y react-native-webview 13.16.1 nativo. La app envía marcas mediante mensajes sin tokens. Se validan origen/ventana en web y contenido de mensajes. El backend calcula distancia Haversine y ordena antes de paginar.
- **Fotos:** expo-image-picker selecciona imágenes. La API verifica pertenencia, decodifica con Pillow 13, limita tamaño/dimensiones, elimina EXIF y guarda JPEG privado bajo `backend/media`. La descarga requiere autenticación y pertenencia; no se publica una ruta abierta `/media/`.
- **Administración:** Django Admin conserva operaciones de negocio como lectura. Los reclamos tienen una vista específica con fotos y fundamento de resolución. API de revisión restringida a staff activo.

## Modelo y relaciones nuevas

| Entidad | Relación y propósito |
|---|---|
| ProviderProfile | Coordenadas opcionales del punto público de atención, `map_visible`; restricciones de par y rango en BD |
| ServiceRequest | Coordenadas privadas de la solicitud; visibles solo para sus partes autorizadas |
| DemoCard | Una referencia UUID ficticia por cliente, no se devuelve el token al frontend |
| PaymentOrder | Una orden por solicitud; snapshot inmutable de servicio/materiales, comisión y monto del prestador; estado y fecha de reembolso |
| WorkEvidence | Hasta 10 archivos privados por solicitud, autor, descripción y fecha |
| ServiceDispute | Un reclamo por solicitud, motivo, estado, fundamento, revisor y fechas |
| ProviderWarning | Una alerta por reclamo confirmado; relación con prestador, sin duplicados |

Las migraciones son aditivas. Los pagos históricos no se recalculan: los nuevos campos de comisión tienen cero por defecto en órdenes anteriores. No confundir esos registros históricos con un nuevo desglose al 30%. Las semillas antiguas contienen ejemplos de estados anteriores; para demostrar el nuevo flujo se deben crear solicitudes nuevas.

## Recorrido funcional

1. Cliente guarda sus datos y selecciona prestador por mapa o listado. El punto elegido se conserva en la solicitud; dirección y comuna se confirman al enviarla.
2. Prestador cotiza y cliente acepta. Prestador propone materiales y cliente aprueba o rechaza cada uno.
3. Cliente confirma el total. Materiales pendientes impiden crear la orden; después de crearla no se pueden cambiar importes.
4. Cliente guarda una tarjeta ficticia y simula aprobación o rechazo. Reintentar usa la misma orden. Total y comisión se calculan en servidor, nunca desde datos enviados por la app.
5. Pago aprobado habilita chat y permite iniciar el trabajo. El chat se actualiza manualmente; no hay WebSocket ni notificaciones push.
6. Prestador adjunta fotos. Solo el cliente confirma el término y se exige al menos una evidencia. Una foto no demuestra automáticamente cumplimiento.
7. Si no se realizó el trabajo, cliente abre un reclamo. Mientras está abierto se bloquea el avance del servicio. Administración revisa antecedentes y fotos: rechaza el reclamo o concede reembolso demo completo y una alerta.
8. Reembolso cerrado impide volver a cobrar, avanzar o enviar chat. Tres alertas confirmadas deshabilitan al prestador y revocan sus tokens. No se borran los registros.

Ejemplo: servicio $30.000 + materiales $10.000 = cliente $40.000; comisión $9.000; prestador $31.000. La comisión no se suma nuevamente al cliente. IVA es ilustrativo, ya incluido, sin validez fiscal. El monto del prestador no implica que exista una transferencia.

## Contratos principales agregados

| Método y ruta bajo `/api/v1/` | Acceso |
|---|---|
| GET `providers/?latitude=...&longitude=...&radius_km=10` | Autenticado; solo prestadores activos con punto publicado |
| PATCH `auth/me/provider-profile/` | Propietario: punto y visibilidad |
| GET `provider/dashboard/` | Prestador: resumen, 20 trabajos recientes y 20 clientes atendidos propios |
| GET/POST/DELETE `wallet/demo-card/` | Cliente; demo habilitada |
| GET/POST `requests/{id}/evidence/` | Lectura partes; escritura prestador asignado |
| GET `requests/{id}/evidence/{photo_id}/` | Partes; imagen base64 privada sin cache compartida |
| GET/POST `requests/{id}/dispute/` | Partes; apertura solo cliente pagado |
| POST `admin/disputes/{id}/review/` | Staff activo; `decision: REFUND o REJECT`, `note` obligatorio |

## Hallazgos corregidos

- Prestadores sin coordenadas no podían encontrarse por cercanía: se agregaron coordenadas voluntarias, filtros, distancia y migraciones.
- Rol prestador aterrizaba solo en solicitudes/perfil: ahora tiene inicio con resumen y mapa privado.
- Configuración Referrer-Policy de Django impedía mostrar tiles OSM en el navegador: la página pública de mapa utiliza `strict-origin-when-cross-origin`; verificado visualmente con cartografía cargada.
- Coordenadas tenían demasiado protagonismo: quedaron como alternativa manual en búsqueda; perfil selecciona el punto tocando mapa. Se aumentó texto general a 17 px y etiquetas a 15 px.
- El scroll de página alteraba accidentalmente el zoom: rueda desactivada dentro del mapa; se conservan controles de zoom.
- Flujo anterior cobraba al terminar y el chat llegaba demasiado tarde: ahora se paga antes de empezar y el servidor verifica pago en cada transición.
- No había evidencia ni revisión de incumplimientos: se agregaron fotos privadas, reclamos y resolución idempotente, sin sancionar por la sola denuncia.
- Se actualizaron dependencias compatibles sin bajar Expo de versión ni forzar cambios mayores.

## Verificaciones realizadas

- 69 pruebas Django aprobadas, incluyendo permisos, estados, totales, pago, foto, reclamo, repetición de reembolso y tercera alerta.
- 10 pruebas Node aprobadas: contrato HTTP, errores, catálogos, ubicación válida y mensajes del mapa.
- TypeScript sin errores; migraciones sin cambios pendientes; exportación de bundles web, iOS y Android correcta.
- Pruebas visuales en navegador local: login cliente/prestador, mapa con cartografía, búsqueda por punto y radio, tres marcadores sintéticos, billetera ficticia y tablero del prestador.
- Las capturas en `docs/qa/` corresponden a datos de prueba, no a personas reales.

No se ha comprobado ejecución en dispositivos físicos iOS/Android, lector de pantalla, navegación por teclado completa, aceptación con adultos mayores, estrés de SQLite ni recuperación integral tras fallo del Mac. Exportar bundles no equivale a probar dispositivos.

## Riesgos y seguimiento antes de usar datos reales

| Prioridad | Hallazgo / límite | Acción y señal que vigilar |
|---|---|---|
| Alta | No existe pasarela real | Elegir comercio/proveedor; checkout alojado, tokenización del proveedor, webhooks firmados, idempotencia, conciliación y reembolsos antes de habilitar dinero real |
| Alta | Desarrollo local HTTP | HTTPS, secretos aleatorios, cookies seguras, HSTS y origen CORS explícito antes de publicar. `check --deploy` reporta advertencias; la de clave corta proviene del secreto sintético del test |
| Alta | Dependencias transitivas Expo | `npm audit` reportó 8 avisos (3 altos, 5 bajos), incluyendo zod/deepmerge en árbol Expo; no usar `--force` que propone bajar Expo a 51. Revisar parches compatibles. No se concluye explotación de la app a partir del aviso |
| Media | Alcance geográfico aproximado | Validación por caja de Santiago y catálogo de comunas disponibles; no es un polígono administrativo exacto. Si se amplía cobertura, añadir polígonos y probar bordes |
| Media | Mapa externo sin SLA | Vigilar errores de tiles y conexión; conservar listado como alternativa. Sin precarga masiva ni promesa de mapa sin conexión |
| Media | SQLite y volumen | Medir latencia p95, bloqueos, 409/500, volumen de fotos y respaldos. Evaluar PostgreSQL cuando haya concurrencia sostenida |
| Media | Copia de seguridad | Respaldar SQLite con API backup y `media/`; practicar restauración. Nunca subir base, fotos, tokens o `.env` a GitHub |
| Media | Moderación y comunicaciones | Revisar cola de reclamos y tiempos de resolución; registrar motivos. El MVP admite un reclamo por servicio, sin apelaciones automatizadas |
| Media | Baja de prestador con otros trabajos abiertos | Administración debe revisar sus solicitudes activas, comunicar resolución y resolver cada caso. No hay reasignación automática |
| Media | Accesibilidad y móviles | Pruebas físicas, texto ampliado, contraste, foco, lectores de pantalla, permisos de fotos, pérdida de Wi-Fi y navegación atrás |
| Baja | Consultas/listados | Medir consultas de serializadores por página y eliminar N+1 según evidencia; dashboard limita a 20, catálogo paginado |

No se implementó un monitor periódico ni envío de alertas externas. La tabla define qué revisar, no afirma que exista observabilidad desplegada.

## Guía de prueba manual

Preparación: instalar dependencias, migrar, habilitar `DJANGO_DEBUG=true` y `PAYMENTS_DEMO_ENABLED=true`; arrancar Django y Expo según README. Usar dos cuentas ficticias de cliente/prestador. Para administración, crear un superusuario local con `python manage.py createsuperuser`; no compartir credenciales ni publicarlas. Nunca usar tarjetas reales.

1. **Perfil y mapa:** prestador selecciona punto público de Santiago, categoría/comuna y guarda perfil visible. Cliente abre Explorar: debe ver el punto y su ficha. Ocultarlo debe retirarlo de nuevas búsquedas. Un punto sin publicar no debe revelar sus coordenadas.
2. **Cercanía:** cliente selecciona punto o introduce coordenadas válidas, cambia radio y busca. Debe ver distancia aproximada en línea recta. Probar vacío, fuera de Santiago y `nan`: no deben aceptarse. Los marcadores corresponden a la página actual.
3. **Solicitud:** cliente solicita categoría/comuna que ofrece el prestador. Tercera cuenta no debe leer la solicitud ni su ubicación. Prestador debe verla en Inicio y Solicitudes.
4. **Cotización/materiales:** prestador cotiza; cliente acepta. Añadir material; intentar confirmar total antes de decidirlo debe fallar. Aprobar o rechazar y verificar total; rechazados no suman.
5. **Pago:** confirmar total; guardar tarjeta demo; simular rechazo, luego aprobación. Recargar y verificar persistencia. Debe existir una sola orden; el total no cambia. Chat y comienzo bloqueados antes de aprobación.
6. **Trabajo/chat:** abrir conversación en ambas cuentas, enviar y actualizar. Iniciar como prestador. Cliente no debe poder iniciar; prestador no debe poder confirmar término por su cuenta.
7. **Fotos:** prestador adjunta JPEG/PNG/WebP pequeño; cliente abre foto. Tercera cuenta no puede acceder. Archivo de texto renombrado, foto demasiado grande o foto número 11 deben rechazarse. Cliente no puede subir evidencia como prestador.
8. **Cierre:** sin foto, confirmar debe fallar. Con foto, cliente confirma término y valora. Repetir valoración no duplica registros.
9. **Reclamo:** en otro servicio pagado, cliente informa trabajo no realizado. Prestador ve el estado; no recibe alerta automáticamente. Abrir Django Admin → Service disputes → Revisar reclamo; leer foto/motivo y registrar fundamento.
10. **Reembolso:** aprobar revisión debe mostrar DEMO_REFUNDED y una alerta, sin dinero real. Repetir resolución no duplica alerta. No se puede volver a cobrar o enviar chat. Rechazar reclamo mantiene pago y no crea alerta.
11. **Tres alertas:** repetir en tres solicitudes distintas del mismo prestador de prueba. Debe quedar inactivo, fuera del catálogo, sin token utilizable; su historial permanece.
12. **Fallos:** detener API: mostrar error recuperable. Volver a iniciar: reintentar. Sin Internet para tiles: el listado sigue siendo la alternativa. Revisar desde teléfono por IP LAN, nunca `localhost` del teléfono.

## Fuentes de integración

- Expo SDK 57 ImagePicker: https://docs.expo.dev/versions/v57.0.0/sdk/imagepicker/
- Expo WebView: https://docs.expo.dev/versions/v57.0.0/sdk/webview/
- Leaflet: https://leafletjs.com/reference.html
- Política de tiles OSM: https://operations.osmfoundation.org/policies/tiles/

OSM ofrece cartografía pública con atribución y políticas de uso, no una garantía de servicio gratuito ilimitado. No se incorporó Nominatim ni búsqueda automática de domicilios.

## Actualización: mapa y entregables
La interfaz de exploración ahora prioriza el mapa con filtros flotantes y ficha de prestador. El punto se selecciona tocando el mapa; los campos manuales de coordenadas de la exploración anterior fueron retirados. Se añadió foto de perfil normalizada y valoración media real con contador. La suite actual tiene 70 pruebas backend y 10 de contrato móvil; véase [registro vigente](PRUEBAS.md) y [entregables](ENTREGABLES.md).
