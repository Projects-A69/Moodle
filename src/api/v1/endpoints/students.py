from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from src.api.deps import get_db, get_current_user
from src.models.models import Student
from src.schemas.all_models import CoursesRate, StudentUpdate

from src.crud.student import list_accessible_courses, subscribe_to_course, view_course, list_sections, view_section, view_profile, rate_course, edit_profile

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/courses")
def list_accessible_courses(
    current_student: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_accessible_courses(current_student=current_student, db=db)


@router.post("/courses/{course_id}/subscribe")
def subscribe_to_course(
    course_id: UUID,
    current_student: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return subscribe_to_course(
        course_id=course_id,
        current_student=current_student,
        db=db,)


@router.get("/courses/{course_id}")
def view_course(
    course_id: UUID,
    current_student: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return view_course(course_id=course_id, current_student=current_student, db=db)


@router.get("/courses/{course_id}/sections")
def list_sections(
    course_id: UUID,
    current_student: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_sections(course_id=course_id, current_student=current_student, db=db)


@router.get("/courses/{course_id}/sections/{section_id}")
def view_section(
    course_id: UUID,
    section_id: UUID,
    current_student: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return view_section(
        course_id=course_id, section_id=section_id, current_student=current_student, db=db
    )


@router.get("/")
def view_profile(
    current_student: Student = Depends(get_current_user), db: Session = Depends(get_db)
):
    return view_profile(current_student=current_student, db=db)


@router.post("/courses/{course_id}/rate")
def rate_course(
    course_id: UUID,
    payload: CoursesRate,
    current_student: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return rate_course(
        course_id=course_id,
        payload=payload,
        current_student=current_student,
        db=db
    )


@router.put("/profile")
def edit_profile_endpoint(
    payload: StudentUpdate,
    current_student: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return edit_profile(payload=payload, current_student=current_student, db=db)
