from fastapi import Depends
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.models.models import Course, Teacher, Role
from src.crud.user import get_by_id
from src.utils.custom_responses import NotFound, Forbidden, BadRequest
from uuid import UUID
from src.utils.token_utils import verify_student_approval_token

def list_accessible_courses(current_teacher: Teacher = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """
    Lists all public and premium courses the teacher is owner of.
    """
    public_courses = db.query(Course).filter(Course.is_premium == False).all()
    owned_courses = current_teacher.courses

    return {
        "public_courses": public_courses,
        "owned_courses": owned_courses
    }


def list_sections(course_id: str,
                  current_teacher: Teacher = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """
    List all sections for a course owned by the current teacher.
    """
    course = db.query(Course).filter(Course.id == course_id, Course.owner_id == current_teacher.id).first()
    if not course:
        raise NotFound("Course not found")

    sections = course.sections
    return {"sections": sections}


def view_profile(current_teacher: Teacher = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    View teacher's profile info.
    """
    teacher = get_by_id(db, current_teacher.id)

    return teacher


def view_course(course_id: UUID, current_teacher: Teacher, db: Session):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFound("Course not found")

    if course.owner_id != current_teacher.id:
        raise Forbidden("You can only view your own courses")

    return course


def approve_student_by_token(token: str, db: Session = Depends(get_db)):
    user_id_str = verify_student_approval_token(token)
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise BadRequest("Invalid user ID in token")

    user = get_by_id(db, user_id)

    if not user:
        raise NotFound("User not found")

    if user.role != Role.STUDENT:
        raise BadRequest("User is not a student")

    if user.is_approved:
        return {"message": "Student is already approved"}

    user.is_approved = True
    db.commit()

    return {"message": "Student approved successfully"}


def edit_profile(first_name: str = None, last_name: str = None, phone_number: str = None, linked_in_acc: str = None,
                 current_teacher: Teacher = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    """
    Edit teacher profile details.
    """
    if first_name:
        current_teacher.first_name = first_name
    if last_name:
        current_teacher.last_name = last_name
    if phone_number:
        current_teacher.phone_number = phone_number
    if linked_in_acc:
        current_teacher.linked_in_acc = linked_in_acc

    db.commit()
    db.refresh(current_teacher)
    return current_teacher
