from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user
from src.api.deps import get_db, get_current_user, optional_user, get_teacher_user
from src.crud.course import create_courses, get_course, get_course_by_id, update_specific_course, rating_course
from src.schemas.all_models import CourseInDB, CoursesCreate, CoursesUpdate, User, CoursesRate, Role
from src.utils.custom_responses import Unauthorized
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("")
def get_courses(title: Optional[str] = None, db: Session = Depends(get_db), current_user: Optional[User] = Depends(optional_user)):
    return get_course(db, title = title, current_user = current_user)

@router.get("/{course_id}")
def get_courses_by_id(course_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_teacher_user)):
    course = get_course_by_id(db, course_id, current_user = current_user)
    return course

@router.post("")
def create_course(payload: CoursesCreate, db: Session = Depends(get_db), current_user = Depends(get_teacher_user)):
    owner_id = current_user.id
    new_courses = create_courses(db, payload.title, payload.description, payload.objectives, payload.picture, payload.is_premium, owner_id)
    return new_courses

@router.put("/courses/{course_id}")
def update_course(course_id: UUID, payload: CoursesUpdate, db: Session = Depends(get_db), current_user = Depends(get_teacher_user)):
    return update_specific_course(db, course_id, payload, current_user= current_user)

@router.post("/courses/{course_id}")
def get_rating_course(course_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_teacher_user)):
    return rating_course(db, course_id, current_user)


