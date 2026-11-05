# Diagrama UML de clases — FIX&GO

El diagrama representa las entidades persistentes principales. Django agrega claves técnicas y metadatos internos que se consultan en las migraciones.

```mermaid
classDiagram
    class User {
      +id: integer
      +email: string
      +role: CLIENT|PROVIDER
      +is_active: boolean
      +phone: string
      +default_address: string
    }
    class ProviderProfile {
      +display_name: string
      +description: text
      +years_experience: integer
      +latitude: decimal
      +longitude: decimal
      +map_visible: boolean
    }
    class Category { +name: string +slug: string }
    class Commune { +name: string +slug: string }
    class ServiceRequest {
      +status: PENDING|QUOTED|ACCEPTED|IN_PROGRESS|COMPLETED|CANCELLED
      +description: text
      +address: string
      +preferred_date: date
      +latitude: decimal
      +longitude: decimal
    }
    class Quote {
      +description: text
      +price: integer CLP
      +status: SUBMITTED|ACCEPTED|REJECTED|WITHDRAWN
    }
    class MaterialExtra {
      +description: string
      +quantity: integer
      +unit_price: integer CLP
      +status: PENDING|APPROVED|REJECTED
    }
    class PaymentOrder {
      +mode: DEMO|WEBPAY_INT
      +status: PENDING|FAILED|DEMO_PAID|DEMO_REFUNDED
      +service_amount: integer
      +materials_amount: integer
      +total: integer
      +snapshot: JSON
    }
    class WebpayAttempt {
      +buy_order: string
      +token: string
      +finished: boolean
    }
    class ServiceMessage { +text: string +created_at: datetime }
    class WorkEvidence { +photo: file +caption: string }
    class Rating { +score: 1..5 +comment: text }
    class ServiceDispute { +reason: text +status: OPEN|REJECTED|REFUNDED }
    class ProviderWarning { +created_at: datetime }

    User "1" *-- "0..1" ProviderProfile : amplía
    ProviderProfile "*" -- "*" Category : ofrece
    ProviderProfile "*" -- "*" Commune : atiende
    User "1" --> "*" ServiceRequest : cliente
    User "1" --> "*" ServiceRequest : prestador
    Category "1" --> "*" ServiceRequest
    Commune "1" --> "*" ServiceRequest
    ServiceRequest "1" *-- "*" Quote
    ServiceRequest "1" *-- "*" MaterialExtra
    ServiceRequest "1" *-- "0..1" PaymentOrder
    PaymentOrder "1" *-- "*" WebpayAttempt
    ServiceRequest "1" *-- "*" ServiceMessage
    User "1" --> "*" ServiceMessage : envía
    ServiceRequest "1" *-- "*" WorkEvidence
    User "1" --> "*" WorkEvidence : carga
    ServiceRequest "1" *-- "0..1" Rating
    ServiceRequest "1" *-- "0..1" ServiceDispute
    ServiceDispute "1" *-- "0..1" ProviderWarning
    User "1" --> "*" ProviderWarning : recibe
```

## Reglas estructurales relevantes

- Cada solicitud tiene como máximo una `PaymentOrder` y una `Rating`.
- Cada reclamo genera como máximo una `ProviderWarning`; repetir una resolución no duplica la alerta.
- Una orden conserva un snapshot para que el total histórico no cambie si luego se modifica un catálogo.
- Las relaciones con pagos, mensajes, evidencias y reclamos usan protección de historial; no se eliminan en cascada como solución operativa.
- El token Webpay es una capacidad de integración y se protege de registros; no representa ni contiene datos de tarjeta.

Fuente ejecutable del modelo: modelos y migraciones del directorio [`FIX_AND_GO_SOFTWARE/backend`](../FIX_AND_GO_SOFTWARE/backend/).
