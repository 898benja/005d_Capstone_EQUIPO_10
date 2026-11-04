# Duoc UC

**ESCUELA DE INFORMÁTICA Y TELECOMUNICACIONES**

# Fix&Go

**"Problema, usuarios, propuesta de valor"**

* **Asignatura:** Capstone (`APT122`)

* **Sección:** 005-D

* **Profesor:** José Luis Pino

* **Integrantes:** Felipe Arce, Daniel Baeza y Benjamín Olmedo

* **Sede:** Duoc UC Plaza Oeste

## Índice de Contenidos

1. **Introducción y contexto** ..................................................................................... Pág. 3

2. **Definición del problema** .................................................................................... Pág. 4

3. **Usuarios y beneficiarios** .................................................................................... Pág. 5

4. **Propuesta de valor y declaración de visión** ....................................................... Pág. 6

   * Propuesta de Valor

   * Declaración de Visión del Producto (*Product Vision Statement*)

5. **Alcance y diferenciadores del MVP** .................................................................. Pág. 7

## 1. Introducción y contexto

El mercado actual de servicios técnicos y reparaciones domiciliarias en Chile —particularmente en áreas críticas para la habitabilidad como **Agua/Gasfitería, Electricidad y Gas**— exige un estándar de confianza, transparencia tarifaria y trazabilidad operativa que los canales tradicionales e informales no logran satisfacer. En la cotidianidad de los hogares de la Región Metropolitana, los propietarios y residentes enfrentan la necesidad recurrente de resolver emergencias o mantenimientos técnicos sin contar con herramientas objetivas que respalden la idoneidad del especialista, la justicia del precio cobrado ni el cumplimiento efectivo del trabajo.

Este proyecto se enfoca en el diseño, desarrollo y validación del Producto Mínimo Viable (MVP) de **Fix&Go**, una plataforma digital multiplataforma (desarrollada en **React Native con Expo** y respaldada por una API transaccional en **Django REST Framework**). Su propósito central es proveer un ecosistema tecnológico estructurado que conecte a clientes residenciales con prestadores de servicios técnicos, transformando la contratación informal y fragmentada en un recorrido digital trazable de extremo a extremo, con cotizaciones vinculantes, control estricto de materiales adicionales y liquidación financiera blindada contra manipulaciones.

## 2. DEFINICIÓN DEL PROBLEMA

La contratación y ejecución de servicios técnicos para el hogar en el mercado tradicional se ve severamente afectada por tres factores críticos que perjudican tanto a los clientes como a los especialistas calificados:

* **Informalidad tarifaria y asimetría en el cobro de materiales adicionales:** En el modelo tradicional (recomendaciones de boca en boca, redes sociales o directorios sin control), los presupuestos suelen acordarse verbalmente sin respaldo técnico. Durante la ejecución del trabajo en terreno, es frecuente que surjan cobros sorpresivos por repuestos o insumos adicionales que el cliente no puede verificar ni aprobar formalmente antes del cierre, generando disputas sobre el monto final a pagar y desconfianza hacia el técnico.

* **Falta de trazabilidad, seguridad y riesgo de desintermediación (fuga):** La ausencia de un flujo estructurado de estados impide distinguir con certeza cuándo una solicitud fue solo consultada, cuándo cuenta con una cotización firme, cuándo está en ejecución real y cuándo ha finalizado. Asimismo, las plataformas de clasificados convencionales exponen prematuramente los datos de contacto personales (teléfonos y direcciones exactas), facilitando que las partes cierren tratos por fuera del sistema sin garantías de seguridad, sin registro de incidencias y sin respaldo ante trabajos inconclusos.

* **Incertidumbre comercial para el prestador y ausencia de incentivos de retención:** Los técnicos independientes y especialistas certificados enfrentan alta variabilidad en sus ingresos semanales y falta de estímulos para mantener un alto volumen de servicios completados dentro de la plataforma. Adicionalmente, carecen de un historial digital inmutable que respalde su reputación y permita premiar su constancia operativa.

## 3. USUARIOS Y BENEFICIARIOS

Para comprender el impacto integral de la solución **Fix&Go**, se diferencian los actores directos e indirectos que interactúan dentro del ecosistema:

### Usuario Primario A: Cliente Residencial (Solicitante del Servicio)

* **Rol y uso:** Es el actor que inicia el flujo operativo dentro de la aplicación móvil. Utiliza el sistema para explorar el catálogo filtrando por especialidad (**Agua/Gasfitería, Electricidad, Gas**) y comuna de cobertura (ej. Pudahuel, Cerrillos, Maipú, Estación Central, Santiago, Lo Espejo), crear solicitudes detallando la falla domiciliaria, evaluar y aceptar cotizaciones de manera atómica, aprobar o rechazar cada material extra propuesto en terreno, ejecutar el cierre de pago (demostración académica) y calificar el desempeño del especialista en una escala de $1$ a $5$.

* **Necesidad:** Encontrar especialistas confiables con cobertura real en su comuna, contar con certeza absoluta del monto final a pagar sin cobros ocultos y mantener el control sobre cualquier gasto adicional en repuestos antes de proceder a la liquidación.

### Usuario Primario B: Prestador de Servicios Técnicos (Especialista)

* **Rol y uso:** Es el profesional o técnico que configura su perfil (`ProviderProfile`) declarando sus años de experiencia, certificaciones (ej. SEC clase B), categorías de especialidad y comunas de atención. A través de su interfaz dedicada ("Tu trabajo, al día"), recibe solicitudes compatibles, emite cotizaciones en pesos chilenos ($\text{CLP}$) con notas técnicas, gestiona el inicio (`IN_PROGRESS`) y término (`COMPLETED`) de la obra, y registra propuestas de materiales adicionales (`MaterialExtra`).

* **Necesidad:** Recibir requerimientos filtrados y pertinentes a su zona geográfica y rubro, asegurar que el cliente acepte formalmente su tarifa y los insumos extras, y acceder a **bonos de incentivo por rendimiento semanal** basados en la cantidad y calidad de servicios completados en la plataforma.

### Beneficiario / Rol de Administración y Plataforma (Gobernanza Fix&Go)

* **Rol y uso:** Representado por la lógica central del servidor y la gestión operativa. Administra la integridad transaccional de las órdenes de pago (`PaymentOrder`) y calcula la comisión del **30% sobre el valor del servicio**. El prestador recibe el 70% del servicio más el 100% de los materiales aprobados. Los montos del MVP son demostrativos y no constituyen liquidaciones reales.

* **Beneficio:** Garantiza la viabilidad económica y comercial del servicio, incentiva la productividad de los prestadores mediante estímulos económicos y previene la fuga de usuarios reteniendo la apertura del canal de comunicación directa (`ServiceMessage`) hasta la confirmación del pago.

## 4. PROPUESTA DE VALOR Y DECLARACIÓN DE VISIÓN

### Propuesta de Valor

**Fix&Go** estructura la contratación de reparaciones del hogar mediante búsqueda geográfica, cotización, aprobación de materiales, pago de prueba, comunicación protegida y evidencia del trabajo. El backend conserva el estado del servicio y calcula los montos; la aplicación presenta a cada rol las acciones que corresponden. La comisión del 30% se aplica únicamente al valor del servicio y los materiales se asignan íntegramente al prestador.

### Declaración de Visión del Producto (*Product Vision Statement*)

> **Para** los propietarios y residentes de hogares, así como para los especialistas técnicos de gasfitería, electricidad y gas,
> **que enfrentan** la informalidad tarifaria, la desconfianza operativa, los cobros imprevistos de materiales en terreno y la falta de incentivos estables en las reparaciones domiciliarias,
> **Fix&Go** es una plataforma móvil e infraestructura transaccional de servicios para el hogar
> **que** estructura el ciclo desde la búsqueda y cotización hasta la aprobación de materiales, pago de prueba, chat protegido, evidencia y valoración,
> **a diferencia de** los directorios informales, redes sociales o acuerdos verbales desconectados donde no existe control de estados, protección contra la desintermediación ni estímulos económicos para los trabajadores,
> **nuestro producto** aplica reglas de transición y cálculos en el servidor, conserva evidencia del recorrido y reduce los acuerdos informales que no quedan registrados.

## 5. ALCANCE Y DIFERENCIADORES DEL MVP

Para la presente etapa del proyecto Capstone en Duoc UC, el alcance funcional y técnico del Producto Mínimo Viable (MVP) se concentra rigurosamente en los siguientes cuatro pilares estratégicos y diferenciadores:

1. **Máquina de Estados Transaccional y Aceptación Atómica:**
   Gestión estricta del ciclo de vida de la solicitud (`PENDING` $\rightarrow$ `QUOTED` $\rightarrow$ `ACCEPTED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `COMPLETED`). El sistema implementa bloques `transaction.atomic` y actualizaciones condicionadas en base de datos para que la aceptación de una cotización sea indivisible, devolviendo un código de conflicto `HTTP 409` ante condiciones de carrera sin duplicar efectos.

2. **Gestión Transparente de Materiales Adicionales y Bloqueo Preventivo de Checkout:**
   Capacidad del prestador para declarar insumos extras requeridos durante la intervención técnica (`MaterialExtra`). La API bloquea cualquier intento de pasar al pago final (*checkout*) mientras existan materiales en estado pendiente de decisión, exigiendo que el cliente apruebe o rechace explícitamente cada ítem antes de consolidar el cobro.

3. **Liquidación Financiera Inmutable en Servidor y Comisión de Servicio:**
   Django suma el valor del servicio y los materiales aprobados y conserva un *snapshot* en `PaymentOrder`. La comisión de Fix&Go equivale al 30% del servicio; el prestador recibe el 70% del servicio más la totalidad de los materiales. El cierre utiliza Webpay en ambiente de integración o una simulación controlada y genera un comprobante académico sin validez tributaria.

4. **Seguridad en Tres Capas y Control Anti-Fuga:**
   Protección integral compuesta por: (1) autenticación mediante tokens con expiración de $24\text{ horas}$ y aislamiento por propiedad donde terceros no autorizados reciben `HTTP 404`; (2) validaciones de reglas de negocio y cobertura en la API REST; y (3) restricciones de unicidad e integridad referencial en la base de datos SQLite. Adicionalmente, los teléfonos permanecen ocultos en el catálogo público y el chat interno (`ServiceMessage`) se habilita exclusivamente tras aprobar el pago de demostración.
