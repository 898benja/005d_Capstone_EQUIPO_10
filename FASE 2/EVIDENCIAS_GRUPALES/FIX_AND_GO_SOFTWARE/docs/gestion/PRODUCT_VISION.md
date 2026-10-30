# Product Vision — FIX&GO

Versión 1.0 · 28 de octubre de 2026 · Equipo 10.

## Visión
Facilitar que personas de Santiago encuentren prestadores de servicios para el hogar, comparen perfiles y acuerden un trabajo con precios claros y seguimiento desde una aplicación móvil sencilla.

## Problema y usuarios
El cliente necesita identificar a quién solicitar ayuda, conocer su experiencia y evitar costos adicionales que no haya aprobado. El prestador necesita presentar sus servicios, organizar solicitudes y respaldar el trabajo realizado. Administración necesita revisar reclamos con antecedentes y decisiones trazables.

Usuarios: clientes, incluidos adultos mayores; prestadores independientes; administración académica del equipo. La validación inicial será con el equipo y eventualmente compañeros/familiares, sin afirmar que ya se realizaron esas pruebas externas.

## Propuesta de valor
Mapa como inicio, perfiles con foto/descripción/valoraciones reales, cotización y materiales aprobados antes del pago, conversación vinculada al servicio y fotos del resultado. El usuario debe entender el siguiente paso sin conocer la arquitectura.

## MVP y límites
React Native + Expo + TypeScript, Django REST Framework monolítico modular y SQLite local. Santiago y comunas habilitadas. La presentación puede funcionar en red local; la cartografía requiere Internet. Pagos, tarjeta y reembolsos exclusivamente simulados. Comisión propuesta e implementada: 30% del servicio, excluidos materiales. No se afirma disponibilidad GPS en vivo, validación profesional, transferencias ni boleta tributaria.

## Objetivos medibles de validación
- Completar solicitud → cotización → pago demo → trabajo/foto → confirmación sin fallos bloqueantes en todos los casos críticos de QA.
- Conservar los datos al reiniciar API y app; verificar mediante prueba de persistencia.
- Lograr que al menos 4 de 5 participantes de una prueba futura completen una solicitud sin ayuda del desarrollador; meta pendiente de medición.
- No exponer dirección/fotos a terceros en las pruebas cruzadas de permisos.
- Entregar instalación reproducible y evidencia de pruebas con resultados reales.

## Equipo y criterio de decisión
Benjamín Olmedo: programación e integración. Felipe Arce y Daniel Baeza: documentación, revisión y apoyo en validación; asignaciones específicas de este backlog son propuestas a ratificar en reunión. Las evaluaciones son individuales aunque el producto es grupal. Priorizar completar el recorrido sobre ampliar funciones; cualquier cambio de cobro requiere actualizar requisitos, pruebas y documentación.
