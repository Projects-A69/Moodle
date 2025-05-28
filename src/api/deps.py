from typing import Generator, Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.core.authentication import from_token
from src.database.session import SessionLocal
from src.models.models import Role, User
from src.utils.custom_responses import Unauthorized

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user = from_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

def optional_user(token: Optional[str] = None, db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    return from_token(db, token)


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can perform this action.")
    return current_user