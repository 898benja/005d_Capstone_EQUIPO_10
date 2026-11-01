# Duoc UC
**ESCUELA DE INFORMÁTICA Y TELECOMUNICACIONES**

---

# Fix&Go
**"Definición y Priorización de las Historias de Usuario"**

* **Asignatura:** Capstone (`APT122`)
* **Sección:** 005-D
* **Profesor:** José Luis Pino
* **Integrantes:** Felipe Arce, Daniel Baeza y Benjamín Olmedo
* **Sede:** Duoc UC Plaza Oeste

---

## ÍNDICE
1. Introducción y propósito del Product Backlog
2. Metodología de trabajo ágil (Kanban y Scrum adaptado)
3. Organización del Product Backlog
4. Historias de usuario priorizadas
5. Matriz de priorización
6. Criterios de aceptación del equipo
7. Gestión de roles dentro del Backlog
8. Glosario

---

## 1. Introducción y propósito del Product Backlog

### Nombre del producto
**Fix&Go** — Plataforma Transaccional de Servicios para el Hogar.

### Tipo de proyecto
Proyecto de desarrollo de software desde cero (MVP), implementado bajo una arquitectura de **monolito modular** con un backend en **Django REST Framework (Python)** utilizando SQLite como persistencia relacional local, y un cliente multiplataforma desarrollado en **React Native con Expo y TypeScript** (compatible con iOS, Android y Web).

### Descripción del producto
**Fix&Go** es un ecosistema digital diseñado para conectar de manera segura, directa y transparente a propietarios y residentes de hogares con especialistas técnicos calificados (en rubros críticos como **Agua/Gasfitería, Electricidad y Gas**). El sistema resuelve la informalidad y la desconfianza del mercado tradicional mediante un flujo transaccional controlado: solicitud geolocalizada por comuna, cotización formal, aceptación atómica protegida contra condiciones de carrera, aprobación granular de materiales adicionales en terreno, liquidación financiera inmutable en servidor (con un **modelo de retención del 30% como margen institucional para Fix&Go** y un sistema de **bonos por desempeño semanal para los prestadores**), y apertura controlada del chat interno únicamente tras registrar el pago de demostración académica.

### Usuario principal y actores del ecosistema
* **Cliente (Solicitante):** Actor que busca especialistas, crea solicitudes, acepta cotizaciones, aprueba materiales extras, ejecuta el pago demo y valora el servicio.
* **Prestador (Especialista):** Actor que configura su perfil técnico, emite cotizaciones vinculantes, gestiona el avance de la obra, propone insumos adicionales y accede a bonos semanales por productividad.

### Objetivo del Product Backlog
Organizar y priorizar las funcionalidades necesarias para construir y validar el MVP de **Fix&Go**, permitiendo planificar las iteraciones del equipo mediante historias de usuario plenamente trazables que entregan valor incremental alineado con los requerimientos académicos de Duoc UC.

---

## 2. Metodología de trabajo
El proyecto se desarrolla bajo un enfoque ágil adaptado a los tiempos del curso Capstone, utilizando tableros Kanban (Trello) y reuniones de coordinación semanal presenciales los días miércoles, además de seguimiento diario entre los integrantes. Las iteraciones se agrupan en cuatro grandes fases:
* **Fase 1 (Semanas 1–4):** Definición del problema, alcance, restricciones y modelado de datos relacional.
* **Fase 2 (Semanas 5–12):** Desarrollo del monolito modular en Django, configuración de vistas móviles en React Native y endurecimiento de la autenticación por token.
* **Fase 3 (Semanas 13–15):** Pruebas de integración HTTP real (91 tests ejecutados), validación de casos borde y estabilización del flujo de pagos y materiales.
* **Fase 4 (Semanas 16–18):** Ensayos generales en dispositivos físicos, consolidación de evidencias en GitHub y defensa del proyecto.

---

## 3. Organización del Product Backlog
El Product Backlog se estructura en Épicas funcionales, Historias de Usuario (HU) con su respectiva prioridad, y Criterios de Aceptación verificables que aseguran el cumplimiento de los estándares técnicos y de negocio de la plataforma.

---

## 4. Historias de usuario priorizadas

### Épica 1: Gestión de Identidad y Autenticación (`accounts`)
*Esta épica agrupa las funcionalidades de registro, inicio de sesión y control estricto de privilegios por rol y propiedad.*

#### **HU-01: Registro y Autenticación por Token**
* **Como** usuario nuevo (sea cliente o prestador),
* **quiero** registrarme en el sistema e iniciar sesión mediante credenciales seguras,
* **para** obtener un Token de acceso con expiración de 24 horas que me permita operar dentro de la aplicación móvil.
* **Prioridad:** Alta
* **Criterios de Aceptación:**
  1. El sistema valida que el correo electrónico sea único en la base de datos.
  2. Al autenticarse correctamente, la API retorna un Token de sesión activo.
  3. Las peticiones subsiguientes del cliente móvil (`api.ts`) inyectan obligatoriamente el encabezado `Authorization: Token [valor]`.

#### **HU-02: Control de Permisos por Rol y Propiedad**
* **Como** sistema de seguridad de la API,
* **quiero** validar que cada petición HTTP verifique el rol del usuario (Cliente vs. Prestador) y su propiedad sobre el recurso solicitado,
* **para** impedir que terceros no autorizados consulten o modifiquen datos ajenos.
* **Prioridad:** Alta
* **Criterios de Aceptación:**
  1. Si un usuario intenta acceder a una solicitud que no le pertenece, el servidor responde con un código `HTTP 404 (Not Found)` para ocultar la existencia del recurso.
  2. Las acciones exclusivas de prestador (como cotizar o proponer materiales) rechazan tokens pertenecientes a cuentas con rol de cliente.

---

### Épica 2: Catálogo y Cobertura Geográfica (`catalog`)
*Permite la exploración filtrada de especialistas según especialidad y comuna.*

#### **HU-03: Búsqueda y Filtrado de Prestadores**
* **Como** cliente residencial,
* **quiero** buscar especialistas filtrando por categoría de servicio (**Agua/Gasfitería, Electricidad, Gas**) y por comuna de cobertura,
* **para** encontrar profesionales disponibles y certificados en mi zona geográfica.
* **Prioridad:** Alta
* **Criterios de Aceptación:**
  1. La interfaz muestra un listado dinámico de especialistas que cumplen con los filtros seleccionados.
  2. Cada tarjeta de prestador exhibe sus años de experiencia, comuna base y certificaciones (ej. SEC clase B).
  3. Los números de teléfono personales permanecen ocultos en el catálogo público para prevenir la desintermediación.

---

### Épica 3: Ciclo de Vida de Solicitudes y Cotizaciones (`services`)
*Gestiona la creación de solicitudes, emisión de cotizaciones y la aceptación atómica.*

#### **HU-04: Creación de Solicitudes de Servicio**
* **Como** cliente,
* **quiero** crear una solicitud detallando la falla domiciliaria, la comuna y la categoría requerida,
* **para** iniciar el proceso formal de atención con estado inicial `PENDING`.
* **Prioridad:** Alta
* **Criterios de Aceptación:**
  1. La solicitud vincula de forma relacional al cliente autenticado, la categoría y la comuna.
  2. El sistema asigna el estado `PENDING` permitiendo que los prestadores de la zona visualicen el requerimiento.

#### **HU-05: Emisión y Aceptación Atómica de Cotizaciones**
* **Como** prestador y cliente,
* **quiero** que el prestador emita una cotización en pesos chilenos y que el cliente pueda aceptarla de forma segura,
* **para** transicionar la solicitud al estado `ACCEPTED` sin riesgo de inconsistencias ante accesos simultáneos.
* **Prioridad:** Alta
* **Criterios de Aceptación:**
  1. El prestador emite una cotización vinculando un precio en `CLP` (`QUOTED`).
  2. La aceptación por parte del cliente se ejecuta bajo un bloque atómico (`transaction.atomic`) y un `UPDATE` condicionado en SQLite.
  3. Si ocurre una condición de carrera simultánea, el sistema responde de forma controlada con un conflicto `HTTP 409` sin duplicar efectos.

---

### Épica 4: Materiales Adicionales, Liquidación Financiera y Modelo de Negocio (`billing`)
*Controla los insumos extras en terreno, el bloqueo de checkout, el margen institucional del 30% y los bonos semanales.*

#### **HU-06: Gestión y Aprobación de Materiales Adicionales**
* **Como** prestador y cliente,
* **quiero** que el prestador proponga repuestos o insumos extras necesarios durante la obra y que el cliente deba aprobarlos o rechazarlos explícitamente,
* **para** evitar cobros sorpresivos en el monto final.
* **Prioridad:** Media
* **Criterios de Aceptación:**
  1. El prestador registra ítems en `MaterialExtra` indicando cantidad y precio unitario.
  2. La API bloquea preventivamente cualquier intento de realizar el *checkout* mientras existan materiales en estado pendiente de aprobación.
  3. El cliente debe aprobar o rechazar cada ítem individualmente antes de recalcular el cobro final.

#### **HU-07: Cálculo Inmutable de Liquidación y Margen 30%**
* **Como** administrador de la plataforma,
* **quiero** que el servidor Django calcule automáticamente el total sumando el servicio y los materiales aprobados, congelando una copia inmutable (*snapshot*) que destine el **30% de margen institucional a Fix&Go** y el **70% al prestador**,
* **para** garantizar la sostenibilidad financiera del negocio.
* **Prioridad:** Alta
* **Criterios de Aceptación:**
  1. El cliente nunca envía el monto total por la petición; el servidor calcula y congela los valores de Neto e IVA ilustrativo (19%).
  2. El sistema separa internamente la retención operativa del 30% para Fix&Go y el abono del 70% para el prestador.
  3. El flujo de pago se ejecuta mediante una simulación académica controlada (`DEMO_PAID`) que emite un comprobante sin validez tributaria.

#### **HU-08: Bonos por Desempeño Semanal para Prestadores**
* **Como** prestador de servicios,
* **quiero** acumular bonificaciones económicas basadas en la cantidad y calidad de trabajos semanales completados,
* **para** recibir incentivos de retención y productividad dentro de la plataforma.
* **Prioridad:** Media
* **Criterios de Aceptación:**
  1. El sistema procesa de forma periódica el conteo de servicios completados por cada prestador durante el ciclo semanal.
  2. Al superar el umbral establecido, se registra automáticamente el bono correspondiente asociado al perfil del especialista.

---

### Épica 5: Soporte, Chat Anti-Fuga y Valoraciones (`core` / `services`)
*Habilita la comunicación segura post-pago y la reputación mediante valoraciones.*

#### **HU-09: Desbloqueo del Chat Interno Post-Pago**
* **Como** usuario del sistema,
* **quiero** que el canal de mensajería interna (`ServiceMessage`) permanezca restringido durante la ejecución y se habilite únicamente tras confirmar el pago de demostración,
* **para** prevenir la desintermediación y asegurar que las partes operen bajo el resguardo de la plataforma.
* **Prioridad:** Media
* **Criterios de Aceptación:**
  1. El acceso al chat arroja restricciones si el estado de la orden no es `DEMO_PAID`.
  2. Una vez registrado el pago demo, se abre el canal de comunicación directa entre cliente y prestador.

#### **HU-10: Valoración y Calificación del Servicio**
* **Como** cliente,
* **quiero** calificar el servicio completado otorgando un puntaje de 1 a 5 estrellas y un comentario público,
* **para** construir el historial de reputación del prestador.
* **Prioridad:** Media
* **Criterios de Aceptación:**
  1. El módulo de valoración se habilita al alcanzar el estado `COMPLETED`.
  2. El sistema exige un puntaje numérico del 1 al 5 y almacena el comentario asociado de forma inmutable.

---

## 5. Matriz de priorización

| ID | Épica | Historia de Usuario | Prioridad | Justificación Técnica y de Negocio |
| :--- | :--- | :--- | :--- | :--- |
| **HU-01** | Accounts | Registro y Token (24h) | Alta | Núcleo de seguridad; requisito indispensable para cualquier petición autenticada. |
| **HU-02** | Accounts | Control de permisos (Rol/Propiedad) | Alta | Garantiza aislamiento de datos y respuestas HTTP 404 ante accesos no autorizados. |
| **HU-03** | Catalog | Búsqueda y filtros por comuna | Alta | Permite al cliente descubrir especialistas geográficamente cercanos y calificados. |
| **HU-04** | Services | Creación de solicitudes | Alta | Punto de partida del recorrido operativo del MVP. |
| **HU-05** | Services | Cotización y aceptación atómica | Alta | Crítico para evitar condiciones de carrera mediante `transaction.atomic` y códigos 409. |
| **HU-06** | Billing | Gestión de materiales y bloqueo | Media | Evita cobros sorpresivos; exige aprobación explícita antes de permitir el checkout. |
| **HU-07** | Billing | Liquidación inmutable y margen 30% | Alta | Resguarda la lógica financiera en servidor, congelando el snapshot y el desglose 30/70. |
| **HU-08** | Billing | Bonos semanales por desempeño | Media | Estímulo de retención y productividad para los prestadores activos. |
| **HU-09** | Core | Desbloqueo de chat post-pago | Media | Mecanismo anti-fuga para retener la interacción dentro de la plataforma. |
| **HU-10** | Services | Valoración de servicio (1-5★) | Media | Cierra el ciclo operativo consolidando la reputación del especialista. |

---

## 6. Criterios de aceptación del equipo

### Definición de Listo (DoR)
Una historia de usuario puede tomarse en un sprint cuando:
1. Cuenta con criterios de aceptación claros acordados con el Product Owner (Daniel Baeza).
2. Se encuentra vinculada a las pantallas de la interfaz móvil en React Native / Expo.
3. Tiene definido el endpoint bajo `/api/v1/` y el contrato de datos serializados en Django.
4. Ha sido estimada y desglosada por el equipo técnico.

### Definición de Terminado (DoD)
Una historia se considera completamente finalizada cuando:
1. El código backend y frontend está integrado en el repositorio oficial de Git sin romper la compilación.
2. Supera las pruebas automatizadas de servidor e integración HTTP real (respaldado por los 91 tests ejecutados).
3. Fue verificada visualmente en el flujo operativo de la aplicación.
4. No genera errores en consola ni datos de prueba inconsistentes.

---

## 7. Gestión de roles dentro del Backlog

| Rol en el Equipo | Responsabilidad frente al Backlog |
| :--- | :--- |
| **Product Owner** — Daniel Baeza | Prioriza las historias, valida que los requerimientos reflejen las necesidades reales de los clientes y prestadores, y ajusta la planificación según la rúbrica de Duoc UC. |
| **Desarrollador Principal** — Benjamín Olmedo | Estima la complejidad técnica en Django REST Framework, SQLite y React Native; asegura la integridad transaccional y el modelo financiero (30/70). |
| **QA y Testing** — Felipe Arce | Diseña y ejecuta los casos de prueba (unidades, cliente HTTP simulado e integración real), asegurando que cada historia cumpla con los estándares de calidad del MVP. |

---

## 8. Glosario
* **Monolito Modular:** Arquitectura de software donde todo el sistema reside en un único proceso (Django), pero estrictamente dividido en módulos independientes (`accounts`, `catalog`, `services`, `billing`).
* **Transacción Atómica (`transaction.atomic`):** Bloque de ejecución en base de datos donde todas las operaciones se realizan con éxito o se revierten por completo si una falla.
* **Snapshot:** Copia inmutable de los montos financieros calculados en el servidor que evita alteraciones maliciosas en el cliente.
* **Modelo 30/70:** Esquema comercial donde el 30% del monto total retenido por la pasarela constituye el margen operativo para Fix&Go, y el 70% se transfiere al prestador.