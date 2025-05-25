from uuid import UUID

from fastapi import HTTPException
from src.database import session
from src.models.models import User


def get_by_id(db: session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
