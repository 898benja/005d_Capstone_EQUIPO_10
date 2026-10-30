# Backlog Trello FIX AND GO MVP

Fuente de trabajo preparada el 30 de septiembre de 2026 a partir del SRS, la Carta Gantt y el estado local del repositorio `fix-and-go`.

## Convenciones

- **P0** bloquea el recorrido principal del MVP.
- **P1** es necesario para una entrega estable y de alta calidad.
- **P2** se implementa solo después de estabilizar el flujo principal.
- **Existe local** significa que hay código sin publicar que debe revisarse, probarse y confirmarse antes de marcarlo como terminado.

## Lista Backend

### [P0][BE-01] Revisar y consolidar el backend existente

**Estado inicial:** Existe local.

**Trabajo:** revisar las apps `accounts`, `catalog` y `services`; confirmar que las rutas coinciden con el SRS; ejecutar checks; separar correcciones necesarias; publicar el código en una rama controlada.

**Aceptación:** Django inicia, `makemigrations --check` no detecta cambios, las rutas responden y el equipo conoce qué partes están terminadas.

### [P0][BE-02] Completar pruebas de registro e inicio de sesión

**Trabajo:** cubrir registro de cliente y prestador, correo duplicado sin distinguir mayúsculas, contraseña inválida, login correcto e incorrecto, cuenta inactiva, `me` y logout.

**Aceptación:** todos los casos aprueban y ningún token permite usar la API después de cerrar sesión.

### [P0][BE-03] Endurecer autenticación y sesión por token

**Trabajo:** definir expiración o rotación adecuada para el MVP, respuestas consistentes de autenticación y manejo de tokens inválidos.

**Aceptación:** los endpoints protegidos devuelven 401 sin credenciales y la app puede distinguir sesión expirada de un error de red.

### [P0][BE-04] Validar permisos por rol y propiedad

**Trabajo:** probar que cliente, prestador y terceros solo consultan o modifican recursos autorizados; ocultar recursos ajenos con respuestas consistentes.

**Aceptación:** las pruebas cruzadas impiden leer dirección, solicitudes, perfiles privados o cotizaciones ajenas.

### [P0][BE-05] Completar API de perfil de prestador

**Estado inicial:** Existe local.

**Trabajo:** validar nombre visible, experiencia, teléfono demo, categorías, comunas, estado activo y edición exclusiva del propietario.

**Aceptación:** el prestador actualiza su perfil; un cliente no puede editarlo; categorías y comunas inválidas se rechazan.

### [P0][BE-06] Completar catálogo y búsqueda de prestadores

**Estado inicial:** Existe local.

**Trabajo:** confirmar categorías y comunas activas, filtros por `category` y `commune`, orden estable, respuesta vacía y detalle público.

**Aceptación:** la búsqueda devuelve solo perfiles activos compatibles y no expone datos privados innecesarios.

### [P0][BE-07] Fortalecer creación de solicitudes

**Estado inicial:** Existe local.

**Trabajo:** validar que el prestador esté activo, que ofrezca la categoría solicitada y atienda la comuna seleccionada; validar fecha, descripción y dirección opcional.

**Aceptación:** no se puede crear una solicitud incoherente y una solicitud válida queda `PENDING` para ambas partes.

### [P0][BE-08] Completar listado detalle y cancelación de solicitudes

**Estado inicial:** Existe local.

**Trabajo:** filtrar por rol, ordenar, incluir historial mínimo, ocultar dirección en listados y aplicar transiciones válidas al cancelar.

**Aceptación:** cliente y prestador ven únicamente sus solicitudes y el cliente cancela solo antes de aceptar.

### [P0][BE-09] Fortalecer cotizaciones y transacciones

**Estado inicial:** Existe local.

**Trabajo:** asegurar una sola cotización activa, monto positivo entero, prestador asignado, aceptación y rechazo transaccionales, retiro permitido e idempotencia.

**Aceptación:** no existen estados parciales ni dobles cotizaciones activas aunque se repita una petición.

### [P0][BE-10] Crear suite de pruebas de solicitudes y cotizaciones

**Trabajo:** cubrir creación, listados por rol, detalle, dirección privada, cancelación, cotizar, aceptar, rechazar, retirar, estados inválidos y accesos de terceros.

**Aceptación:** la suite automatizada reproduce el recorrido principal y todas las pruebas aprueban.

### [P1][BE-11] Normalizar errores y respuestas de la API

**Trabajo:** definir estructura de error con código y mensaje; aplicar 400, 401, 403, 404 y 409 de manera consistente; documentar ejemplos.

**Aceptación:** el frontend puede presentar errores sin analizar formatos distintos por endpoint.

### [P1][BE-12] Implementar paginación y filtros estables

**Trabajo:** aplicar paginación real a prestadores y solicitudes, conservar filtros y definir orden por defecto.

**Aceptación:** respuestas grandes mantienen el contrato y el móvil puede cargar siguientes páginas.

### [P1][BE-13] Configurar Django Admin para operación demo

**Estado inicial:** Parcialmente existente.

**Trabajo:** añadir búsquedas, filtros y columnas útiles para usuarios, perfiles, solicitudes y cotizaciones; bloquear ediciones peligrosas cuando corresponda.

**Aceptación:** el equipo prepara y diagnostica la demo sin editar directamente SQLite.

### [P1][BE-14] Restringir CORS y configuración por ambiente

**Trabajo:** reemplazar `CORS_ALLOW_ALL_ORIGINS` por configuración explícita, validar `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS` y variables de entorno.

**Aceptación:** desarrollo local sigue funcionando y los valores sensibles no quedan versionados.

### [P1][BE-15] Documentar contrato de API y colección de pruebas

**Trabajo:** registrar rutas, métodos, permisos, cargas y respuestas; preparar comandos o colección para ejecutar el flujo completo.

**Aceptación:** otra persona puede probar la API sin leer el código fuente.

### [P1][BE-16] Mejorar diagnóstico y registro de errores

**Trabajo:** conservar `health`, registrar errores con contexto sin datos sensibles y añadir comprobación de base de datos.

**Aceptación:** una falla de configuración, red o base puede identificarse durante la presentación.

### [P2][BE-17] Implementar cierre simple del servicio

**Dependencia:** flujo de cotización estable.

**Trabajo:** añadir estados `IN_PROGRESS` y `COMPLETED` o una entidad de servicio simple con permisos para las partes.

**Aceptación:** una solicitud aceptada puede cerrarse sin romper el historial.

### [P2][BE-18] Implementar valoración posterior al cierre

**Dependencia:** BE-17.

**Trabajo:** permitir una valoración única del cliente, validar puntaje y calcular resumen público.

**Aceptación:** solo el cliente de un servicio completado puede valorar una vez.

## Lista Frontend

### [P0][FE-01] Definir navegación y estructura de la app móvil

**Trabajo:** incorporar navegación compatible con Expo SDK 57, separar rutas públicas, cliente y prestador, y documentar la estructura.

**Aceptación:** una sesión válida entra al flujo de su rol y no puede abrir pantallas de otro rol.

### [P0][FE-02] Crear cliente API centralizado

**Estado inicial:** solo existe el cliente de `health`.

**Trabajo:** URL configurable, headers, token, timeout, JSON, errores normalizados y funciones para todos los endpoints.

**Aceptación:** ninguna pantalla hace `fetch` directo y los errores tienen un formato común.

### [P0][FE-03] Persistir sesión de forma segura

**Trabajo:** guardar token con mecanismo compatible con Expo Go, restaurar sesión al abrir, consultar `me` y limpiar credenciales al cerrar o expirar.

**Aceptación:** la sesión sobrevive al reinicio y un logout elimina el acceso local.

### [P0][FE-04] Crear sistema visual y componentes reutilizables

**Trabajo:** definir colores, tipografía, espaciado, botones, campos, tarjetas, etiquetas de estado, carga, vacío y error.

**Aceptación:** las pantallas usan componentes consistentes y áreas táctiles legibles en iOS y Android.

### [P0][FE-05] Implementar pantalla de inicio de sesión

**Trabajo:** correo, contraseña, validaciones, carga, errores de credenciales y enlace a registro.

**Aceptación:** una cuenta demo ingresa y se dirige al inicio correcto según su rol.

### [P0][FE-06] Implementar registro de cliente y prestador

**Trabajo:** selección de rol, datos personales mínimos, nombre visible del prestador, validación de contraseña y errores del backend.

**Aceptación:** ambos roles pueden crear cuenta e iniciar su sesión sin usar Django Admin.

### [P0][FE-07] Implementar arranque de sesión y cierre

**Trabajo:** pantalla inicial de carga, restauración de usuario, navegación por rol, logout y manejo de token inválido.

**Aceptación:** no hay destellos de pantallas incorrectas ni sesión residual.

### [P0][FE-08] Crear inicio del cliente y catálogo

**Trabajo:** mostrar categorías activas, acceso a solicitudes y navegación hacia búsqueda.

**Aceptación:** el cliente selecciona una categoría y llega a prestadores filtrados.

### [P0][FE-09] Implementar búsqueda y filtros de prestadores

**Trabajo:** filtros por categoría y comuna, tarjetas, estados de carga, sin resultados, reintento y paginación.

**Aceptación:** los resultados coinciden con la API y el filtro puede limpiarse.

### [P0][FE-10] Implementar detalle del prestador

**Trabajo:** nombre, descripción, experiencia, categorías, comunas, verificación simulada claramente indicada y acción para solicitar.

**Aceptación:** el cliente comprende la oferta y puede iniciar una solicitud dirigida.

### [P0][FE-11] Implementar formulario de solicitud

**Trabajo:** categoría, comuna, descripción, fecha y horario opcionales, dirección privada opcional, confirmación y errores.

**Aceptación:** una solicitud válida aparece en las cuentas del cliente y prestador.

### [P0][FE-12] Implementar solicitudes del cliente

**Trabajo:** listado, filtros básicos, estados, detalle, cotización, cancelar, aceptar y rechazar.

**Aceptación:** el cliente completa todo el recorrido sin acceder a herramientas administrativas.

### [P0][FE-13] Implementar panel y solicitudes del prestador

**Trabajo:** resumen, listado de recibidas, detalle privado, estados y acceso a cotización.

**Aceptación:** el prestador ve únicamente solicitudes dirigidas a su cuenta.

### [P0][FE-14] Implementar edición del perfil del prestador

**Trabajo:** nombre visible, biografía, experiencia, teléfono demo, categorías, comunas y activo.

**Aceptación:** los cambios guardados se reflejan en la búsqueda del cliente.

### [P0][FE-15] Implementar creación y retiro de cotización

**Trabajo:** monto CLP, alcance, fecha, duración, notas, confirmación y retiro antes de la decisión.

**Aceptación:** la cotización aparece en el detalle del cliente y respeta estados válidos.

### [P1][FE-16] Completar estados de carga vacío error y sin conexión

**Trabajo:** cubrir todas las pantallas, ofrecer reintento y mostrar diagnóstico de WiFi o URL local cuando corresponda.

**Aceptación:** ninguna pantalla queda en blanco ni presenta mensajes técnicos crudos.

### [P1][FE-17] Validar accesibilidad y uso en pantallas pequeñas

**Trabajo:** etiquetas, foco, contraste, tamaños táctiles, teclado, scroll y lectores de pantalla básicos.

**Aceptación:** formularios y acciones siguen utilizables en un iPhone y Android de pantalla pequeña.

### [P1][FE-18] Probar recorrido completo en iOS y Android

**Trabajo:** ejecutar registro, búsqueda, solicitud, cotización y decisión con Expo Go en ambos sistemas.

**Aceptación:** cero defectos bloqueantes y evidencia de cada plataforma.

### [P1][FE-19] Preparar modo de demostración y contingencia

**Trabajo:** cuentas demo, mensajes estables, guía de red local, comprobación inicial y video de respaldo.

**Aceptación:** el equipo repite la demo tras restaurar datos y cambiar la IP del Mac.

### [P2][FE-20] Mostrar cierre y valoración del servicio

**Dependencia:** BE-17 y BE-18.

**Trabajo:** acciones y estados posteriores a la aceptación, formulario de valoración y resultado en perfil.

**Aceptación:** la extensión no interfiere con el recorrido principal.

## Lista Base de datos

### [P0][BD-01] Revisar y publicar migraciones actuales

**Estado inicial:** existen migraciones nuevas sin publicar.

**Trabajo:** revisar dependencias, nombres, reversibilidad y ejecución desde una base limpia.

**Aceptación:** `migrate` funciona desde cero y `makemigrations --check` no detecta diferencias.

### [P0][BD-02] Añadir restricciones de integridad de usuarios

**Trabajo:** asegurar correo único sin distinguir mayúsculas, rol válido y correspondencia entre rol prestador y perfil.

**Aceptación:** la base rechaza duplicados o relaciones incompatibles aunque no pasen por el formulario normal.

### [P0][BD-03] Añadir restricciones de solicitudes

**Trabajo:** proteger estados, conservar categoría y comuna, impedir cliente igual a prestador y validar relaciones de negocio en aplicación.

**Aceptación:** no se guardan solicitudes con relaciones imposibles.

### [P0][BD-04] Garantizar una sola cotización activa

**Trabajo:** añadir restricción condicional o diseño equivalente y probar concurrencia e idempotencia.

**Aceptación:** la base no admite dos cotizaciones `SUBMITTED` para la misma solicitud.

### [P0][BD-05] Completar semilla determinística de datos demo

**Estado inicial:** existe comando `seed_demo_data`.

**Trabajo:** hacerlo idempotente, actualizar datos existentes, evitar datos personales reales y crear escenarios pendiente, cotizado y aceptado.

**Aceptación:** ejecutar el comando varias veces produce el mismo conjunto utilizable.

### [P1][BD-06] Añadir índices para consultas principales

**Trabajo:** revisar índices para usuario y rol, perfil activo, categoría, comuna, estado y fechas de solicitudes y cotizaciones.

**Aceptación:** las consultas principales evitan recorridos completos innecesarios y conservan orden estable.

### [P1][BD-07] Implementar respaldo restauración y reinicio de demo

**Trabajo:** documentar copia segura de SQLite, restauración y comando para dejar estados iniciales.

**Aceptación:** el equipo recupera la demo en menos de cinco minutos.

### [P1][BD-08] Crear diccionario de datos y diagrama de relaciones

**Trabajo:** documentar entidades, campos, claves, privacidad, relaciones y estados.

**Aceptación:** el documento coincide con las migraciones publicadas y sirve para revisar cambios.

### [P1][BD-09] Probar migración desde base vacía y base anterior

**Trabajo:** automatizar una prueba de migración limpia y verificar conservación de los datos de la base inicial.

**Aceptación:** no se pierden datos y la aplicación arranca después de migrar.

### [P1][BD-10] Definir política de datos privados y demo

**Trabajo:** identificar dirección, teléfono, credenciales y evidencias; usar exclusivamente datos ficticios; evitar logs y capturas con información real.

**Aceptación:** la revisión del repositorio y evidencias no encuentra datos personales reales ni secretos.

### [P2][BD-11] Documentar futura migración a PostgreSQL

**Trabajo:** identificar tipos, restricciones y configuración que deben mantenerse portables.

**Aceptación:** existe una guía breve sin incorporar infraestructura cloud al MVP.

## Orden recomendado de ejecución

1. BE-01 y BD-01 para convertir el código local en una línea base verificable.
2. BE-02 a BE-10 y BD-02 a BD-05 para cerrar el contrato principal.
3. FE-01 a FE-15 para completar el recorrido móvil entre roles.
4. BE-11 a BE-16, FE-16 a FE-19 y BD-06 a BD-10 para estabilizar y demostrar.
5. Las tareas P2 solo comienzan cuando el recorrido principal no tiene defectos bloqueantes.
