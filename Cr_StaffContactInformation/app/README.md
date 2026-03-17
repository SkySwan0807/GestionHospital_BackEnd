# Hospital Staff Management API
Backend service for managing hospital staff, departments, specialties, and vacation tracking.

The project is built using:

- FastAPI
- SQLAlchemy
- SQLite
- Pytest
- Uvicorn

## Important Note About Database Path
The project uses SQLite with a relative path. Because of this, the API and seed scripts must be executed from the same folder to ensure they use the same database file.

All backend commands should therefore be executed from:

```
Cr_StaffContactInformation
```

---


## Running the API
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

*Departments

*Specialties

*Users (with email)

*Staff members (linked to users)

*Vacation information

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
⚙️ Verificando/Creando tablas en la base de datos...
  ➕ Creado Usuario y Staff: Carlos Mendoza
  ➕ Creado Usuario y Staff: Laura Vargas (RRHH)
  ➕ Creado Usuario y Paciente: Juan Pérez
  ➕ Creadas vacaciones y citas de prueba
✅ ¡Datos de prueba insertados con la nueva arquitectura!
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
9 passed in 14.93s
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
user_id
first_name	
last_name	
phone_number
start_date
status
role_level
department_id
specialty_id
profile_pic
vacation_details
created_at
email	    
Note: The email field is not stored in the staff table. It is retrieved from 
the related users table via the user_id relationship. This ensures email 
consistency and avoids duplication.
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
*assigned: Total vacation days assigned per year

*used: Vacation days already taken

*available: Remaining vacation days
---

# Main Features

The API currently supports:

*Create staff members (requires an existing user_id)

*Get staff by ID (includes email from the related user)

*Update staff information (editable fields: first_name, last_name, phone_number, status, role_level, profile_pic)

```
Endpoints Overview
Method	Endpoint	            Description
POST	/api/staff/	            Create a new staff record
GET	    /api/staff/{staff_id}	Retrieve staff details by ID
PATCH	/api/staff/{staff_id}	Update editable staff fields
```
---