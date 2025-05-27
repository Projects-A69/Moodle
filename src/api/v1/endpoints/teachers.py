from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.crud.teacher import list_accessible_courses, list_sections, view_profile, approve_student_by_token, edit_profile


from src.schemas.all_models import UserUpdate, Teacher

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.get("/courses")
def list_accessible_courses(
    current_teacher: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_accessible_courses(current_teacher, db)


@router.get("/courses/{course_id}/sections")
def list_sections(
    course_id: UUID,
    current_teacher: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_sections(course_id, current_teacher, db)


@router.get("/")
def view_profile(
    current_teacher: Teacher = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return view_profile(current_teacher, db)


@router.get("/enrollments/approve-student")
def approve_student_subscription(
    token: str,
    db: Session = Depends(get_db),
):
    return approve_student_by_token(token, db)


@router.put("/", response_model=Teacher)
def edit_teacher_profile(
    payload: UserUpdate,
    current_teacher=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return edit_profile(payload, current_teacher, db)
