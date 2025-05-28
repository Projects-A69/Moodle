from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.core.authentication import create_token
from src.models.models import User as UserModel
from src.schemas.all_models import AdminCreate, TeacherCreate, StudentCreate, AdminUpdate, TeacherUpdate, StudentUpdate, LoginRequest
from src.crud import user as user_crud
from src.crud.user import get_by_email, register_admin, register_teacher, register_student
from src.utils.custom_responses import BadRequest
router = APIRouter()

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = user_crud.login_user(db, payload)
    return {"access_token": create_token(user)}

@router.post("/register/admin")
def register_admin_user(payload: AdminCreate, db: Session = Depends(get_db)):
    if get_by_email(db, payload.email):
        raise BadRequest("Email already registered")
    return register_admin(db, payload)


@router.post("/register/teacher")
def register_teacher_user(payload: TeacherCreate, db: Session = Depends(get_db)):
    if get_by_email(db, payload.email):
        raise BadRequest("Email already registered")
    return register_teacher(db, payload)


@router.post("/register/student")
def register_student_user(payload: StudentCreate, db: Session = Depends(get_db)):
    if get_by_email(db, payload.email):
        raise BadRequest("Email already registered")
    return register_student(db, payload)

@router.get("/me")
def get_current_user_info(current_user: UserModel = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    
    return user_crud.get_user_info(db, current_user)

@router.put("/me/admin")
def update_me_admin(payload: AdminUpdate, db: Session = Depends(get_db),
                    current_user: UserModel = Depends(get_current_user)):
    return user_crud.update_admin_info(db, current_user, payload)

@router.put("/me/teacher")
def update_me_teacher(payload: TeacherUpdate, db: Session = Depends(get_db),
                      current_user: UserModel = Depends(get_current_user)):
    return user_crud.update_teacher_info(db, current_user, payload)

@router.put("/me/student")
def update_me_student(payload: StudentUpdate, db: Session = Depends(get_db),
                      current_user: UserModel = Depends(get_current_user)):
    return user_crud.update_student_info(db, current_user, payload)

@router.delete("/delete")
def delete_own_account(db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    return user_crud.delete_user(db, current_user.id)


@router.post("/logout")
def logout():
    return {"message": "Successfully logged out."}

