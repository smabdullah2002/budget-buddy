from jose import jwt, JWTError
from datetime import datetime, timedelta
from .config import settings


class TokenGenerator:
    @staticmethod
    def create_token(data: dict, expires_in_minutes: int | None = None) -> str:
        to_encode = data.copy()
        minutes = expires_in_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
        expire = datetime.utcnow() + timedelta(minutes=minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def verify_token(token: str):
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None
