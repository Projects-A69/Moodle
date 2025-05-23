from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.models import Admin, Role, User, Teacher, Student
from src.schemas.all_models import UserUpdate,UserCreate
from src.core.security import hash_password

def get_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return user


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


# def get_all_users(db: Session) -> list[User]:
#     return db.query(User).all()


def register_user(db: Session, payload: UserCreate) -> User:
    hashed_password = hash_password(payload.password)
    new_user = User(
        email=payload.email,
        password=hashed_password,
        role=payload.role
    )
    db.add(new_user)
    db.flush()

    if payload.role == Role.ADMIN:
        db.add(Admin(
            id=new_user.id,
            first_name=payload.first_name,
            last_name=payload.last_name
        ))
    elif payload.role == Role.TEACHER:
        db.add(Teacher(
            id=new_user.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            profile_picture=payload.profile_picture,
            phone_number=payload.phone_number,
            linked_in_acc=payload.linked_in_acc
        ))
    elif payload.role == Role.STUDENT:
        db.add(Student(
            id=new_user.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            subscribed=payload.subscribed
        ))
    else:
        raise HTTPException(status_code=400, detail="Invalid role")

    db.commit()
    db.refresh(new_user)
    return new_user



def update_user_info(db: Session, user_id: int, payload: UserUpdate) -> User:
    user = get_by_id(db, user_id)
    if payload.password:
        user.password = hash_password(payload.password)
    db.commit()
    db.refresh(user)
    return user

