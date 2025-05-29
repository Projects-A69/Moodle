from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from src.api.deps import get_db, get_student_user
from src.models.models import Student
from src.models.models import User as UserModel
from src.schemas.all_models import CoursesRate
from src.crud.student import subscribe_to_course, rate_course, unsubscribe_from_course

router = APIRouter()

@router.post("/courses/{course_id}/subscribe")
def subscribe_to_courses(
    course_id: UUID,
    current_student: Student = Depends(get_student_user()),
    db: Session = Depends(get_db),
):
    return subscribe_to_course(
        course_id=course_id,
        current_student=current_student,
        db=db,)


@router.delete("/courses/{course_id}/unsubscribe")
def unsubscribe_from_course_endpoint(course_id: UUID,
                                     student_id: UUID,
                                     db: Session = Depends(get_db)):

    return unsubscribe_from_course(course_id=course_id,
                                   student_id=student_id,
                                   db=db)


@router.put("/courses/{course_id}/rate")
def rate_courses(
    course_id: UUID,
    payload: CoursesRate,
    current_user: UserModel = Depends(get_student_user()),
    db: Session = Depends(get_db),
):
    return rate_course(
        course_id=course_id,
        payload=payload,
        current_user=current_user,
        db=db
    )