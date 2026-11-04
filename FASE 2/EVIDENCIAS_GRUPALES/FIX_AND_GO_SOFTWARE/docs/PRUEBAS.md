# Plan y registro de pruebas

Corte vigente: 04-11-2026. Entorno automatizado: contenedores Linux, Python 3.13, SQLite temporal y Node 24; datos ficticios. No usar usuarios ni tarjetas reales.

## Resultado ejecutado
| Verificación | Resultado observado |
|---|---|
| Django suite completa | 82 pruebas aprobadas dentro del contenedor |
| Contratos y lógica móvil Node | 12 pruebas aprobadas |
| TypeScript | Sin errores |
| Exportación Expo | Web, Android e iOS generados correctamente |
| Migración de avatar | Aplicada en base aislada |
| Compose config | Sintaxis validada, sin imprimir secretos |
| Docker arranque/construcción | Construcción y arranque aprobados; API saludable y web HTTP 200 |
| Persistencia Docker | Tres perfiles sintéticos conservados tras reiniciar backend |
| UI web adaptable | Ficha sobre mapa revisada en 1280×720 y 390×844 |
| iOS/Android físicos | Pendiente; no confundir exportación con ejecución real |
| Estudio con adultos mayores | Pendiente |
| Carga y restauración integral | Pendiente |

## Reproducción automática
```sh
cd backend
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py test --noinput
cd ../mobile
npm ci
npm run typecheck
npm test
npx expo export --platform all
```
Usar una `.env` de desarrollo con secreto local. Django crea una base de test independiente. Para contenedor: `docker compose --env-file .env.docker exec backend python manage.py test --noinput`.

## Matriz de aceptación manual
| Caso | Pasos | Resultado esperado |
|---|---|---|
| QA-01 Perfil | Prestador carga JPEG; cliente toca marcador | Foto, descripción y calificación; sin valoración muestra Sin reseñas |
| QA-02 Reseñas | Cliente valora dos servicios completados con4 y5 | Promedio4,5 y contador2, no estrellas inventadas |
| QA-03 Cercanía | Elegir punto y categoría, cambiar radio | Resultados actualizados, respuesta obsoleta no sustituye selección |
| QA-04 Permisos | Tercera cuenta intenta solicitud/foto ajena | Acceso denegado |
| QA-05 Cobro | Cotización, materiales, token de tarjeta demo y pago Webpay en integración de prueba | Un total por orden; pendientes bloquean; comisión del 30 % solo sobre el servicio; materiales se transfieren íntegros al prestador |
| QA-06 Chat | Intentar antes/después de aprobación | Bloqueado antes, habilitado después |
| QA-07 Evidencia | Subir foto como prestador y confirmar como cliente | Prestador no confirma por cliente; sin foto no cierra |
| QA-08 Reclamo | Abrir, revisar en admin, reembolsar y repetir | Una alerta/reembolso; historial conservado |
| QA-09 Sanción | Tres casos distintos confirmados | Cuenta inactiva y token revocado |
| QA-10 Persistencia | Reiniciar servicios | Datos conservados |
| QA-11 Redes | Interrumpir API/Internet y recuperar | Error comprensible y reintento; tiles requieren Internet |
| QA-12 Dispositivos | Repetir01–11 en iOS y Android | Registrar modelo/versión, resultado y evidencia por caso |

Pasos detallados adicionales: [Auditoría y QA](AUDITORIA_Y_QA_2026_10_28.md).

## Formato de registro del equipo
Fecha real · caso · tester · equipo/SO · commit · datos sintéticos usados · esperado · observado · aprobado/fallido · captura · incidencia. No declarar aprobada una prueba que no se haya ejecutado. Benjamín informó pruebas manuales propias; las de Felipe/Daniel deben registrarse cuando ocurran.

## Evidencia de esta revisión
Las 82 pruebas Django se ejecutaron dentro del contenedor Linux y aprobaron. Las 12 pruebas móviles y la comprobación de TypeScript también aprobaron. Se verificaron la salud de la API, la respuesta HTTP 200 de la aplicación web y la persistencia de tres perfiles sintéticos después de reiniciar el backend. La integración Webpay utiliza exclusivamente el ambiente de integración de Transbank y un monto demostrativo de $500 CLP; no se efectuó un cobro real. Compose se detuvo sin eliminar el volumen para conservar los datos de demostración.

El recorrido automatizado cubre registro y roles, búsqueda geográfica, cotización, materiales, cálculo financiero, pago de prueba, habilitación del chat, evidencias fotográficas, término del trabajo, valoración, reclamos, reembolso demostrativo e inhabilitación por tres alertas confirmadas. La aceptación en teléfonos físicos iOS y Android, el estudio con personas mayores, la prueba de carga y la restauración integral permanecen pendientes y no se presentan como aprobados.

Capturas con datos ficticios: [escritorio](qa/map-profile-desktop.png) y [ancho móvil web](qa/map-profile-mobile-web.png). Se verificó abrir la ficha desde una tarjeta; las capturas muestran el caso sin foto y sin reseñas. La normalización de foto y el cálculo de promedio se validaron automáticamente; no se atribuye esta prueba a un dispositivo físico.
