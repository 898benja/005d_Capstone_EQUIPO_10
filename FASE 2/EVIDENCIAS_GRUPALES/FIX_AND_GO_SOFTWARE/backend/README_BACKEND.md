# Backend FIX&GO

Guía técnica actualizada el 14 de octubre de 2026. Documenta el backend local
del MVP, sus contratos principales, las pruebas automatizadas y las tareas que
siguen abiertas antes de la validación física con Expo Go.

## Arquitectura y recorrido de una petición

La app móvil consume una API REST Django con SQLite local. Django Admin permite
administrar datos. No se requieren microservicios ni nube para este MVP.

1. `config/urls.py` dirige la URL a `accounts`, `catalog` o `services`.
2. DRF identifica al usuario mediante `Authorization: Token <token>`.
3. La vista verifica el rol y la propiedad del recurso.
4. El serializer valida los datos y prepara la representación JSON.
5. Para cotizaciones, `services/workflow.py` coordina la transacción y los estados.
6. El ORM persiste en SQLite; `core/exceptions.py` convierte excepciones DRF en errores JSON.

## Módulos

| Módulo | Responsabilidad |
|---|---|
| accounts | Usuario, rol CLIENT/PROVIDER, perfil, registro, login y logout |
| catalog | Categorías, comunas y búsqueda de prestadores |
| services | Solicitudes, cotizaciones, cierre y valoración |
| core | Salud de API, errores y comando de datos demo |
| config | Configuración, rutas principales y conexión de base de datos |

`views.py` maneja HTTP; `serializers.py` valida entrada y salida; `models.py`
define datos; `workflow.py` concentra cambios que deben confirmarse juntos.
Los comentarios nuevos explican por qué se usan transacciones y actualizaciones
condicionales, especialmente por las limitaciones de bloqueo de SQLite.

## Ejecutar en el Mac

Desde la carpeta `backend` del repositorio:

```sh
source .venv/bin/activate
pip install -r requirements.txt
# Si todavía no existe .env: copiar .env.example a .env y configurar sus valores.
python manage.py check
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Configurar `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` y `DJANGO_ALLOWED_HOSTS` en `.env`.
Para Expo Go, Mac y teléfono deben compartir red y la URL móvil debe usar la IP
del Mac, nunca localhost del teléfono. `runserver` es solo para desarrollo local.
Las pruebas usan una base temporal; no modifican los datos de demostración.

Para cargar un escenario completo y repetible:

```sh
python manage.py seed_demo_data
python manage.py seed_demo_data --reset
```

El comando es idempotente. La opción `--reset` elimina solamente las cuentas
conocidas de demostración y sus datos relacionados; conserva usuarios ajenos.
Las credenciales que imprime son exclusivamente locales y no deben reutilizarse.

## API principal

Todas las rutas siguientes parten de `/api/v1/` y terminan en `/`.

| Método | Ruta | Uso |
|---|---|---|
| GET | health/ | Comprobar API y base |
| POST | auth/register/ | Registrar cliente o prestador |
| POST | auth/login/ | Obtener token |
| GET | auth/me/ | Identidad autenticada |
| POST | auth/logout/ | Revocar token |
| GET, PATCH | auth/me/provider-profile/ | Consultar o editar perfil propio |
| GET | categories/, communes/ | Catálogo |
| GET | providers/, providers/{id}/ | Buscar y consultar prestadores |
| GET, POST | requests/ | Listar propias o crear como cliente |
| GET | requests/{id}/ | Detalle de las partes autorizadas |
| POST | requests/{id}/cancel/ | Cancelar antes de aceptar |
| GET, POST | requests/{id}/quote/ | Consultar o crear cotización |
| POST | requests/{id}/quote/accept/ | Aceptar como cliente |
| POST | requests/{id}/quote/reject/ | Rechazar como cliente |
| POST | requests/{id}/quote/withdraw/ | Retirar como prestador |
| POST | requests/{id}/start/ | Iniciar el servicio aceptado |
| POST | requests/{id}/complete/ | Completar el servicio iniciado |
| GET, POST | requests/{id}/rating/ | Consultar o registrar valoración |

El ID en las rutas de cotización es el de la **solicitud**, no el de la cotización.
Registro/login devuelven `{token, user}`. `me` devuelve el usuario sin contraseña.
La creación de solicitud usa `provider_id`, `category_id`, `commune_id`,
`description` y opcionalmente `address`, `preferred_date`, `preferred_time`.
La cotización usa `description`, `price` (CLP positivo entero), y opcionalmente
`proposed_date`, `estimated_duration`, `notes`. Los listados paginados
responden con `count`, `next`, `previous` y `results`; aceptan `page` y
`page_size`, con un máximo de 100 elementos por página.

## Estados y consistencia

| Acción | Solicitud antes | Solicitud después | Cotización |
|---|---|---|---|
| Crear cotización | PENDING | QUOTED | SUBMITTED |
| Aceptar | QUOTED | ACCEPTED | ACCEPTED |
| Rechazar | QUOTED | PENDING | REJECTED |
| Retirar | QUOTED | PENDING | WITHDRAWN |
| Cancelar | PENDING o QUOTED | CANCELLED | La enviada pasa a WITHDRAWN |

Se conserva la decisión del código previo: rechazar permite recibir otra
cotización y devuelve la solicitud a PENDING. Esto difiere del estado terminal
REJECTED propuesto en el SRS inicial y debe sincronizarse con esa especificación.

Cada operación inicia con un UPDATE condicionado al estado esperado dentro de
`transaction.atomic`. Un cambio incompatible devuelve 409. Si no se encuentra
la cotización esperada, se revierte también el cambio de solicitud. Repetir una
aceptación devuelve la cotización ya aceptada; rechazar y retirar no se repiten
automáticamente porque podría existir una nueva propuesta.

SQLite protege una sola cotización SUBMITTED o ACCEPTED por solicitud mediante
un índice único parcial y exige `price > 0`. `select_for_update` no ofrece bloqueo
de filas en SQLite. No se ha certificado carga concurrente elevada; esa prueba
y el manejo explícito de `database is locked` quedan pendientes.

## Registro y permisos

Usuario, perfil del prestador y token se crean en una sola transacción. Si falla
un paso, ninguno persiste. El correo se normaliza y se comprueba duplicación sin
distinguir mayúsculas en la API. Las contraseñas se validan y se almacenan con hash.
Login incorrecto o cuenta inactiva devuelve credenciales inválidas. Los registros
de login/registro usan ID interno, sin correo ni token.

El cliente crea y decide; el prestador asignado cotiza y retira. Un tercero recibe
404 al consultar una solicitud ajena. El listado excluye dirección privada.
Los tokens expiran después de 24 horas por defecto, valor configurable mediante
`TOKEN_EXPIRY_HOURS`. Un token vencido se elimina al utilizarlo y el login lo
rota antes de entregar una nueva sesión. Logout revoca el token inmediatamente.
Login y registro tienen límites por IP para reducir intentos automatizados.

## Pruebas y migraciones

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --verbosity 1
```

La suite contiene 35 pruebas de identidad, expiración y rotación de tokens,
perfiles, catálogo paginado, búsqueda de prestadores, permisos, cobertura del
prestador, cotizaciones duplicadas, aceptación repetida, cancelación, rechazo,
retiro, cierre, valoración, rollback, datos demo e integridad. La prueba de salud
admite campos diagnósticos adicionales sin perder las claves que consume Expo.

Las nuevas migraciones incluyen índices de modelos ya existentes, el modelo
Rating y los estados de cierre que estaban sin migrar, además de las restricciones
de cotizaciones. Antes de migrar una base compartida, respaldarla y revisar
cotizaciones activas duplicadas o de precio cero: las restricciones rechazan esos
datos; no se eliminan automáticamente para preservar el historial.

## Configuración de seguridad del MVP

`CORS_ALLOWED_ORIGINS` define los orígenes web autorizados. Si está vacío y
`DJANGO_DEBUG=true`, se permiten todos los orígenes para facilitar el desarrollo
local. En una ejecución que no sea local debe configurarse explícitamente y
mantener `DJANGO_DEBUG=false`. Expo Go nativo utiliza la IP del Mac declarada en
`DJANGO_ALLOWED_HOSTS`.

## Pendientes antes de declarar el MVP validado

- Ejecutar el recorrido completo desde Expo Go en un iPhone y un Android reales.
- Preparar y probar el procedimiento de respaldo/restauración de la base SQLite.
- Mantener una colección Postman, Bruno o equivalente con recorridos correctos y de error.
- Probar concurrencia y recuperación ante `database is locked`; SQLite no se ha
  certificado para carga alta y el alcance actual es una demostración local.
- Alinear el SRS y el frontend con la decisión de que rechazar una cotización
  devuelve la solicitud a `PENDING`.
