from re import U
from httpx import UnsupportedProtocol
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.core.config import settings
from src.models.models import Admin, Role, User, Teacher, Student
from src.schemas.all_models import AdminCreate, TeacherCreate, StudentCreate, LoginRequest
from src.core.security import hash_password, verify_password
from uuid import UUID
from src.utils.custom_responses import Unauthorized, BadRequest, NotFound, UnprocessableEntity
from src.utils.email_utils import send_email
from src.utils.token_utils import generate_approval_token

def get_by_id(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound(f"User with id {user_id} not found")
    return user


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()

def login_user(db: Session, payload: LoginRequest) -> User:
    user = get_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.password):
        raise Unauthorized("Invalid email or password")
        
    
    if not user.is_active:
        raise BadRequest("User account is deactivated. Please contact support.")
    return user


def handle_registration(db: Session, payload):
    if get_by_email(db, payload.email):
        raise BadRequest("Email already registered")
        
    role = payload.role

    if role == Role.ADMIN:
        if not payload.first_name or not payload.last_name:
            raise UnprocessableEntity("Admins must provide first and last name")
        new_user = register_admin(db, payload)

    elif role == Role.TEACHER:
        if not payload.first_name:
            raise UnprocessableEntity("Teachers must provide first name")
        if not payload.last_name:
            raise UnprocessableEntity("Teachers must provide last name")
        if not payload.phone_number:
            raise UnprocessableEntity("Teachers must provide phone number")
        if not payload.linked_in_acc:
            raise UnprocessableEntity("Teachers must provide LinkedIn account")
        new_user = register_teacher(db, payload)

        token = generate_approval_token(str(new_user.id))
        approve_link = f"{settings.APP_BASE_URL}/api/v1/admins/teachers/approve?token={token}"
        email_body = (
            f"A new teacher has registered:\n\n"
            f"Name: {payload.first_name} {payload.last_name}\n"
            f"Email: {payload.email}\n\n"
            f"Click the link below to approve this teacher:\n"
            f"{approve_link}")

        send_email(
            to=settings.ADMIN_NOTIFICATION_EMAIL,
            subject="New Teacher Registration - Approval Required",
            body=email_body)
        
    elif role == Role.STUDENT:
        if not payload.first_name or not payload.last_name:
            raise UnprocessableEntity("Students must provide first and last name")
        new_user = register_student(db, payload)

    else:
        raise BadRequest("Unsupported role")

    return {"message": f"User {payload.first_name} registered successfully", "user_id": str(new_user.id)}


def register_admin(db: Session, payload: AdminCreate) -> User:
    
    if not payload.first_name or not payload.last_name:
        raise UnprocessableEntity("Admins must provide first and last name")
    
    hashed_password = hash_password(payload.password)
    new_user = User(email=payload.email.lower(), password=hashed_password, role=Role.ADMIN)
    db.add(new_user)
    db.flush()

    db.add(Admin(id=new_user.id, first_name=payload.first_name, last_name=payload.last_name))
    db.commit()
    return {
        "id": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
        "first_name": payload.first_name,
        "last_name": payload.last_name}

def register_teacher(db: Session, payload: TeacherCreate) -> User:
    
    if not payload.first_name:
        raise UnprocessableEntity("Teachers must provide first name")
    if not payload.last_name:
        raise UnprocessableEntity("Teachers must provide last name")
    if not payload.phone_number:
        raise UnprocessableEntity("Teachers must provide phone number")
    if not payload.linked_in_acc:
        raise UnprocessableEntity("Teachers must provide LinkedIn account")
    
    hashed_password = hash_password(payload.password)
    new_user = User(email=payload.email.lower(), password=hashed_password, role=Role.TEACHER)
    db.add(new_user)
    db.flush()

    db.add(Teacher(id=new_user.id,
                   first_name=payload.first_name,
                   last_name=payload.last_name,
                   profile_picture=payload.profile_picture,
                   phone_number=payload.phone_number,
                   linked_in_acc=payload.linked_in_acc))
    db.commit()
    return {
        "id": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "profile_picture": payload.profile_picture if payload.profile_picture else None,
        "phone_number": payload.phone_number,
        "linked_in_acc": payload.linked_in_acc}

def register_student(db: Session, payload: StudentCreate) -> User:
    
    if not payload.first_name or not payload.last_name:
        raise UnprocessableEntity("Students must provide first and last name")
    
    hashed_password = hash_password(payload.password)
    new_user = User(email=payload.email.lower(), password=hashed_password, role=Role.STUDENT)
    db.add(new_user)
    db.flush()

    db.add(Student(id=new_user.id,
                   first_name=payload.first_name,
                   last_name=payload.last_name,
                   profile_picture=payload.profile_picture))
    db.commit()
    return {
        "id": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "profile_picture": payload.profile_picture if payload.profile_picture else None}



def get_user_info(db: Session, current_user: User) -> dict:
    base_info = {
        "email": current_user.email,
        "role": current_user.role.value}

    if current_user.role == Role.ADMIN:
        admin = db.query(Admin).filter(Admin.id == current_user.id).first()
        if admin:
            base_info.update({"first_name": admin.first_name,"last_name": admin.last_name})

    elif current_user.role == Role.TEACHER:
        teacher = db.query(Teacher).filter(Teacher.id == current_user.id).first()
        if teacher:
            base_info.update({"first_name": teacher.first_name,"last_name": teacher.last_name,
                "phone_number": teacher.phone_number,"linked_in_acc": teacher.linked_in_acc,
                "profile_picture": teacher.profile_picture})

    elif current_user.role == Role.STUDENT:
        student = db.query(Student).filter(Student.id == current_user.id).first()
        if student:
            base_info.update({"first_name": student.first_name,"last_name": student.last_name,"profile_picture": student.profile_picture})

    return base_info

def update_admin_info(db: Session, current_user: User, payload) -> User:
    if payload.password is not None:
        current_user.password = hash_password(payload.password)

    admin = db.query(Admin).filter(Admin.id == current_user.id).first()
    if not admin:
        raise NotFound("Admin not found")

    if payload.first_name is not None:
        admin.first_name = payload.first_name
    if payload.last_name is not None:
        admin.last_name = payload.last_name

    db.commit()
    db.refresh(current_user)
    return current_user

def update_teacher_info(db: Session, current_user: User, payload) -> User:
    if payload.password is not None:
        current_user.password = hash_password(payload.password)

    teacher = db.query(Teacher).filter(Teacher.id == current_user.id).first()
    if not teacher:
        raise NotFound("Teacher not found")

    if payload.first_name is not None:
        teacher.first_name = payload.first_name
    if payload.last_name is not None:
        teacher.last_name = payload.last_name
    if payload.phone_number is not None:
        teacher.phone_number = payload.phone_number
    if payload.linked_in_acc is not None:
        teacher.linked_in_acc = payload.linked_in_acc
    if payload.profile_picture is not None:
        teacher.profile_picture = payload.profile_picture

    db.commit()
    db.refresh(current_user)
    return current_user

def update_student_info(db: Session, current_user: User, payload) -> User:
    if payload.password is not None:
        current_user.password = hash_password(payload.password)

    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        raise NotFound("Student not found")

    if payload.first_name is not None:
        student.first_name = payload.first_name
    if payload.last_name is not None:
        student.last_name = payload.last_name
    if payload.profile_picture is not None:
        student.profile_picture = payload.profile_picture

    db.commit()
    db.refresh(current_user)
    return current_user

def delete_user(db: Session, user_id: UUID):
    user = get_by_id(db, user_id)
    db.delete(user)
    db.commit()
    return {"message": "Account deleted successfully."}
