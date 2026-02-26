sequenceDiagram
    participant Client
    participant FastAPI
    participant Service
    participant Database

    Client->>FastAPI: POST /api/staff/
    FastAPI->>Service: Validar datos (Pydantic)
    Service->>Database: Insert Staff
    Database-->>Service: Staff creado (id)
    Service-->>FastAPI: StaffResponse
    FastAPI-->>Client: 201 Created