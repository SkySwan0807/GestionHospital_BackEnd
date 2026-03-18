# Hospital Staff Management API

## 1. Descripcion
Esta es una API RESTful desarrollada con FastAPI, disenada para gestionar de manera eficiente las operaciones centrales de un hospital. El sistema administra la informacion del personal medico y administrativo (Staff), el registro de pacientes, la organizacion por departamentos y especialidades medicas, y un modulo completo para la solicitud y aprobacion de vacaciones. El proyecto esta estructurado para ser facilmente desplegable y cuenta con un entorno preconfigurado ideal para pruebas de Aseguramiento de Calidad (QA).

## 2. Tecnologias Utilizadas
* Python 3.10+
* FastAPI (Framework web de alto rendimiento)
* Uvicorn (Servidor ASGI)
* SQLAlchemy (ORM para la gestion de la base de datos)
* pytest (Para pruebas automatizadas)

## 3. Requisitos
Antes de ejecutar el proyecto, asegurate de tener instalado en tu computadora:
* Python 3.10 o superior.
* pip (Gestor de paquetes de Python).
* Virtualenv (Recomendado para no afectar otras instalaciones de tu sistema).

Nota: Aunque el sistema es compatible con bases de datos robustas como PostgreSQL o MySQL, el repositorio ya incluye una base de datos local SQLite (`hospital.db`) lista para usar, por lo que no requieres instalar motores de bases de datos adicionales para probar el proyecto.

## 4. Instalacion

Sigue estos pasos en tu terminal o linea de comandos:

Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd GestionHospital_BackEnd
```

Crear el entorno virtual:
```bash
python -m venv venv
```

Activar el entorno virtual:
En Windows:
```bash
venv\Scripts\activate
```
En Linux/Mac:
```bash
source venv/bin/activate
```

Instalar las dependencias del proyecto:
```bash
pip install -r requirements.txt
```

## 5. Sobre la base de datos
El sistema utiliza una arquitectura de persistencia de datos relacional. Para facilitar el trabajo del equipo de desarrollo y QA, el repositorio incluye un archivo llamado `hospital.db`. Esta base de datos SQLite ya se encuentra pre-poblada con catalogos iniciales (departamentos, especialidades) y usuarios de prueba. 

Esto significa que, una vez clonado el repositorio, el proyecto es "Plug and Play": no necesitas ejecutar scripts de migracion ni crear datos manualmente para comenzar a realizar pruebas funcionales o de integracion.

## 6. Modelos de Datos Principales
La arquitectura de la base de datos se divide en los siguientes modelos centrales:
* Users: Maneja las credenciales de acceso (email y contrasena encriptada) y los roles del sistema.
* Staff: Almacena la informacion operativa, de contacto y profesional de los empleados del hospital.
* Patients: Gestiona los datos personales y de contacto de los pacientes.
* Departments y Specialties: Actuan como catalogos para organizar la estructura medica del recinto.
* Vacations: Registra el historial y el estado (pendiente, aceptado, rechazado) de las solicitudes de tiempo libre.

## 7. Como ejecutar la aplicacion
Con tu entorno virtual activado, ejecuta el siguiente comando en la raiz del proyecto para encender el servidor:

```bash
uvicorn app.main:app --reload
```

Una vez que la consola indique que la aplicacion ha iniciado, abre tu navegador web y visita:
`http://localhost:8000/docs`

Alli encontraras la interfaz interactiva de Swagger UI. Desde esta pagina, cualquier persona, tenga o no conocimientos profundos de programacion, puede visualizar, entender y probar todos los endpoints del sistema.

## 8. Logica de autenticacion y payloads

El sistema protege sus rutas operativas exigiendo que el usuario inicie sesion. Todo el flujo de acceso, registro de nuevos pacientes y recuperacion de contrasenas esta disenado con un sistema de verificacion por pasos (OTP o codigos de verificacion).

Para que el equipo de QA pueda realizar pruebas funcionales de inicio de sesion sin necesidad de registrar nuevos usuarios, se han habilitado las siguientes credenciales precargadas:

Cuentas de Doctor (Rol: Staff):
* Usuario: dra.suzeth@hospital.com | Contrasena: 123456
* Usuario: dr.perez@hospital.com | Contrasena: 123456

Cuentas de Paciente (Rol: Patient):
* Usuario: oscar.vargas@gmail.com | Contrasena: 123456
* Usuario: carlos.mendoza@gmail.com | Contrasena: 123456

### 8.1. Endpoints de Acceso y Onboarding

#### GET /login
Endpoint para iniciar sesion. Recibe los datos mediante parametros de consulta (query params).

Request (Query params):
`/login?email=user@email.com&password=userpassword`

Response Body (Exito):
```json
{
  "success": true,
  "message": "Login successful",
  "role": "patient"
}
```

Response Body (Error):
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

#### POST /register
Inicia el flujo de registro para un nuevo paciente solicitando el envio de un codigo de verificacion a su correo.

Request Body:
```json
{
  "email": "user@email.com"
}
```

#### POST /verify
Verifica el codigo enviado al usuario y responde dinamicamente indicando el siguiente paso (`next_step`).

Request Body:
```json
{
  "email": "user@email.com",
  "code": "123456"
}
```

#### POST /register_user
Paso final del registro. Se envian los datos personales del paciente para crear su perfil en la base de datos.

Request Body:
```json
{
  "email": "user@email.com",
  "password": "SecurePassword123",
  "first_name": "Juan",
  "last_name": "Perez",
  "date_of_birth": "1995-01-01",
  "contact_number": "77777777"
}
```

#### POST /forgot_password y POST /reset_password
Flujo de recuperacion de credenciales. El primero envia el codigo y el segundo actualiza la contrasena tras la verificacion.

Request Body (Reset Password):
```json
{
  "email": "user@email.com",
  "new_password": "NewPassword123"
}
```

## 9. Informacion de contacto del Personal (Staff)

### 9.1. Como funciona
El modulo Staff gestiona a los empleados del hospital y su informacion profesional. Cada miembro del personal esta vinculado a una cuenta de usuario (almacenada en la tabla `users`) a traves de un campo `user_id`. 

Esto significa que, cuando creas un registro de personal, debes proporcionar un `user_id` existente. El sistema asociara automaticamente el correo electronico de ese usuario con el perfil del personal. Como regla estricta de diseno y seguridad, el correo electronico nunca se almacena directamente en la tabla staff; siempre se recupera del usuario relacionado para evitar duplicidades.

Actualmente, cualquier usuario autenticado puede acceder a los endpoints del personal para crear, ver o actualizar la informacion. Sin embargo, existen validaciones estrictas de proteccion de datos: por ejemplo, no es posible modificar ni transferir el `user_id` de un miembro del personal que ya ha sido registrado.

## 10. Referencia de Endpoints y Payloads

### 10.1. Gestion de Personal (Staff)

#### POST /api/staff
Registra a un nuevo empleado en el sistema.

Request Body:
```json
{
  "user_id": 3,
  "first_name": "string",
  "last_name": "string",
  "phone_number": "string",
  "start_date": "2026-03-12",
  "status": "string",
  "role_level": "string",
  "department_id": 0,
  "specialty_id": 0,
  "profile_pic": "string",
  "vacation_details": {}
}
```

#### GET /api/staff/{staff_id}
Obtiene el perfil detallado de un empleado especifico.

Response Body (Exito):
```json
{
  "id": 3,
  "user_id": 3,
  "first_name": "Juan",
  "last_name": "Perez",
  "email": "juanperez@mail.com",
  "phone_number": "strings",
  "start_date": "2026-03-12",
  "status": "string",
  "role_level": "string",
  "department_id": 0,
  "specialty_id": 0,
  "profile_pic": "string",
  "vacation_details": {},
  "created_at": "2026-03-12T01:32:05"
}
```

#### PUT /api/staff/{staff_id}
Actualiza campos especificos del perfil de un empleado.

Request Body (Ejemplo de actualizacion parcial):
```json
{
  "first_name": "Juan",
  "last_name": "Perez",
  "phone_number": "strings",
  "status": "string",
  "role_level": "string",
  "profile_pic": "string" 
}
```

### 10.2. Gestion de Vacaciones

#### POST /myprofile/requestvacation
Endpoint utilizado por el personal (Staff) para solicitar dias de vacaciones.

Request Body:
```json
{
  "start_date": "2026-03-11",
  "end_date": "2026-04-01",
  "comment": "string"
}
```

Response Body:
```json
{
  "start_date": "2026-03-11",
  "end_date": "2026-04-01",
  "comment": "string",
  "reason": "string",
  "id": 0,
  "staff_id": 0,
  "requestDate": "2026-03-01",
  "status": "pending"
}
```

### 10.3. Respuestas de Error (Error Responses)
Tabla de referencia para validaciones de QA:

| Metodo | Endpoint | Descripcion del Error (Mensaje) | Codigo |
| :--- | :--- | :--- | :--- |
| GET | `/human-resources/vacation-managment` | There is no existence database | 404 |
| GET | `/human-resources/vacation-managment/{request_id}` | requested id does not exist | 404 |
| PATCH | `/human-resources/vacation-managment/{request_id}` | Vacation request status can only be "accepted" or "rejected" | 402 |

## 11. The Complete project structure (Estructura del Proyecto)
El proyecto sigue una arquitectura limpia orientada a micro-modulos, separando claramente la logica global de los modulos independientes. 

Nota: Directorios de entorno local (`.venv`), configuraciones de IDE (`.idea`) y cachés (`__pycache__`) estan ignorados en el control de versiones y excluidos de este diagrama por claridad.

```text
GestionHospital_BackEnd/
├── app/                               # Nucleo principal de la API
│   ├── routers/                       # Enrutadores principales
│   │   ├── specialties.py
│   │   └── staff.py
│   ├── main.py                        # Punto de entrada de FastAPI
│   ├── database.py                    # Configuracion de conexion DB
│   ├── models.py                      # Modelos SQLAlchemy (Tablas)
│   ├── schemas.py                     # Modelos Pydantic (Validacion)
│   └── crud.py                        # Logica de base de datos
├── Cr_StaffContactInformation/        # Modulo de gestion de Personal
│   ├── app/                           # Logica especifica del modulo
│   └── tests/                         # Pruebas aisladas del modulo
├── Diagrams/                          # Documentacion visual de arquitectura
├── tests/                             # Pruebas automatizadas globales (QA)
│   ├── test_specialties.py
│   └── test_staff.py
├── .gitignore                         # Reglas de exclusion de Git
├── requirements.txt                   # Dependencias del proyecto
└── hospital.db                        # Base de datos local pre-poblada
```

## 12. Environment variables (Variables de Entorno)
El sistema utiliza el paquete `python-dotenv` para cargar la configuracion desde un archivo `.env` en la raiz. 

* `DATABASE_URL`: Define la cadena de conexion a la base de datos.
  * Comportamiento por defecto: Si no se define, el sistema utilizara automaticamente la base de datos local SQLite: `sqlite:///./hospital.db`.

## 13. Test cases (Casos de Prueba)
El proyecto incluye una suite de pruebas de integracion desarrolladas con `pytest` y `TestClient`. Utilizan una base de datos en memoria separada para no afectar datos de QA.

Casos principales cubiertos:
* Modulo de Especialidades: Creacion exitosa, rechazo por nombre duplicado (Status 409), validacion de campos (Status 422), y busquedas (Status 200 y 404).
* Modulo de Personal: Verificacion de llaves foraneas (Status 201), actualizacion exitosa (Status 200), bloqueo por correo duplicado (Status 400), y bloqueo al modificar campos protegidos (Status 422).
