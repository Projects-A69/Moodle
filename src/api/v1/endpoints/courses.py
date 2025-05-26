from fastapi import APIRouter, Depends, HTTPException, Header
from pygments.lexer import default
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user
from src.api.deps import get_db, get_current_user, optional_user
from src.crud.course import create_courses, get_course, get_course_by_id, update_specific_course, rating_course
from src.schemas.all_models import CourseInDB, CoursesCreate, CoursesUpdate, User, CoursesRate, Role
from src.utils.custom_responses import Unauthorized

from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("/")
def get_courses(title: Optional[str] = None, db: Session = Depends(get_db), current_user: Optional[User] = Depends(optional_user)):
    return get_course(db, title = title, current_user = current_user)

@router.get("/{course_id}")
def get_courses_by_id(course_id: UUID, db: Session = Depends(get_db)):
    course = get_course_by_id(db, course_id)
    return course

@router.post("/create_courses")
def create_course(payload: CoursesCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    owner_id = current_user.id
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        raise Unauthorized("Access for teacher or admin only!")
    new_courses = create_courses(db, payload.title, payload.description, payload.objectives, owner_id)
    return new_courses

@router.put("/update/{course_id}")
def update_course(course_id: UUID, payload: CoursesUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        raise Unauthorized("Access for teacher only!")
    return update_specific_course(db, course_id, payload)

@router.post("/rating/{course_id}")
def get_rating_course(course_id: UUID, payload: CoursesRate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        raise Unauthorized("Access for teacher only!")
    return rating_course(db =db, id = id, payload = payload, user = user)


