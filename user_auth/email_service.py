"""
email_service.py
----------------
Single Responsibility: Handles outbound email delivery.

This module:
  - Connects to SMTP server
  - Sends password reset emails
  - Abstracts email logic from router layer
"""

import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")


def send_reset_email(to_email: str, code: str):
    """
    Sends a password reset code to the user email.
    """

    if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM]):
        raise RuntimeError("Email configuration is missing in environment variables.")

    # Create email message
    msg = EmailMessage()
    msg["Subject"] = "Password Reset Code"
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    msg.set_content(
        f"""
Hello,

You requested to reset your password.

Your verification code is:

{code}

This code will expire in 10 minutes.

If you did not request this, please ignore this message.

Regards,
Hospital Management System
"""
    )

    # Connect to SMTP server
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()  # Secure connection
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        raise RuntimeError(f"Failed to send email: {str(e)}")