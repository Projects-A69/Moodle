from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.models import Admin, Role, User, Teacher, Student
from src.schemas.all_models import UserUpdate, UserCreate, LoginRequest
from src.core.security import hash_password, verify_password
from uuid import UUID
from src.utils.common import get_by_id
from src.utils.custom_responses import Unauthorized, BadRequest, NotFound, UnprocessableEntity



def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()

def login_user(db: Session, payload: LoginRequest) -> User:
    user = get_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.password):
        raise Unauthorized("Invalid email or password")
        
    
    if not user.is_active:
        raise BadRequest("User account is deactivated. Please contact support.")
    return user


def handle_registration(db: Session, payload: UserCreate):
    if get_by_email(db, payload.email):
        raise BadRequest("Email already registered")
        
    if payload.role == Role.ADMIN:
        if not payload.first_name or not payload.last_name:
            raise UnprocessableEntity("Admins must provide first and last name")
    elif payload.role == Role.TEACHER:
        if not payload.first_name:
            raise UnprocessableEntity("Teachers must provide first name")
        if not payload.last_name:
            raise UnprocessableEntity("Teachers must provide last name")
        if not payload.phone_number:
            raise UnprocessableEntity("Teachers must provide phone number")
        if not payload.linked_in_acc:
            raise UnprocessableEntity("Teachers must provide LinkedIn account")

    elif payload.role == Role.STUDENT:
        if not payload.first_name or not payload.last_name:
            raise UnprocessableEntity("Students must provide first and last name")

    new_user = register_user(db, payload)
    return {"message": f"User:{payload.first_name} registered successfully", "user_id": str(new_user.id)}


def register_user(db: Session, payload: UserCreate) -> User:
    hashed_password = hash_password(payload.password)
    new_user = User(email=payload.email.lower(), password=hashed_password, role=payload.role)
    db.add(new_user)
    db.flush()

    if payload.role == Role.ADMIN:
        db.add(Admin(id=new_user.id, first_name=payload.first_name, last_name=payload.last_name))
    elif payload.role == Role.TEACHER:
        db.add(Teacher(id=new_user.id, first_name=payload.first_name,
                       last_name=payload.last_name, profile_picture=payload.profile_picture,
                       phone_number=payload.phone_number, linked_in_acc=payload.linked_in_acc))
    elif payload.role == Role.STUDENT:
        db.add(Student(id=new_user.id, first_name=payload.first_name, last_name=payload.last_name,profile_picture=payload.profile_picture))
    else:
        raise HTTPException(status_code=400, detail="Invalid role")

    db.commit()
    db.refresh(new_user)
    return new_user


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


def update_user_info(db: Session, user_id: UUID, payload: UserUpdate) -> User:
    user = get_by_id(db, user_id)

    if payload.password:
        user.password = hash_password(payload.password)

    if user.role == Role.ADMIN:
        admin = db.query(Admin).filter(Admin.id == user_id).first()
        if not admin:
            raise NotFound("Admin not found")
        if payload.first_name:
            admin.first_name = payload.first_name
        if payload.last_name:
            admin.last_name = payload.last_name

    elif user.role == Role.TEACHER:
        teacher = db.query(Teacher).filter(Teacher.id == user_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        if payload.first_name:
            teacher.first_name = payload.first_name
        if payload.last_name:
            teacher.last_name = payload.last_name
        if payload.phone_number:
            teacher.phone_number = payload.phone_number
        if payload.linked_in_acc:
            teacher.linked_in_acc = payload.linked_in_acc
        if payload.profile_picture:
            teacher.profile_picture = payload.profile_picture

    elif user.role == Role.STUDENT:
        student = db.query(Student).filter(Student.id == user_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        if payload.first_name:
            student.first_name = payload.first_name
        if payload.last_name:
            student.last_name = payload.last_name
        if payload.profile_picture:
            student.profile_picture = payload.profile_picture
        

    db.commit()
    db.refresh(user)
    return user
