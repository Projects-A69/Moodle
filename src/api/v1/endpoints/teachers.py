from fastapi import APIRouter, Depends
from uuid import UUID
from itsdangerous import BadSignature, SignatureExpired
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.crud.teacher import list_accessible_courses, list_sections, view_profile, remove_student_from_course
from src.models.models import Role, User
from src.schemas.all_models import Teacher
from src.utils.custom_responses import Unauthorized, BadRequest
from src.utils.token_utils import verify_approval_token

router = APIRouter()


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


@router.get("/teachers/approval")
def approve_student_by_token(token: str,
                             db: Session = Depends(get_db)):
    try:
        user_id = verify_approval_token(token)
    except SignatureExpired:
        raise BadRequest("Token has expired.")

    except BadSignature:
        raise BadRequest("Invalid approval token.")

    return approve_student_by_id(db, user_id)


@router.put("/teachers/{user_id}/approval")
def approve_student(user_id: UUID,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):

    if current_user.role != Role.TEACHER:
        raise Unauthorized("Only teachers can approve students.")

    return approve_student_by_id(db, user_id)


@router.delete("/courses/{course_id}/students/{student_id}", tags=["courses"])
def remove_student_from_course(course_id: UUID,
                               student_id: UUID,
                               db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    if current_user.role != Role.TEACHER:
        raise Unauthorized("Only teachers can remove students from courses.")

    return remove_student_from_course(db, course_id, student_id)

@router.put("/courses/{course_id}/students/{student_id}", tags=["courses"])
def approve_student_by_id(course_id: UUID,
                          student_id: UUID,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):

    if current_user.role != Role.TEACHER:
        raise Unauthorized("Only teachers can approve students from courses.")

    return approve_student_by_id(db, course_id, student_id, current_user)


# def edit_teacher_profile(
#     payload: TeacherUpdate,
#     current_teacher=Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     return edit_profile(payload, current_teacher, db)
