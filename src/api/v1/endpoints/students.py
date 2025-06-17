from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_student_user
from src.crud.student import (
    get_all_favorite_courses,
    rate_course,
    subscribe_to_course,
    toggle_favorite_course,
    unsubscribe_from_course,
)
from src.models.models import Student, StudentCourse
from src.models.models import User as UserModel
from src.schemas.all_models import CoursesRate

router = APIRouter()

@router.get("/courses")
def get_student_courses(current_student: Student = Depends(get_student_user), db: Session = Depends(get_db)):
    return (db.query(StudentCourse).filter(StudentCourse.student_id == current_student.id).all())

@router.post("/courses/{course_id}/subscribe")
def subscribe_to_courses(
    course_id: UUID,
    current_student: Student = Depends(get_student_user),
    db: Session = Depends(get_db),
):
    return subscribe_to_course(
        course_id=course_id,
        current_student=current_student,
        db=db,
    )


@router.delete("/courses/{course_id}/unsubscribe")
def unsubscribe_from_course_endpoint(
    course_id: UUID, student_id: UUID, db: Session = Depends(get_db)
):

    return unsubscribe_from_course(course_id=course_id, student_id=student_id, db=db)

@router.get("/students/courses")
def get_student_courses(
    current_student: Student = Depends(get_student_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(StudentCourse)
        .options(joinedload(StudentCourse.course))
        .filter(StudentCourse.student_id == current_student.id)
        .all()
    )


@router.post("/courses/{course_id}/rate")
def rate_course_endpoint(
    course_id: UUID,
    payload: CoursesRate,
    current_student: UserModel = Depends(get_student_user),
    db: Session = Depends(get_db),
):

    return rate_course(db, course_id, payload, current_student)


@router.get("/courses/favorites")
def get_favorite_courses(
    current_student: UserModel = Depends(get_student_user),
    db: Session = Depends(get_db),
):
    return get_all_favorite_courses(db, current_student)


@router.put("/courses/favorites/{course_id}")
def toggle_favorite_course_route(
    course_id: UUID,
    current_student: UserModel = Depends(get_student_user),
    db: Session = Depends(get_db),
):
    return toggle_favorite_course(course_id, current_student, db)
