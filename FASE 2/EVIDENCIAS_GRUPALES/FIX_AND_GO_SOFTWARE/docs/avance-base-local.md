# Base local — 16 de septiembre de 2026

## Implementado y comprobado

- Django 5.2.17 y DRF 3.16.1, aislados en `backend/.venv`.
- SQLite con migraciones aplicadas y usuario extensible sin roles de negocio aún.
- Endpoint de diagnóstico SQL y administración Django.
- App Expo SDK 57 / React Native 0.86 / TypeScript con pantalla de conexión.
- Cinco pruebas del backend aprobadas; chequeo Django sin problemas.
- TypeScript y compatibilidad de dependencias Expo aprobados.
- Bundles JavaScript de iOS y Android generados correctamente.
- API comprobada desde el Mac por loopback y dirección LAN.
- Workflow de GitHub para pruebas de backend y comprobaciones de móvil.

## Pendiente de comprobar

- Abrir en Expo Go compatible desde un iPhone y un Android reales.
- Confirmar comunicación entre teléfonos y Mac en la red de la presentación.
- Compilación nativa iOS: SDK 57 requiere Xcode 26.4+, mientras el Mac tiene 16.2.
- Docker y restauración de respaldos.
- Reglas de roles, solicitudes, cotizaciones, estados, cancelaciones y valoraciones antes de sus migraciones.

## Dependencias

`npm audit` detectó 10 entradas moderadas asociadas a la cadena Expo / xcode / uuid. No detectó entradas altas o críticas. La corrección automática sugerida implica retroceder a Expo 46 y no se aplicó por incompatibilidad. Se requiere revisar una actualización compatible de esa cadena antes de distribución. Este registro no equivale a una auditoría integral.

Los bundles no prueban la ejecución en teléfonos ni sustituyen una compilación nativa. La fase de Base local sigue en curso.
