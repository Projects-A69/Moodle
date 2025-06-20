from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.crud.user import get_by_id
from src.models.models import Course, Role, StudentCourse, User
from src.utils.custom_responses import BadRequest, NotFound, Unauthorized
from src.utils.token_utils import verify_student_approval_token


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

    enrollment = (
        db.query(StudentCourse)
        .filter_by(student_id=student_id, course_id=course_id)
        .first()
    )

    if not enrollment:
        enrollment = StudentCourse(
            student_id=student_id, course_id=course_id, is_approved=True
        )
        db.add(enrollment)
    else:
        enrollment.is_approved = True

    db.commit()

    return {"message": f"Student approved and enrolled in '{course.title}'."}


def remove_student_from_course(db: Session, course_id: UUID, student_id: UUID):
    """
    Removes a student from the course.
    """
    student_course = (
        db.query(StudentCourse)
        .filter(
            StudentCourse.course_id == course_id, StudentCourse.student_id == student_id
        )
        .first()
    )

    if not student_course:
        raise NotFound(
            f"Student with ID: {student_id} is not enrolled in course with ID: {course_id}"
        )

    db.delete(student_course)
    db.commit()

    return {
        "message": f"Student with ID: {student_id} removed from course with ID: {course_id} successfully."
    }


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

    existing = (
        db.query(StudentCourse)
        .filter_by(student_id=student_id, course_id=course_id)
        .first()
    )

    if not existing:
        existing = StudentCourse(
            student_id=student_id, course_id=course_id, is_approved=True
        )
        db.add(existing)
    else:
        existing.is_approved = True

    db.commit()

    return {"message": f"Student approved and enrolled in '{course.title}'."}


def list_pending_students(db: Session, current_teacher: User, course_id: UUID):
    """
    List all pending students in the course.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFound("Course not found.")

    if course.owner_id != current_teacher.id:
        raise Unauthorized("You do not have permission to view this course's students.")

    pending_students = (
        db.query(StudentCourse)
        .filter(
            StudentCourse.course_id == course_id, StudentCourse.is_approved.is_(False)
        )
        .all()
    )
    result = []
    for sc in pending_students:
        student = sc.student
        result.append(
            {
                "id": str(student.id),
                "email": student.user.email if student.user else None,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "profile_picture": student.profile_picture,
            }
        )

    return result


def toggle_course_visibility_by_teacher(
    db: Session, course_id: UUID, current_user: User
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise NotFound(f"Course with ID: {course_id} not found")

    if course.owner_id != current_user.id:
        raise Unauthorized("You are not the owner of this course.")
    print(f"[DEBUG] current_user.id: {current_user.id}")
    print(f"[DEBUG] course.owner_id: {course.owner_id}")
    print(f"[DEBUG] course.students = {course.students}")

    if course.is_hidden:
        course.is_hidden = False
        db.commit()
        return {
            "message": f"Course '{course.title}' is now visible.",
            "is_locked": False,
        }

    if course.students:
        raise BadRequest("You cannot hide a course that has enrolled students.")

    course.is_hidden = True
    db.commit()
    return {
        "message": f"Course '{course.title}' has been hidden successfully.",
        "is_locked": True,
    }
