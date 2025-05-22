from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.security import hash_password, verify_password
from src.api.deps import get_db
from src.core.authentication import create_token
from src.models.models import User as UserModel
from src.schemas.all_models import LoginRequest,User as UserSchema
from src.crud import user as user_crud

router = APIRouter()

@router.get("/")
def read_users():
    pass


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = user_crud.get_by_email(db, payload.email)

    if user is None or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"access_token": create_token(user)}


@router.post("/register")
def register_user(payload: UserSchema, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(payload.password)

    new_user = UserModel(
        email=payload.email,
        password=hashed_password,
        role=payload.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": str(new_user.id)}
