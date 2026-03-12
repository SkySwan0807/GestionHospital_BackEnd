Manual de Usuario – Sistema de Autenticación
1. Introducción

Este sistema permite a los usuarios:

Iniciar sesión

Recuperar su contraseña si la olvidan

Crear una nueva cuenta

Para algunas acciones el sistema enviará un código de verificación al correo electrónico del usuario.

2. Iniciar Sesión

Permite acceder al sistema usando el correo y la contraseña.

Endpoint
GET /login
Ejemplo
/login?email=usuario@email.com&password=123456
Respuesta si es correcto
{
  "success": true,
  "message": "Login successful",
  "role": "patient"
}
Respuesta si es incorrecto
{
  "success": false,
  "message": "Invalid credentials"
}
3. Recuperar Contraseña

Si el usuario olvidó su contraseña puede solicitar un código de verificación por correo.

Paso 1: Solicitar código
Endpoint
POST /forgot_password
Datos que se envían
{
  "email": "usuario@email.com"
}

El sistema hará lo siguiente:

Verifica que el correo exista.

Genera un código de verificación.

Envía el código al correo.

El código dura 10 minutos.

Paso 2: Verificar el código
Endpoint
POST /verify
Datos que se envían
{
  "email": "usuario@email.com",
  "code": "123456"
}

El sistema verifica que:

El correo sea correcto

El código sea correcto

El código no haya sido usado

El código no haya expirado

Paso 3: Cambiar contraseña
Endpoint
POST /reset_password
Datos que se envían
{
  "email": "usuario@email.com",
  "new_password": "NuevaContraseña123"
}

Respuesta:

{
  "message": "Password updated successfully"
}
4. Crear un Nuevo Usuario

Para crear una cuenta nueva también se utiliza un código de verificación por correo.

Paso 1: Solicitar código
Endpoint
POST /register
Datos que se envían
{
  "email": "usuario@email.com"
}

El sistema:

Verifica que el correo no esté registrado.

Genera un código.

Envía el código al correo.

Paso 2: Verificar código
Endpoint
POST /verify
Datos que se envían
{
  "email": "usuario@email.com",
  "code": "123456"
}
Paso 3: Completar registro
Endpoint
POST /register_user
Datos que se envían
{
  "email": "usuario@email.com",
  "password": "ContraseñaSegura123",
  "first_name": "Juan",
  "last_name": "Perez",
  "date_of_birth": "1995-01-01",
  "contact_number": "77777777"
}

Respuesta:

{
  "message": "User registered successfully"
}