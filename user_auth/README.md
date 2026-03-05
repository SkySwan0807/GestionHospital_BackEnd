In de root directory of your project, create a file named .env and add the following environment variables:

EMAIL_HOST=smtp.gmail.com

EMAIL_PORT=587

EMAIL_USERNAME=hospitalesbackend@gmail.com

EMAIL_PASSWORD=ksqx upej cqfu ksjl

EMAIL_FROM=hospitalesbackend@gmail.com

For testing add a new user or modify one user and add a working email address.
this is necesary for testing and will be used to send the password reset email.

To run the project, use the following command:

python -m uvicorn user_auth.main:app --reload