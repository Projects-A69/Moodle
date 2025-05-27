from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.models.models import User as UserModel, Role
from src.crud import admin as admin_crud
from src.utils.custom_responses import BadRequest, Unauthorized
from itsdangerous import BadSignature, SignatureExpired
from src.utils.token_utils import verify_approval_token

router = APIRouter()

@router.get("/users")
def get_all_users(role: str = None,search: str = None,db: Session = Depends(get_db),
                  current_user: UserModel = Depends(get_current_user)):
    
    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can list all users.")
    
    return admin_crud.list_all_users(db, role, search)

@router.put("/users/update-status/{user_id}")
def update_is_active(user_id: UUID, db: Session = Depends(get_db),
                             current_user: UserModel = Depends(get_current_user)):
    
    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can toggle user status.")
    
    return admin_crud.update_user_active(db, user_id)

@router.get("/pending-teachers")
def list_pending_teachers(db: Session = Depends(get_db),
                         current_user: UserModel = Depends(get_current_user)):
    
    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can see pending teachers.")
    
    return admin_crud.list_pending_teachers(db)

@router.put("/teachers/{user_id}/approve")
def approve_teacher(user_id: UUID, db: Session = Depends(get_db),
                    current_user: UserModel = Depends(get_current_user)):
    
    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can approve teachers.")
    
    return admin_crud.approve_teacher_by_id(db, user_id)

@router.get("/teachers/approve")
def approve_teacher_with_token(token: str, db: Session = Depends(get_db)):


    try:
        user_id = verify_approval_token(token)
    except SignatureExpired:
        raise BadRequest("Token has expired.")
    except BadSignature:
        raise BadRequest("Invalid approval token.")

    return admin_crud.approve_teacher_by_id(db, user_id)


@router.get("/courses")
def list_courses(teacher_id: UUID | None = None,student_id: UUID | None = None,
    title: str | None = None,skip: int = 0,
    limit: int = 10,db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    
    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can view all courses.")

    return admin_crud.list_all_courses(db, teacher_id, student_id, title)


@router.put("/courses/{course_id}/hide")
def hide_course(course_id: UUID,db: Session = Depends(get_db),
                current_user: UserModel = Depends(get_current_user)):

    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can hide courses.")

    return admin_crud.hide_course_crud(db, course_id)

@router.delete("/courses/{course_id}")
def delete_course(course_id: UUID,db: Session = Depends(get_db),
                  current_user: UserModel = Depends(get_current_user)):

    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can delete courses.")

    return admin_crud.delete_course_crud(db, course_id)

@router.delete("/courses/{course_id}/students/{student_id}")
def remove_student_from_course(course_id: UUID,student_id: UUID,db: Session = Depends(get_db),
                               current_user: UserModel = Depends(get_current_user)):
    
    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can remove students from courses.")

    return admin_crud.remove_student_from_course(db, course_id, student_id)


@router.get("/courses/{course_id}/ratings")
def trace_course_ratings(course_id: UUID,db: Session = Depends(get_db),
                         current_user: UserModel = Depends(get_current_user)):

    if current_user.role != Role.ADMIN:
        raise Unauthorized("Only admins can trace course ratings.")

    return admin_crud.trace_course_ratings(db, course_id)
