from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.models import User
import bcrypt


def get_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user


def get_by_email(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user


def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()


def register_user(db: Session, user_data: User) -> User:
    hashed_password = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt())
    user_data.password = hashed_password.decode()

    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data
