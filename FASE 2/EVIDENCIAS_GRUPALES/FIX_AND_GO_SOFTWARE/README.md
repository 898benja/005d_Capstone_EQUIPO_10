# FIX&GO · MVP móvil

App académica de servicios para el hogar en Santiago. Cliente React Native + Expo + TypeScript; API monolítica modular Django REST Framework; SQLite local en el Mac. **Los pagos implementados son exclusivamente de demostración.**

## Documentación del equipo

El [índice de entregables](docs/ENTREGABLES.md) reúne Product Vision, Product Backlog, Sprint Backlog, retrospectivas, requisitos no funcionales, pruebas, Docker y manual técnico. Incluye responsables propuestos y distingue implementación de aceptación pendiente.

Para Docker: consultar [manual técnico](docs/MANUAL_TECNICO.md), puertos locales 18000/18090 y volumen aislado.

## Recorrido implementado

Registro e inicio de sesión → perfil reutilizable → mapa de prestadores → solicitud → cotización aceptada → materiales aprobados/rechazados → pago único demo con tarjeta ficticia guardada → chat e inicio del trabajo → fotos del resultado → confirmación del cliente → valoración. Un reclamo abre una revisión administrativa; aprobarlo genera reembolso demo y alerta al prestador. Tres alertas confirmadas deshabilitan su cuenta, conservando el historial.

- Roles separados: cliente y prestador; permisos por propietario en cada solicitud.
- Datos personales editables: nombre, apellido, teléfono, dirección y comuna habitual. La app reutiliza dirección y comuna al pedir otro servicio; puede modificarlas antes de enviar.
- Solicitudes y cotizaciones con validaciones, historial básico y transiciones controladas.
- El backend calcula el total; materiales pendientes bloquean el checkout y materiales rechazados quedan excluidos.
- Una sola orden por solicitud, snapshot de importes, rechazo y reintento sin duplicar órdenes.
- Teléfonos ocultos en el catálogo; conversación posterior al pago demo, con actualización manual.
- Tokens con expiración de 24 horas. SecureStore en dispositivos; memoria en la vista web.
- Inicio del prestador con resumen, trabajos recientes, clientes atendidos y mapa privado de sus solicitudes.
- Mapa Leaflet/OpenStreetMap con búsqueda por radio, puntos de atención voluntariamente publicados y ubicación privada de la solicitud. Requiere Internet para cargar cartografía.
- Comisión del 30% del servicio, sin comisión sobre materiales, incluida en el total; desglose calculado en servidor.
- Fotos privadas JPEG/PNG/WebP: hasta 10 por trabajo, 2 MB y 16 MP por archivo; se normalizan a JPEG sin EXIF.
- Administración de operaciones en modo consulta; los reclamos tienen una pantalla específica de revisión con fundamento obligatorio.

**Fuera del MVP:** pasarela bancaria y tokenización reales, boletas tributarias, transferencias al prestador, llamadas, notificaciones push, GPS en vivo, geocodificación de direcciones, verificación profesional y distribución en tiendas. No hay cuenta de comercio ni proveedor de pagos elegido. La tarjeta guardada es un identificador ficticio; la app no solicita PAN ni CVV.

Consulta la [auditoría y guía de QA vigente](docs/AUDITORIA_Y_QA_2026_10_28.md). Los informes anteriores describen versiones históricas; este recorrido reemplaza el cobro posterior al término del servicio.

## Ejecutar en el Mac

Requisitos: Python 3.13, Node 24, dependencias de `backend/requirements.txt` y `mobile/package-lock.json`.

### 1. API

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Solo en una instalación nueva; no sobrescribas tu configuración existente.
cp -n .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copia el secreto generado a `DJANGO_SECRET_KEY` en `backend/.env`. Configura `DJANGO_DEBUG=true` para el entorno local y añade la IP LAN del Mac a `DJANGO_ALLOWED_HOSTS`. No publiques `.env` ni bases de datos.

```sh
python manage.py migrate
# Opción explícita de prueba: no activa una pasarela ni cobra dinero.
PAYMENTS_DEMO_ENABLED=true python manage.py runserver 0.0.0.0:8000
```

La simulación exige simultáneamente `DJANGO_DEBUG=true` y `PAYMENTS_DEMO_ENABLED=true`. Sin esas dos condiciones responde 403. Estado de API y base: `http://127.0.0.1:8000/api/v1/health/`.

Usa cuentas nuevas desde la app. Para datos ficticios precargados en una base de desarrollo puedes ejecutar `python manage.py seed_demo_data`. Ese comando contiene credenciales públicas de demo: no usarlo en producción ni con información real. No cambia las contraseñas de usuarios ya existentes. `--reset` se rechaza si hay materiales, pagos o mensajes que deban conservarse.

### 2. App React Native

En otra terminal:

```sh
cd mobile
npm ci
cp -n .env.example .env
```

Configura `EXPO_PUBLIC_API_URL=http://IP_DEL_MAC:8000` en `mobile/.env`. En teléfono, `localhost` apunta al teléfono; ambos equipos deben poder comunicarse por Wi-Fi. La variable Expo es pública y no debe contener secretos.

```sh
npm start -- --lan
```

Abre el QR en Expo Go compatible con SDK 57. Para revisar la misma app en el navegador:

```sh
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npm run web
```

Reinicia Expo al cambiar la URL. La comprobación de conexión está en la pantalla de ingreso. Si la red del instituto aísla dispositivos, usa una red de pruebas que permita comunicación entre ellos.

## Validar cambios

```sh
cd backend
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py test --noinput
cd ../mobile
npm run typecheck
npm test
npx expo install --check
npx expo export --platform all
```

GitHub Actions verifica Django, migraciones, pruebas Python, TypeScript, pruebas del cliente HTTP y compatibilidad de dependencias Expo. Generar bundles no equivale a instalar ni probar la app en un teléfono físico.

## Documentación y carpetas

- [Funcionamiento del backend, API y conexión móvil](docs/backend-mvp-pagos.md).
- [Resultados QA y pruebas pendientes](docs/qa-mvp-2026-10-20.md).
- `backend/accounts/`: identidad y perfiles privados/profesionales.
- `backend/catalog/`: categorías, comunas, búsqueda y catálogo de prestadores.
- `backend/services/`: solicitudes, cotizaciones, estados y valoraciones.
- `backend/billing/`: materiales, liquidación, pago demo, comprobante y mensajes.
- `backend/core/`: health, errores y datos de demostración.
- `mobile/`: cliente principal, también ejecutable en web.
- `frontend/`: prototipo HTML previo, conservado como referencia; no es el cliente React Native ni implementa el nuevo flujo completo.
- `trello_fix_go_mvp_backlog.md`: backlog histórico; el estado implementado actual está en esta documentación.

## Compatibilidad

Expo SDK 57 usa React Native 0.86 y React 19.2.3. Para compilar iOS localmente requiere Xcode 26.4 o superior; el Mac revisado tenía Xcode 16.2. Los bundles iOS/Android se generan, pero no se afirma que exista una compilación nativa instalada. Ver [requisitos oficiales de Expo SDK 57](https://docs.expo.dev/versions/v57.0.0/).
