from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import bcrypt

from src.api.deps import get_db
from src.core.authentication import create_token
from src.models.models import User as UserModel
from src.schemas.all_models import User as UserSchema
from src.crud import user as user_crud

router = APIRouter()


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = user_crud.get_by_email(db, form_data.username)
    except HTTPException:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not bcrypt.checkpw(form_data.password.encode(), user.password.encode()):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"access_token": create_token(user), "token_type": "bearer"}


@router.post("/register")
def register_user(payload: UserSchema, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hashpw(payload.password.encode(), bcrypt.gensalt()).decode()

    new_user = UserModel(
        email=payload.email,
        password=hashed_password,
        role=payload.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": str(new_user.id)}
