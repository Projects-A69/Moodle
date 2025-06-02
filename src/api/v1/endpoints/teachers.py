from uuid import UUID

from fastapi import APIRouter, Depends
from itsdangerous import BadSignature, SignatureExpired
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_teacher_user
from src.crud.teacher import (
    approve_student_by_id,
    list_pending_students,
    remove_student_from_course,
    toggle_course_visibility_by_teacher,
)
from src.models.models import User as UserModel
from src.utils.custom_responses import BadRequest
from src.utils.token_utils import verify_student_approval_token

router = APIRouter()


@router.get("/teachers/{course_id}/pending")
def list_pending_students_endpoint(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_teacher: UserModel = Depends(get_teacher_user),
):
    return list_pending_students(
        db=db, current_teacher=current_teacher, course_id=course_id
    )


@router.get("/teachers/approval", include_in_schema=False)
def approve_student_by_token(token: str, db: Session = Depends(get_db)):
    try:
        data = verify_student_approval_token(token)
        student_id = UUID(data["student_id"])
        course_id = UUID(data["course_id"])
    except SignatureExpired:
        raise BadRequest("Token has expired.")
    except BadSignature:
        raise BadRequest("Invalid approval token.")
    except Exception:
        raise BadRequest("Invalid data in token.")

    return approve_student_by_id(db, student_id, course_id)


@router.post("/teachers/{user_id}/approvals")
def approve_student_endpoint(
    user_id: UUID, course_id: UUID, db: Session = Depends(get_db)
):
    return approve_student_by_id(db, user_id, course_id)


@router.delete("/courses/{course_id}/students/{student_id}")
def remove_student_from_course_endpoint(
    course_id: UUID, student_id: UUID, db: Session = Depends(get_db)
):
    return remove_student_from_course(db, course_id, student_id)



@router.put("/courses/{course_id}/visibility")
def toggle_course_visibility(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_teacher_user),
):
    return toggle_course_visibility_by_teacher(db, course_id, current_user)
