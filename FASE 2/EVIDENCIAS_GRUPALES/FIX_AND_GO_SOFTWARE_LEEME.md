# Software FIX&GO — evidencia grupal de Fase 2

Copia del código publicado el **4 de noviembre de 2026** para revisión del equipo y del docente.

- **Repositorio de desarrollo:** [898benja/fix-and-go](https://github.com/898benja/fix-and-go).
- **Versión incluida:** [6e59671f82435891bd01732fbdacf599fa6c8b6a](https://github.com/898benja/fix-and-go/commit/6e59671f82435891bd01732fbdacf599fa6c8b6a).
- **Código:** [FIX_AND_GO_SOFTWARE](FIX_AND_GO_SOFTWARE/).
- **Instalación y ejecución:** [README](FIX_AND_GO_SOFTWARE/README.md) y [manual técnico](FIX_AND_GO_SOFTWARE/docs/MANUAL_TECNICO.md).
- **Visión, backlogs, retrospectivas, requisitos y pruebas:** [índice de entregables](FIX_AND_GO_SOFTWARE/docs/ENTREGABLES.md).
- **Integridad:** [manifiesto SHA-256](FIX_AND_GO_SOFTWARE_MANIFIESTO.json) de cada archivo incluido.

La carpeta contiene los archivos versionados del commit indicado: backend Django, app React Native/Expo, migraciones de base de datos, pruebas, Docker y documentación. No incluye historial Git, dependencias instaladas, bases de datos locales, archivos de entorno privados ni fotos privadas de trabajos. Los archivos `.env.example` son plantillas de configuración.

Para ejecutar, entrar a `FIX_AND_GO_SOFTWARE` y seguir su manual. Los pagos son de demostración: Webpay Plus utiliza exclusivamente el ambiente de integración y no mueve dinero real; también se conserva el simulador local. La configuración Docker es de desarrollo.

Para esta versión se ejecutaron 82 pruebas de backend, 12 pruebas del móvil, revisión de tipos y exportación de bundles web/iOS/Android. También se comprobó el recorrido manual con un servicio ficticio de $500: pago de integración, chat, evidencia, cierre, valoración y reversa de prueba. Docker se construyó y levantó con backend saludable en el puerto 18000 y app web en el 18090; las mismas pruebas pasaron dentro de los contenedores. El detalle y sus límites están en `docs/FLUJO_MVP_2026-11-04.md`.

Esta es una copia de entrega, no una sincronización automática. El desarrollo continúa en el repositorio original; futuras entregas deben registrar el nuevo commit y actualizar el manifiesto. El workflow incluido en la subcarpeta `.github` se conserva como parte del código original y no se ejecuta automáticamente como workflow del repositorio Capstone.
