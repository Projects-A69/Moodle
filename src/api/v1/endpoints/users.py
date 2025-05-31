from fastapi import APIRouter, Depends,Form,File,UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.core.authentication import create_token
from src.models.models import User as UserModel
from src.schemas.all_models import AdminCreate, TeacherCreate, StudentCreate, AdminUpdate, TeacherUpdate, StudentUpdate
from src.crud import user as user_crud
from src.utils.custom_responses import BadRequest
from src.utils.s3 import upload_image_to_s3

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_crud.get_by_email(db, form_data.username)
    if not user or not user_crud.verify_password(form_data.password, user.password):
        raise BadRequest("Invalid email or password")
    return {"access_token": create_token(user), "token_type": "bearer"}

@router.post("/register/admin")
def register_admin_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)):
    payload = AdminCreate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password)
    if user_crud.get_by_email(db, payload.email):
        raise BadRequest("Email already registered")
    return user_crud.register_admin(db, payload)

@router.post("/register/teacher")
def register_teacher_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone_number: str = Form(...),
    linked_in_acc: str = Form(...),
    profile_picture: UploadFile = File(None),
    db: Session = Depends(get_db)):

    image_url = None
    if profile_picture:
        image_url = upload_image_to_s3(profile_picture)

    payload = TeacherCreate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        phone_number=phone_number,
        linked_in_acc=linked_in_acc,
        profile_picture=image_url)

    if user_crud.get_by_email(db, payload.email):
        raise BadRequest("Email already registered")
    return user_crud.register_teacher(db, payload)

@router.post("/register/student")
def register_student_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_picture: UploadFile = File(None),
    db: Session = Depends(get_db)):
    
    image_url = None
    if profile_picture:
        image_url = upload_image_to_s3(profile_picture)

    payload = StudentCreate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        profile_picture=image_url,)

    if user_crud.get_by_email(db, payload.email):
        raise BadRequest("Email already registered")
    return user_crud.register_student(db, payload)

@router.get("/me")
def get_current_user_info(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_crud.get_user_info(db, current_user)

@router.put("/me/admin")
def update_me_admin(
    first_name: str = Form(None),
    last_name: str = Form(None),
    password: str = Form(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    payload = AdminUpdate(
        first_name=first_name,
        last_name=last_name,
        password=password
    )
    return user_crud.update_admin_info(db, current_user, payload)

@router.put("/me/teacher")
def update_me_teacher(
    first_name: str = Form(None),
    last_name: str = Form(None),
    password: str = Form(None),
    phone_number: str = Form(None),
    linked_in_acc: str = Form(None),
    profile_picture: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    
    image_url = None
    
    if profile_picture:
        image_url = upload_image_to_s3(profile_picture)

    payload = TeacherUpdate(
        first_name=first_name,
        last_name=last_name,
        password=password,
        phone_number=phone_number,
        linked_in_acc=linked_in_acc,
        profile_picture=image_url,)

    return user_crud.update_teacher_info(db, current_user, payload)

@router.put("/me/student")
def update_me_student(
    first_name: str = Form(None),
    last_name: str = Form(None),
    password: str = Form(None),
    profile_picture: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):

    image_url = None
    
    if profile_picture:
        image_url = upload_image_to_s3(profile_picture)

    payload = StudentUpdate(
        first_name=first_name,
        last_name=last_name,
        password=password,
        profile_picture=image_url)

    return user_crud.update_student_info(db, current_user, payload)

@router.delete("/delete")
def delete_own_account(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return user_crud.delete_user(db, current_user.id)

@router.post("/logout")
def logout():
    return {"message": "Successfully logged out."}