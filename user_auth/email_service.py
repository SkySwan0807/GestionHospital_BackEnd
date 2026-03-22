"""
email_service.py
----------------
Single Responsibility: Handles outbound email delivery.

This module:
  - Connects to SMTP server using environment variables
  - Sends password reset (type=1) and account verification (type=2) emails
  - Abstracts all email logic away from the router layer

Required .env variables:
  EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM
"""

import os
import smtplib
import random
import string
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")


def generate_code(length: int = 6) -> str:
    """Generates a random numeric verification code."""
    return ''.join(random.choices(string.digits, k=length))


def send_email(to_email: str, code: str, type: int):
    """
    Sends a verification email to the given address.
    type=1 → password reset
    type=2 → account verification
    """
    if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM]):
        raise RuntimeError("Email configuration is missing in environment variables.")

    msg = get_email_msg(type, code)
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        raise RuntimeError("SMTP Authentication failed. Check email credentials.")
    except smtplib.SMTPException as e:
        raise RuntimeError(f"SMTP error occurred: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error sending email: {str(e)}")


def get_email_msg(type: int, code: str) -> EmailMessage:
    """Builds the EmailMessage object based on the verification type."""
    msg = EmailMessage()

    if type == 1:
        msg["Subject"] = "Password Reset Code"
        msg.set_content(
            f"""Hello,

You requested to reset your password.
Your verification code is: {code}

This code will expire in 10 minutes.
If you did not request this, please ignore this email.

Regards,
Hospital Management System"""
        )
    elif type == 2:
        msg["Subject"] = "Account Verification Code"
        msg.set_content(
            f"""Hello,

Welcome to the Hospital Management System.
To complete your registration, verify your email using this code: {code}

This code will expire in 10 minutes.
If you did not create this account, please ignore this email.

Regards,
Hospital Management System"""
        )
    else:
        raise ValueError("Unexpected email type code")

    return msg
