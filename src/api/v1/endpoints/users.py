from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.core.authentication import create_token
from src.models.models import User as UserModel
from src.schemas.all_models import UserCreate, UserUpdate, LoginRequest
from src.crud import user as user_crud

router = APIRouter()

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = user_crud.login_user(db, payload)
    return {"access_token": create_token(user)}

@router.post("/register")
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    return user_crud.handle_registration(db, payload)

@router.get("/info")
def get_current_user_info(current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)):
    return user_crud.get_user_info(db, current_user)

@router.put("/info")
def update_user_info(payload: UserUpdate,db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    return user_crud.update_user_info(db, current_user.id, payload)

@router.post("/logout")
def logout():
    pass
