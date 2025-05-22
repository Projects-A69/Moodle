from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.security import verify_password
from src.api.deps import get_db,get_current_user
from src.core.authentication import create_token
from src.models.models import User as UserModel
from src.schemas.all_models import LoginRequest,User as UserSchema
from src.crud import user as user_crud

router = APIRouter()

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = user_crud.get_by_email(db, payload.email)

    if user is None or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"access_token": create_token(user)}


@router.post("/register")
def register_user(payload: UserSchema, db: Session = Depends(get_db)):
    if user_crud.get_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = user_crud.register_user(db, payload.email, payload.password, payload.role)

    return {"message": "User registered successfully", "user_id": str(new_user.id)}


@router.get("/info")
def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    return {"email": current_user.email, "role": current_user.role}


@router.put("/info")
def update_user_info():
    pass


@router.post("/logout")
def logout():
    pass