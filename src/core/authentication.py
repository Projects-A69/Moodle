from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.core.config import settings
from src.crud import user as user_crud
from src.models.models import User


def create_token(user: User) -> str:
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION),
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def from_token(db: Session, token: str) -> User | None:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload.get("email")
        user_id = payload.get("user_id")
        user = user_crud.get_by_email(db, email)
        return user if user and str(user.id) == user_id else None
    except JWTError:
        return None
