from fastapi import APIRouter, Depends
from uuid import UUID
from itsdangerous import BadSignature, SignatureExpired
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_teacher_user
from src.crud.teacher import approve_student_by_id, remove_student_from_course
from src.models.models import Role
from src.models.models import User as UserModel
from src.utils.custom_responses import Unauthorized, BadRequest
from src.utils.token_utils import verify_student_approval_token

router = APIRouter()


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
def approve_student(user_id: UUID,
                    db: Session = Depends(get_db),
                    current_user: UserModel = Depends(get_teacher_user)):

    return approve_student_by_id(db, user_id)


@router.delete("/courses/{course_id}/students/{student_id}")
def remove_student_from_course(course_id: UUID,
                               student_id: UUID,
                               db: Session = Depends(get_db),
                               current_user: UserModel = Depends(get_teacher_user)):

    return remove_student_from_course(db, course_id, student_id)

# @router.post("/courses/{course_id}/students/{student_id}")
# def approve_student_by_ids(course_id: UUID,
#                           student_id: UUID,
#                           db: Session = Depends(get_db),
#                           current_user: UserModel = Depends(get_teacher_user)):


#     return approve_student_by_id(db, course_id, student_id, current_user)