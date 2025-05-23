from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.security import verify_password
from src.api.deps import get_db, get_current_user
from src.core.authentication import create_token
from src.models.models import Admin, Role, Student, Teacher, User as UserModel
from src.schemas.all_models import UserCreate, UserUpdate, LoginRequest
from src.crud import user as user_crud

router = APIRouter()

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = user_crud.get_by_email(db, payload.email)

    if user is None or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"access_token": create_token(user)}


@router.post("/register")
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    if payload.role == Role.ADMIN:
        if not payload.first_name or not payload.last_name:
            raise HTTPException(status_code=422, detail="Admins must provide first and last name")

    elif payload.role == Role.TEACHER:
        missing_fields = [field for field in ["first_name", "last_name", "phone_number", "linked_in_acc"] if not getattr(payload, field)]
        if missing_fields:
            raise HTTPException(status_code=422,detail=f"Missing teacher fields: {', '.join(missing_fields)}")

    elif payload.role == Role.STUDENT:
        if not payload.first_name or not payload.last_name:
            raise HTTPException(status_code=422, detail="Students must provide first and last name")

    new_user = user_crud.register_user(db, payload)

    return {"message": "User registered successfully", "user_id": str(new_user.id)}




@router.get("/info")
def get_current_user_info(current_user: UserModel = Depends(get_current_user),db: Session = Depends(get_db)):
    base_info = {"email": current_user.email,"role": current_user.role.value}

    if current_user.role == Role.STUDENT:
        student = db.query(Student).filter(Student.id == current_user.id).first()
        if student:
            base_info.update({"first_name": student.first_name,"last_name": student.last_name,})

    elif current_user.role == Role.TEACHER:
        teacher = db.query(Teacher).filter(Teacher.id == current_user.id).first()
        if teacher:
            base_info.update({"first_name": teacher.first_name,"last_name": teacher.last_name,
                "phone_number": teacher.phone_number,"linked_in_acc": teacher.linked_in_acc,
                "profile_picture": teacher.profile_picture})

    elif current_user.role == Role.ADMIN:
        admin = db.query(Admin).filter(Admin.id == current_user.id).first()
        if admin:
            base_info.update({"first_name": admin.first_name,"last_name": admin.last_name})

    return base_info


@router.put("/info")
def update_user_info(payload: UserUpdate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    updated_user = user_crud.update_user_info(db, current_user.id, payload)
    return {"message": "User updated","user": updated_user.email}


@router.post("/logout")
def logout():
    pass
