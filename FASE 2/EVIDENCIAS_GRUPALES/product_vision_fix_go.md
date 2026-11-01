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

* **Rol y uso:** Representado por la lógica central del servidor y la gestión operativa del negocio. Administra la integridad transaccional de las órdenes de pago (`PaymentOrder`), el cálculo automatizado de impuestos y el modelo de sostenibilidad financiera, el cual contempla una retención integrada del **30% de margen de ganancia para la plataforma Fix&Go** (destinado a operación, escalamiento y financiamiento de bonos de incentivo) y la liquidación del **70% restante para el prestador**, además de la asignación automatizada de bonificaciones por trabajos semanales.

* **Beneficio:** Garantiza la viabilidad económica y comercial del servicio, incentiva la productividad de los prestadores mediante estímulos económicos y previene la fuga de usuarios reteniendo la apertura del canal de comunicación directa (`ServiceMessage`) hasta la confirmación del pago.

## 4. PROPUESTA DE VALOR Y DECLARACIÓN DE VISIÓN

### Propuesta de Valor

**Fix&Go** transforma la contratación de reparaciones y servicios para el hogar en una experiencia digital controlada, transparente y transaccionalmente segura. A través de una arquitectura centralizada de monolito modular, la plataforma unifica el recorrido entre el cliente y el prestador en cinco hitos verificables: solicitud geolocalizada por comuna, cotización formal, aceptación protegida contra condiciones de carrera, aprobación granular de materiales adicionales y liquidación final inmutable. Además, incorpora un modelo de retención sostenible del 30% complementado con un esquema de bonos por trabajos semanales que fideliza a los técnicos y asegura un alto estándar de servicio.

### Declaración de Visión del Producto (*Product Vision Statement*)

> **Para** los propietarios y residentes de hogares, así como para los especialistas técnicos de gasfitería, electricidad y gas,
> **que enfrentan** la informalidad tarifaria, la desconfianza operativa, los cobros imprevistos de materiales en terreno y la falta de incentivos estables en las reparaciones domiciliarias,
> **Fix&Go** es una plataforma móvil e infraestructura transaccional de servicios para el hogar
> **que** estructura y resguarda todo el ciclo de contratación —desde la búsqueda por comuna y la cotización formal, hasta la aprobación transparente de insumos extras, el cálculo inmutable de pago con margen institucional del 30% y un sistema de bonos por productividad semanal—,
> **a diferencia de** los directorios informales, redes sociales o acuerdos verbales desconectados donde no existe control de estados, protección contra la desintermediación ni estímulos económicos para los trabajadores,
> **nuestro producto** garantiza integridad absoluta en cada transición mediante operaciones atómicas en el servidor, congela el desglose financiero final sin posibilidad de manipulación y asegura un ecosistema comercial rentable, altamente motivador y libre de fricciones para ambas partes.

## 5. ALCANCE Y DIFERENCIADORES DEL MVP

Para la presente etapa del proyecto Capstone en Duoc UC, el alcance funcional y técnico del Producto Mínimo Viable (MVP) se concentra rigurosamente en los siguientes cuatro pilares estratégicos y diferenciadores:

1. **Máquina de Estados Transaccional y Aceptación Atómica:**
   Gestión estricta del ciclo de vida de la solicitud (`PENDING` $\rightarrow$ `QUOTED` $\rightarrow$ `ACCEPTED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `COMPLETED`). El sistema implementa bloques `transaction.atomic` y actualizaciones condicionadas en base de datos para que la aceptación de una cotización sea indivisible, devolviendo un código de conflicto `HTTP 409` ante condiciones de carrera sin duplicar efectos.

2. **Gestión Transparente de Materiales Adicionales y Bloqueo Preventivo de Checkout:**
   Capacidad del prestador para declarar insumos extras requeridos durante la intervención técnica (`MaterialExtra`). La API bloquea cualquier intento de pasar al pago final (*checkout*) mientras existan materiales en estado pendiente de decisión, exigiendo que el cliente apruebe o rechace explícitamente cada ítem antes de consolidar el cobro.

3. **Liquidación Financiera Inmutable en Servidor (*Snapshot*) y Modelo de Ganancia (30%):**
   Cálculo centralizado en el backend de Django que suma el valor del servicio aceptado más los materiales aprobados, congelando una copia inmutable (*snapshot*) en `PaymentOrder` que estructura el margen comercial del **30% para Fix&Go** (soporte operativo y fondo de bonos semanales) y el **70% para el prestador**. El cierre se ejecuta mediante una simulación controlada (`DEMO_PAID`) con comprobante académico sin validez tributaria.

4. **Seguridad en Tres Capas y Control Anti-Fuga:**
   Protección integral compuesta por: (1) autenticación mediante tokens con expiración de $24\text{ horas}$ y aislamiento por propiedad donde terceros no autorizados reciben `HTTP 404`; (2) validaciones de reglas de negocio y cobertura en la API REST; y (3) restricciones de unicidad e integridad referencial en la base de datos SQLite. Adicionalmente, los teléfonos permanecen ocultos en el catálogo público y el chat interno (`ServiceMessage`) se habilita exclusivamente tras aprobar el pago de demostración.