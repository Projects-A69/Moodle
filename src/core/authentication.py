from jose import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from src.models.models import User
from src.core.config import settings
from src.crud import user as user_crud


def create_token(user: User) -> str:
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def is_authenticated(db: Session, token: str) -> bool:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("email")
        user = user_crud.get_by_email(db, email)
        return user is not None and str(user.id) == str(payload.get("user_id"))
    except Exception:
        return False


def from_token(db: Session, token: str) -> User | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("email")
        return user_crud.get_by_email(db, email)
    except Exception:
        return None
