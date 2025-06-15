from typing import Generator, Optional

from fastapi import Depends, HTTPException, Request
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


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    user = from_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def optional_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    auth: str = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ")[1]
    return from_token(db, token)


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can perform this action.")
    return current_user


def get_teacher_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.TEACHER:
        raise Unauthorized("Access for teacher only.")
    return current_user


def get_student_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.STUDENT:
        raise Unauthorized("Only students can perform this action.")
    return current_user

def teacher_or_admin(current_user: User = Depends(get_current_user)) -> Optional[User]:
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
