sequenceDiagram
    actor User as Hospital System Consumer
    participant Router as FastAPI Router
    participant Service as Staff Service
    participant DB as Database (SQLAlchemy)

    User ->> Router: PATCH /api/staff/{id}
    Router ->> Service: update_staff(staff_id, staff_update)
    Service ->> DB: Query Staff by ID
    DB -->> Service: Staff object

    alt Staff not found
        Service -->> Router: 404 Not Found
    else Email duplicated
        Service ->> DB: Check email uniqueness
        DB -->> Service: Existing staff
        Service -->> Router: 400 Bad Request
    else Valid update
        Service ->> DB: Update fields
        Service ->> DB: Commit
        DB -->> Service: Updated staff
        Service -->> Router: 200 OK (StaffResponse)
    end