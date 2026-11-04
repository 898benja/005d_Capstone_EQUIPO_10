# Docker — ejecución reproducible

FIX&GO incluye contenedores de desarrollo para reducir diferencias entre los equipos macOS y Windows:

- [`compose.yaml`](../FIX_AND_GO_SOFTWARE/compose.yaml): coordina API y aplicación.
- [`backend/Dockerfile`](../FIX_AND_GO_SOFTWARE/backend/Dockerfile): Django y dependencias Python.
- [`mobile/Dockerfile`](../FIX_AND_GO_SOFTWARE/mobile/Dockerfile): cliente Expo/web.
- [Manual técnico](../FIX_AND_GO_SOFTWARE/docs/MANUAL_TECNICO.md): variables, comandos, puertos, volumen y solución de problemas.

## Objetivo

El entorno reproduce la demostración local y conserva la base de datos en un volumen. No constituye infraestructura productiva: utiliza servidor de desarrollo, SQLite y configuración local. Las variables privadas se entregan fuera de Git mediante `.env.docker`; las plantillas versionadas no contienen secretos.

## Verificación mínima

1. Crear `.env.docker` siguiendo el manual, con una clave Django local aleatoria.
2. Ejecutar `docker compose config` para validar la configuración.
3. Construir y levantar mediante `docker compose up --build`.
4. Verificar salud de la API y acceso a la app por los puertos documentados.
5. Ejecutar `docker compose down` al terminar; el volumen conserva datos mientras no se elimine expresamente.

Para Webpay de integración, el callback debe ser accesible desde el navegador que realiza la prueba y mantener las banderas de demostración. Nunca se deben usar credenciales comerciales en este entorno académico.
