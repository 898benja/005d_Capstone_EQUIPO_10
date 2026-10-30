# Requisitos no funcionales verificables

Versión 1.0 · 28-10-2026. Son criterios de calidad, no una declaración de cumplimiento total.

| ID | Atributo y requisito | Verificación / umbral | Estado |
|---|---|---|---|
| RNF-01 | Autenticación y privacidad | 100% casos cruzados niegan recursos ajenos; token caduca a 24 h | Pruebas automatizadas aprobadas |
| RNF-02 | Datos bancarios | Ninguna API acepta PAN/CVV; solo referencia ficticia | Tests de manipulación y wallet aprobados |
| RNF-03 | Integridad del cobro | Una orden por solicitud; repetición no duplica pago/alerta; CLP entero | Tests billing aprobados |
| RNF-04 | Fotos | JPEG/PNG/WebP, ≤2 MB y ≤16 MP; normalizar sin EXIF; hasta10 evidencias | Tests de validación y acceso aprobados |
| RNF-05 | Usabilidad | 4/5 participantes completan solicitud sin ayuda; pasos y errores comprensibles | Meta pendiente de estudio |
| RNF-06 | Accesibilidad | Texto ampliado, controles legibles y lector de pantalla en recorrido principal | Revisión visual parcial, validación pendiente |
| RNF-07 | Rendimiento | Meta API p95 <1 s en LAN con 5 usuarios y 100 prestadores; UI responde sin congelarse | No medido; no es SLA |
| RNF-08 | Persistencia | Reiniciar conserva usuarios, órdenes y fotos; restaurar respaldo en ≤30 min | Migraciones/respaldo realizados; restauración pendiente |
| RNF-09 | Compatibilidad | Mismo recorrido en iOS y Android físicos compatibles con SDK57 | Bundles exportados; dispositivos pendientes |
| RNF-10 | Mantenibilidad | Migraciones, tests, manual y cambios de contrato en mismo commit | Aplicado; revisión continua |
| RNF-11 | Portabilidad | Instalación local y Compose documentados, sin secretos versionados | Preparado; estado de ejecución en PRUEBAS.md |
| RNF-12 | Geografía | Punto válido en caja Santiago; solicitud en comuna ofrecida; datos no publicados ocultos | Tests geo aprobados; polígono exacto pendiente |
| RNF-13 | Dependencias externas | Error recuperable si API/mapa no responde; sin prometer cartografía offline | Manejo implementado; pruebas de red físicas pendientes |
| RNF-14 | Observabilidad | Revisar 5xx, 409, latencia, fallos de tiles y espacio; no registrar secretos | Logs básicos; no monitoreo automático desplegado |

Antes de producción: HTTPS, CORS restringido, cookies seguras, gestión de secretos, política de retención y revisión de vulnerabilidades. El entorno local de demostración no satisface por sí solo esos requisitos.
