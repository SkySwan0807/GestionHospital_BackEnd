graph TD
    ENV[".env"] --> DB["app/database.py"]
    DB --> MODELS["app/models.py"]
    DB --> ROUTER["app/routers/specialties.py"]
    DB --> MAIN["app/main.py"]
    MODELS --> CRUD["app/crud.py"]
    SCHEMAS["app/schemas.py"] --> CRUD
    SCHEMAS --> ROUTER
    CRUD --> ROUTER
    ROUTER --> MAIN
    MAIN --> TESTS["tests/test_specialties.py"]
    DB --> TESTS
    INIT_APP["app/__init__.py"] -.->|package marker| MAIN
    INIT_APP -.->|package marker| MODELS
    INIT_APP -.->|package marker| SCHEMAS
    INIT_APP -.->|package marker| CRUD
    INIT_APP -.->|package marker| ROUTER
    INIT_ROUTERS["app/routers/__init__.py"] -.->|package marker| ROUTER
    INIT_TESTS["tests/__init__.py"] -.->|package marker| TESTS
    REQ["requirements.txt"] -.->|installed into env| MAIN
    GITIGNORE[".gitignore"] -.->|read by git| ENV
    README["README.md"] -.->|documentation| MAIN

    style ENV fill:#f9f,stroke:#333
    style GITIGNORE fill:#ddd,stroke:#333
    style README fill:#ddd,stroke:#333
    style REQ fill:#ddd,stroke:#333
    style INIT_APP fill:#eee,stroke:#999,stroke-dasharray: 5 5
    style INIT_ROUTERS fill:#eee,stroke:#999,stroke-dasharray: 5 5
    style INIT_TESTS fill:#eee,stroke:#999,stroke-dasharray: 5 5