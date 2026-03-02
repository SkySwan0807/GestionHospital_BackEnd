import random
import string
from datetime import datetime, timedelta

# almacenamiento temporal en memoria
reset_codes = {}

CODE_EXPIRATION_MINUTES = 10


def generate_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def store_code(email: str) -> str:
    code = generate_code()
    expiration = datetime.utcnow() + timedelta(minutes=CODE_EXPIRATION_MINUTES)

    reset_codes[email] = {
        "code": code,
        "expires_at": expiration
    }

    return code


def verify_code(email: str, code: str) -> bool:
    data = reset_codes.get(email)

    if not data:
        return False

    if datetime.utcnow() > data["expires_at"]:
        reset_codes.pop(email, None)
        return False

    if data["code"] != code:
        return False

    reset_codes.pop(email, None)
    return True