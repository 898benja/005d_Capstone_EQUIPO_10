# Manual técnico — FIX&GO

Versión 1.0 · 28 de octubre de 2026. Este documento describe la versión actual; los informes antiguos pueden conservar flujos históricos.

## 1. Componentes y responsabilidades
- `mobile/`: React Native 0.86, React19, TypeScript6 y Expo57. `App.tsx` controla sesión/navegación; `api.ts` construye rutas al backend, adjunta token y maneja errores/timeout.
- `accounts/`: usuarios, tokens y perfiles, punto público y foto. Foto se normaliza a miniatura JPEG de240×240 sin EXIF, almacenada como data URI; no admite URL externa arbitraria.
- `catalog/`: categorías, comunas, búsqueda por radio y valoración media calculada desde Rating. `avg_rating=null` y `rating_count=0` representan ausencia de reseñas.
- `services/`: solicitud, cotización, valoración, fotos privadas, estados y dashboard del prestador.
- `billing/`: materiales, orden/snapshot, tarjeta ficticia, mensajes, reclamos y alertas. Solo demostración.
- `core/`: salud, errores/paginación y semillas de datos.

El monolito mantiene permisos, cálculo y transacciones en un proceso Django. SQLite reduce dependencias para el Mac M1 con8GB. No hay microservicios, cola ni pasarela real.

## 2. Flujo y datos
Cliente → solicitud a prestador → cotización aceptada → materiales decididos → orden demo → aprobación → chat e inicio → fotos → confirmación por cliente → valoración. Un reclamo bloquea avance hasta revisión. Reembolso demo cierra cobro/chat; tres alertas confirmadas deshabilitan cuenta.

Relaciones: User tiene ProviderProfile opcional; ServiceRequest enlaza cliente/prestador/categoría/comuna; Quote y WorkEvidence pertenecen a solicitud; Rating, PaymentOrder y ServiceDispute son únicos por solicitud; ProviderWarning es único por reclamo. DemoCard es único por cliente. FKs protegidas preservan antecedentes de pagos y reclamos.

La API calcula importes enteros CLP, IVA ilustrativo incluido y comisión30% sobre servicio. Materiales aprobados se añaden sin comisión. Snapshot congela el total. Transacciones y restricciones únicas evitan duplicados; UPDATE inicial serializa operaciones en SQLite. No se ha demostrado rendimiento para alta concurrencia.

## 3. Mapa y ficha de prestador
`explore-map.tsx` ocupa el inicio con mapa, filtros flotantes y ficha inferior (lateral en escritorio). Tocar marcador selecciona al prestador. La ficha muestra foto o inicial, descripción, promedio real y número de reseñas. El punto del cliente activa consulta por radio; no hay geocodificación de domicilios ni GPS en vivo.

`/map/` sirve Leaflet con SRI. Web usa iframe y valida origen/ventana; nativo usa WebView y valida mensajes. No se envían tokens al mapa. Cartografía OpenStreetMap requiere Internet, atribución y políticas de uso. Los puntos son zonas de atención voluntarias, no ubicación actual de personas.

## 4. Instalación local
Seguir [README](../README.md): Python3.13, Node24, venv, requirements, `npm ci`, `.env` local y migraciones. Nunca copiar una `.env` por encima de otra existente.

```sh
cd backend
.venv/bin/python manage.py migrate
PAYMENTS_DEMO_ENABLED=true .venv/bin/python manage.py runserver 0.0.0.0:8000
# En otra terminal, desde la raíz:
cd mobile
EXPO_PUBLIC_API_URL=http://localhost:8000 npm run web
```

`DJANGO_DEBUG=true` y `PAYMENTS_DEMO_ENABLED=true` son ambos necesarios para simular pagos. En móvil físico cambiar localhost por IP LAN del Mac y permitir esa IP en ALLOWED_HOSTS. Mantener teléfono y Mac en red accesible; no publicar el servidor de desarrollo en Internet.

## 5. Docker para demostración web
Prerrequisitos: Docker Desktop activo y Compose v2. Desde la raíz, crear `.env.docker` con `DJANGO_SECRET_KEY` aleatorio de al menos50 caracteres. Se puede generar con `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`. Guardar el resultado localmente, no en commits.

```sh
docker compose --env-file .env.docker config --quiet
docker compose --env-file .env.docker up --build -d
docker compose --env-file .env.docker ps
```

App web: http://localhost:18090 · API/administración: http://localhost:18000 · salud: http://localhost:18000/api/v1/health/.

Los puertos se limitan a127.0.0.1. SQLite y fotos persisten en volumen `fixgo_data`, separado de tu base local. La API ejecuta migraciones antes de iniciar; frontend espera healthcheck. Es una configuración de desarrollo (Django runserver y Metro), no producción. No presupone QR nativo desde Docker; usar ejecución LAN local para teléfono.

```sh
docker compose --env-file .env.docker exec backend python manage.py createsuperuser
docker compose --env-file .env.docker exec backend python manage.py seed_map_demo
docker compose --env-file .env.docker logs --tail=100 backend
docker compose --env-file .env.docker down
```

`down` conserva el volumen. No usar `down -v` salvo que se quiera eliminar conscientemente todos los datos de ese entorno. La semilla de mapa crea prestadores sintéticos sin contraseña utilizable; para probar roles, registrar cuentas desde la app. No sobrescribe cuentas existentes.

## 6. Administración y soporte
En `/admin/`, entrar con superusuario local. Service disputes → Revisar reclamo permite leer motivo/fotos y fundamentar REFUND o REJECT. No sancionar automáticamente una denuncia. Los demás registros comerciales son de lectura. Tres alertas revocan token y deshabilitan perfil; no eliminan historia. Administración debe resolver otros trabajos abiertos de una cuenta suspendida.

## 7. Pruebas y mantenimiento
Comandos y casos en [PRUEBAS](PRUEBAS.md), riesgos en [auditoría](AUDITORIA_Y_QA_2026_10_28.md), requisitos en [RNF](REQUISITOS_NO_FUNCIONALES.md).

Respaldar SQLite mediante su API backup y copiar `media/`; una copia de solo la base no incluye fotos de trabajos. Probar restauración en otra carpeta/volumen antes de confiar en el respaldo. Foto de perfil sí está en SQLite. No subir base, fotos privadas, `.env` ni tokens al repositorio.

Ante error de API: comprobar salud, conexión y URL Expo. Ante mapa vacío: revisar publicación del prestador, categoría, cobertura y acceso a tiles. Ante 409: actualizar estado y comprobar pago/materiales/reclamo. Ante archivo rechazado: JPEG/PNG/WebP hasta2MB y16MP. Ante migración pendiente: respaldar y aplicar `migrate`, no editar tablas manualmente.

Para producción se requiere proyecto separado de despliegue: HTTPS, servidor WSGI/ASGI adecuado, gestión de secretos, almacenamiento/retención de fotos, política de privacidad validada y pasarela real con webhooks/conciliación.
