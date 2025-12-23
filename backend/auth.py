"""Authentication module for password hashing and JWT token management."""
import logging
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt
from config import Config


logger = logging.getLogger(__name__)


def hash_password(password: str) -> bytes:

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


def generate_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=Config.JWT_EXPIRATION_DAYS),
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> Optional[str]:
  
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        logger.warning("Token verification failed: %s", e)
        return None

   