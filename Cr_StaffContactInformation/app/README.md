# Hospital Staff Management API

Backend service for managing hospital staff, departments, specialties, and vacation tracking.

The project is built using:

* FastAPI
* SQLAlchemy
* SQLite
* Pytest
* Uvicorn

---

# Important Note About Database Path

The project uses **SQLite with a relative path**.
Because of this, the API and seed scripts **must be executed from the same folder** to ensure they use the same database file.

All backend commands should therefore be executed from:

```
Cr_StaffContactInformation
```

---


# Running the API

Move to the backend module folder:

```
cd Cr_StaffContactInformation
```

Start the FastAPI server:

```
uvicorn app.main:app --reload
```

You should see:

```
Uvicorn running on http://127.0.0.1:8000
```

---

# API Documentation (Swagger)

When the server is running, open:

```
http://127.0.0.1:8000/docs
```

This opens the Swagger UI where you can:

* View all endpoints
* Send requests
* Test the API interactively


---

# Seeding the Database

The project includes a **seed script** that inserts sample data such as:

* Departments
* Specialties
* Staff members
* Vacation information

From inside the backend folder:

```
cd Cr_StaffContactInformation
```

Run:

```
python -m app.seed
```

Example output:

```
🌱 Iniciando la siembra de datos...

➕ Creando departamento: Urgencias
➕ Creando especialidad: Cardiología
➕ Creando empleado: Carlos Mendoza

✅ ¡Datos de prueba verificados/insertados con éxito!
```

The seed script checks if data already exists and prevents duplicates.

---

# Running Tests

Tests are implemented using **pytest**.

Location:

```
Cr_StaffContactInformation/tests
```

Run tests from the **project root**:

```
pytest Cr_StaffContactInformation
```

Example result:

```
7 passed in 2.3s
```

The tests automatically:

* Reset the database
* Create fresh tables
* Insert test data
* Remove tables after execution

This ensures each test run starts with a **clean database**.

---

# Staff Data Model

The API manages the following fields for staff members:

```
id
first_name
last_name
email
phone_number
start_date
status
role_level
department_id
specialty_id
profile_pic
vacation_details
created_at
```

---

# Vacation Details Format

Each staff member contains a JSON field for vacation tracking.

Example:

```
{
  "assigned": 15,
  "used": 5,
  "available": 10
}
```

---

# Main Features

The API currently supports:

* Create staff members
* Get staff by ID
* Update staff information

---