flowchart TD
    A[Request POST /staff] --> B[Validar datos con Pydantic]
    B --> C{Datos válidos?}
    C -- No --> D[Return 422]
    C -- Sí --> E[Insertar en BD]
    E --> F[Commit]
    F --> G[Return 201]