from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.models import User
from src.core.security import hash_password

def get_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return user


def get_by_email(db: Session, email: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return user


def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()


def register_user(db: Session, email: str, password: str, role) -> User:
    hashed_password = hash_password(password)
    new_user = User(email=email, password=hashed_password, role=role)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
