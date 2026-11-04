# FIX&GO · Proyecto Capstone — Equipo 10

FIX&GO es un MVP académico que conecta clientes de Santiago con prestadores de servicios para el hogar. El cliente explora prestadores en un mapa, solicita un servicio, revisa y acepta una cotización, aprueba materiales, realiza un pago de prueba, conversa dentro de la aplicación y confirma el trabajo mediante evidencias. El prestador administra solicitudes, cotiza, coordina trabajos y carga fotografías del resultado.

## Equipo

- Benjamín Olmedo: desarrollo e integración del software.
- Felipe Arce: documentación, revisión y apoyo en validación.
- Daniel Baeza: documentación, revisión y apoyo en validación.
- Carrera: Ingeniería Informática, Duoc UC sede Plaza Oeste.

## Estado del proyecto

El recorrido principal del MVP está implementado en React Native/Expo y Django REST Framework. Incluye roles cliente y prestador, mapa de Santiago, cotizaciones, materiales, Webpay Plus de integración sin cobros reales, chat posterior al pago, evidencias, valoración, reclamos y reembolsos de prueba. La versión incluida corresponde al commit [`6e59671`](https://github.com/898benja/fix-and-go/commit/6e59671f82435891bd01732fbdacf599fa6c8b6a) del repositorio de desarrollo.

## Entregables evaluables

La [matriz de cumplimiento de la directiva](FASE%202/EVIDENCIAS_GRUPALES/DOCUMENTACION_PROYECTO/00_MATRIZ_CUMPLIMIENTO.md) enlaza cada elemento solicitado con su documento verificable:

- Documento de inicio del proyecto y justificación de Scrum.
- Product Vision, Product Backlog, Sprint Backlog y retrospectivas.
- Definition of Done independiente.
- Arquitectura, modelo de datos y diagramas UML, incluido el diagrama de clases.
- Requisitos no funcionales, Docker, pruebas y manual técnico.
- Documento de innovación.

## Código y documentación

- [Copia versionada del software](FASE%202/EVIDENCIAS_GRUPALES/FIX_AND_GO_SOFTWARE/)
- [Descripción de la evidencia y versión incluida](FASE%202/EVIDENCIAS_GRUPALES/FIX_AND_GO_SOFTWARE_LEEME.md)
- [Repositorio de desarrollo](https://github.com/898benja/fix-and-go)
- [Índice técnico del software](FASE%202/EVIDENCIAS_GRUPALES/FIX_AND_GO_SOFTWARE/docs/ENTREGABLES.md)
- [Guía del flujo y pagos de prueba](FASE%202/EVIDENCIAS_GRUPALES/FIX_AND_GO_SOFTWARE/docs/FLUJO_MVP_2026-11-04.md)

## Arquitectura y tecnologías

- Aplicación: React Native, Expo, TypeScript y React.
- API: Python, Django y Django REST Framework, organizada como monolito modular.
- Datos: SQLite para el MVP local; migraciones Django versionadas.
- Servicios: OpenStreetMap/Leaflet y Webpay Plus en ambiente de integración.
- Ejecución: local, Expo Go/web o contenedores Docker de desarrollo.

## Ejecución rápida

La instalación completa y las variables necesarias están en el [manual técnico](FASE%202/EVIDENCIAS_GRUPALES/FIX_AND_GO_SOFTWARE/docs/MANUAL_TECNICO.md). El ambiente bancario es exclusivamente de integración y no cobra dinero real. No se deben usar tarjetas, RUT, claves ni domicilios reales en esta demostración.

## Estructura del repositorio

- `FASE 1/`: definición inicial y evidencias de la primera fase.
- `FASE 2/EVIDENCIAS_INDIVIDUALES/`: entregas individuales.
- `FASE 2/EVIDENCIAS_GRUPALES/`: guías, gestión Scrum, documentación técnica y snapshot verificable del software.
- `FASE 3/`: estructura reservada para la fase final.

Este repositorio documenta un proyecto académico. La pasarela, los comprobantes y los reembolsos implementados son de prueba; la operación comercial requiere cuenta de comercio, infraestructura productiva, revisión jurídica y validación con usuarios reales.

