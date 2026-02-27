sequenceDiagram
    participant Client as Frontend / Client
    participant Router as FastAPI Router (staff.py)
    participant Schema as Pydantic Schema
    participant CRUD as CRUD Layer (crud.py)
    participant DB as SQLite Database

    Client->>Router: PATCH /api/v1/staff/{id}/position
    Note over Client,Router: Body: {department_id, role_level, specialty_id}
    
    Router->>Schema: Validate incoming JSON
    alt Data is invalid
        Schema-->>Router: Validation Error
        Router-->>Client: 422 Unprocessable Entity
    else Data is valid
        Schema-->>Router: Validated StaffPositionUpdate Object
        Router->>CRUD: Call assign_staff_position(id, data)
        
        CRUD->>DB: Query Staff by ID
        DB-->>CRUD: Staff Object OR None
        
        alt Staff not found
            CRUD-->>Router: Return None
            Router-->>Client: 404 Not Found (Employee doesn't exist)
        else Staff found
            CRUD->>DB: Query Department by ID
            DB-->>CRUD: Department Object OR None
            
            alt Department not found
                CRUD-->>Router: Raise ValueError
                Router-->>Client: 400 Bad Request (Department doesn't exist)
            else Department found
                opt specialty_id is provided
                    CRUD->>DB: Query Specialty by ID
                    DB-->>CRUD: Specialty Object OR None
                    alt Specialty not found
                        CRUD-->>Router: Raise ValueError
                        Router-->>Client: 400 Bad Request (Specialty doesn't exist)
                    end
                end
                
                Note over CRUD,DB: All validations passed successfully
                CRUD->>CRUD: Update staff attributes
                CRUD->>DB: db.commit()
                CRUD->>DB: db.refresh()
                DB-->>CRUD: Updated Staff Object
                
                CRUD-->>Router: Return Updated Staff Object
                Router->>Schema: Serialize with StaffResponse
                Schema-->>Router: Valid JSON Output
                Router-->>Client: 200 OK + Updated Staff JSON
            end
        end
    end