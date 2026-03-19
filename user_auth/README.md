# Backend Authentication Service

This project provides a backend authentication service built with **FastAPI**.  
It includes login validation, password reset functionality, and email-based verification codes.

---

## Environment Configuration

In the root directory of your project, create a file named `.env` and add the following environment variables:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=hospitalesbackend@gmail.com

EMAIL_PASSWORD=ksqx upej cqfu ksjl
EMAIL_FROM=hospitalesbackend@gmail.com
```


These variables are required for the email service used to send password reset and verification codes.

---

## Testing Email Functionality

For testing purposes:

1. Add a new user to the database **or**
2. Modify an existing user and assign a **valid email address**.

This is necessary for testing because the system will send a **verification code or password reset code** to the provided email.

---

## Running the Project

To run the FastAPI application, execute the following command:


python -m uvicorn user_auth.main:app --reload


The API will start locally and can be accessed at:


http://127.0.0.1:8000/docs


---

## Login Endpoint

The system provides an endpoint to validate user credentials.

### Endpoint


GET /login


### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| email | string | User email |
| password | string | User password |

### Example Request


GET /login?email=user@email.com
&password=yourpassword


### Example Response (Success)

```json
{
  "success": true,
  "message": "Login successful",
  "role": "patient"
}
```

Example Response (Invalid Credentials)

```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

Implementation

```
@router.get("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    """
    Validates user credentials.

    Returns:
        - success: True if credentials are valid
        - success: False otherwise
    """

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"success": False, "message": "Invalid credentials"}

    if not verify_password(password, user.password):
        return {"success": False, "message": "Invalid credentials"}

    return {
        "success": True,
        "message": "Login successful",
        "role": user.role
    }
```


Notes

Passwords are stored hashed for security.

Email functionality is required to test:

Password reset

Account verification

Ensure the .env file exists before running the project.