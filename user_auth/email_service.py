"""
email_service.py
----------------
Single Responsibility: Handles outbound email delivery.

This module:
  - Connects to SMTP server
  - Sends password reset and verification emails
  - Abstracts email logic from router layer
"""

import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import random
import string
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def generate_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def send_email(to_email: str, code: str, type: int):
    """
    Sends an email depending on the type.

    type = 1 -> password reset
    type = 2 -> account verification
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
    """
    Generates the email message depending on the type.
    """

    msg = EmailMessage()

    # PASSWORD RESET
    if type == 1:

        msg["Subject"] = "Password Reset Code"

        msg.set_content(
f"""
Hello,

You requested to reset your password.

Your verification code is:

{code}

This code will expire in 10 minutes.

If you did not request this request, please ignore this email.

Regards,
Hospital Management System
"""
        )

    # ACCOUNT VERIFICATION
    elif type == 2:

        msg["Subject"] = "Account Verification Code"

        msg.set_content(
f"""
Hello,

Welcome to the Hospital Management System.

To complete your registration, please verify your email using the following code:

{code}

This code will expire in 10 minutes.

If you did not create this account, please ignore this email.

Regards,
Hospital Management System
"""
        )

    else:
        raise ValueError("Unexpected email type code")

    return msg