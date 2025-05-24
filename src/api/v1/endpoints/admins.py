from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.models.models import User as UserModel
from src.crud import admin as admin_crud
router = APIRouter()

@router.get("/users")
def get_all_users(role: str = None,search: str = None,db: Session = Depends(get_db),
                  current_user: UserModel = Depends(get_current_user)):
    return admin_crud.list_all_users(db, current_user, role, search)

@router.put("/users/{user_id}/deactivate")
def deactivate_user(user_id: str):
    pass

@router.put("/users/{user_id}/reactivate")
def reactivate_user(user_id: str):
    pass

@router.get("/pending-teachers")
def list_pending_teachers():
    pass

@router.put("/teachers/{teacher_id}/approve")
def approve_teacher(teacher_id: str):
    pass

@router.get("/courses")
def list_all_courses():
    pass

@router.put("/courses/{course_id}/hide")
def hide_course(course_id: str):
    pass

@router.delete("/courses/{course_id}")
def delete_course(course_id: str):
    pass

@router.get("/courses/search")
def search_courses_by_teacher_or_student():
    pass

@router.delete("/courses/{course_id}/students/{student_id}")
def remove_student_from_course(course_id: str, student_id: str):
    pass

@router.get("/courses/{course_id}/ratings")
def trace_course_ratings(course_id: str):
    pass
