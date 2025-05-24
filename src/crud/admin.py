from sqlalchemy.orm import Session
from src.utils.custom_responses import Unauthorized,BadRequest
from src.models.models import User,Role, Admin, Teacher, Student
from src.crud import user as user_crud
from src.utils.custom_responses import NotFound
def list_all_users(db: Session,current_user: User,role:str = None, search:str = None) -> list[User]:
    
    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can list all users.")

    if role and role.upper() not in ["ADMIN", "TEACHER", "STUDENT"]:
        raise BadRequest("Invalid role. Must be one of: ADMIN, TEACHER, STUDENT.")

    if role and search:
        users = db.query(User).filter(User.role == Role(role.upper()),
                            User.email.ilike(f"%{search}%")).all()
    elif role:
        users = db.query(User).filter(User.role == Role(role.upper())).all()
    elif search:
        users = db.query(User).filter(User.email.ilike(f"%{search}%")).all()
    else:
        users = db.query(User).all()

    result = []

    for user in users:
        user_info = {"id": str(user.id),"email": user.email,
                                    "role": user.role.value,"is_active": user.is_active}

        if user.role == Role.ADMIN:
            admin = db.query(Admin).filter(Admin.id == user.id).first()
            if admin:
                user_info.update({"first_name": admin.first_name,"last_name": admin.last_name})

        elif user.role == Role.TEACHER:
            teacher = db.query(Teacher).filter(Teacher.id == user.id).first()
            if teacher:
                user_info.update({"first_name": teacher.first_name,"last_name": teacher.last_name,
                    "phone_number": teacher.phone_number,"linked_in_acc": teacher.linked_in_acc,
                    "profile_picture": teacher.profile_picture})

        elif user.role == Role.STUDENT:
            student = db.query(Student).filter(Student.id == user.id).first()
            if student:
                user_info.update({"first_name": student.first_name,"last_name": student.last_name,"profile_picture": student.profile_picture})

        result.append(user_info)

    return result

def update_user_activation(db: Session, email: str):
    user = user_crud.get_by_email(db, email)
    
    if not user:
        raise NotFound(f"User with email: {email} not found")

    user.is_active = not user.is_active

    db.commit()

    status = "activated" if user.is_active else "deactivated"
    
    return {"message": f"User {status} successfully."}
    
    