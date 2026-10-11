import hashlib
import hmac
import os

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config import get_settings


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 390000)
    return f"pbkdf2_sha256$390000${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        method, iterations, salt, expected = stored.split("$")
        if method != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iterations))
        return hmac.compare_digest(digest, bytes.fromhex(expected))
    except (ValueError, TypeError):
        return False


def create_token(user_id: int) -> str:
    serializer = URLSafeTimedSerializer(get_settings()["secret_key"], salt="sprintdesk-access")
    return serializer.dumps({"sub": user_id})


def decode_token(token: str) -> int | None:
    serializer = URLSafeTimedSerializer(get_settings()["secret_key"], salt="sprintdesk-access")
    try:
        data = serializer.loads(token, max_age=get_settings()["token_ttl"])
        return int(data["sub"])
    except (BadSignature, SignatureExpired, KeyError, ValueError, TypeError):
        return None
