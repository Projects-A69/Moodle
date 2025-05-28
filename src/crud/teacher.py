from fastapi import Depends
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.models.models import Course, Teacher, Role, StudentCourse, User
from src.crud.user import get_by_id
from src.utils.custom_responses import NotFound, Forbidden, BadRequest
from uuid import UUID
from src.utils.token_utils import verify_student_approval_token

# def list_accessible_courses(current_teacher: Teacher = Depends(get_current_user),
#                              db: Session = Depends(get_db)):
#     """
#     Lists all public and premium courses the teacher is owner of.
#     """
#     public_courses = db.query(Course).filter(Course.is_premium == False).all()
#     owned_courses = current_teacher.courses
#
#     return {
#         "public_courses": public_courses,
#         "owned_courses": owned_courses
#     }


# def list_sections(course_id: str,
#                   current_teacher: Teacher = Depends(get_current_user),
#                   db: Session = Depends(get_db)):
#     """
#     List all sections for a course owned by the current teacher.
#     """
#     course = db.query(Course).filter(Course.id == course_id, Course.owner_id == current_teacher.id).first()
#     if not course:
#         raise NotFound("Course not found")
#
#     sections = course.sections
#     return {"sections": sections}
#
#
# def view_profile(current_teacher: Teacher = Depends(get_current_user), db: Session = Depends(get_db)):
#     """
#     View teacher's profile info.
#     """
#     teacher = get_by_id(db, current_teacher.id)
#
#     return teacher
#

# def view_course(course_id: UUID,
#                 current_teacher: Teacher,
#                 db: Session):
#     """
#     View a single course if it is public or the teacher is its owner.
#     """
#     course = db.query(Course).filter(Course.id == course_id).first()
#
#     if not course:
#         raise NotFound("Course not found")
#
#     if course.owner_id != current_teacher.id:
#         raise Forbidden("You can only view your own courses")
#
#     return course


def approve_student_by_token(token: str, db: Session = Depends(get_db)):
    """
    Approves a student's enrollment in a specific course using the token from the teacher's email.
    """
    try:
        data = verify_student_approval_token(token)
        student_id = UUID(data["student_id"])
        course_id = UUID(data["course_id"])
    except Exception:
        raise BadRequest("Invalid or expired approval token.")

    user = get_by_id(db, student_id)
    if not user or user.role != Role.STUDENT:
        raise NotFound("Student not found")

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFound("Course not found")

    enrollment = db.query(StudentCourse).filter_by(
        student_id=student_id, course_id=course_id
    ).first()

    if not enrollment:
        enrollment = StudentCourse(
            student_id=student_id,
            course_id=course_id,
            is_approved=True)
        db.add(enrollment)
    else:
        enrollment.is_approved = True

    db.commit()

    return {"message": f"Student approved and enrolled in '{course.title}'."}


def remove_student_from_course(db: Session,
                               course_id: UUID,
                               student_id: UUID):
    """
    Removes a student from the course.
    """
    student_course = db.query(StudentCourse).filter(StudentCourse.course_id == course_id,
                              StudentCourse.student_id == student_id).first()

    if not student_course:
        raise NotFound(f"Student with ID: {student_id} is not enrolled in course with ID: {course_id}")

    db.delete(student_course)
    db.commit()

    return {"message": f"Student with ID: {student_id} removed from course with ID: {course_id} successfully."}


def approve_student_by_id(db: Session, student_id: UUID, course_id: UUID):
    """
    Approves student enrolling in the course and subscribes them.
    """
    user = get_by_id(db, student_id)

    if not user:
        raise NotFound(f"User with ID: {student_id} not found")

    if user.role != Role.STUDENT:
        raise BadRequest("User is not a student")

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFound("Course not found")

    existing = db.query(StudentCourse).filter_by(
        student_id=student_id, course_id=course_id
    ).first()

    if not existing:
        existing = StudentCourse(
            student_id=student_id,
            course_id=course_id,
            is_approved=True
        )
        db.add(existing)
    else:
        existing.is_approved = True

    db.commit()

    return {"message": f"Student approved and enrolled in '{course.title}'."}




def list_pending_students(db: Session):
    """
    List all pending students in the course.
    """
    users = db.query(User).filter(User.role == Role.STUDENT,
                                           User.is_approved == False).all()

    result = []
    for user in users:
        student = user.student
        result.append({
            "id": str(user.id),
            "email": user.email,
            "first_name": student.first_name if student else None,
            "last_name": student.last_name if student else None,
            "is_active": user.is_active,
            "profile_picture": student.profile_picture if student else None,
            "is_approved": user.is_approved})

    return result


# def edit_profile(first_name: str = None,
#                  last_name: str = None,
#                  phone_number: str = None,
#                  linked_in_acc: str = None,
#                  current_teacher: Teacher = Depends(get_current_user),
#                  db: Session = Depends(get_db)):
#     """
#     Edit teacher profile details.
#     """
#     if first_name:
#         current_teacher.first_name = first_name
#     if last_name:
#         current_teacher.last_name = last_name
#     if phone_number:
#         current_teacher.phone_number = phone_number
#     if linked_in_acc:
#         current_teacher.linked_in_acc = linked_in_acc
#
#     db.commit()
#     db.refresh(current_teacher)
#     return current_teacher