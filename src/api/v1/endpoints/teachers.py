from fastapi import APIRouter, Depends, BackgroundTasks
from uuid import UUID
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user

from src.crud.teacher import list_accessible_courses, list_sections, view_profile, register_as_teacher, edit_profile, approve_student_subscription

from src.schemas.all_models import UserCreate, UserUpdate, Teacher

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.get("/courses")
def list_accessible_courses(
    current_teacher: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_accessible_courses(current_teacher, db)


@router.get("/courses/{course_id}/sections")
def list_course_sections(
    course_id: UUID,
    current_teacher: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_sections(course_id, current_teacher, db)


@router.get("/")
def view_teacher_profile(
    current_teacher: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return view_profile(current_teacher, db)


@router.post("/", response_model=Teacher)
def register_teacher(
    payload: UserCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return register_as_teacher(payload, current_user, db)


@router.put("/", response_model=Teacher)
def update_teacher_profile(
    payload: UserUpdate,
    current_teacher=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return edit_profile(payload, current_teacher, db)


@router.post("/enrollments/{request_id}/approve")
def approve_student_subscription(
    request_id: UUID,
    current_teacher: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return approve_student_subscription(request_id, current_teacher, db)


