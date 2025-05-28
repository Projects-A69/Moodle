from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.models.models import Course, Student, Section, Role, StudentCourse, User
from src.schemas.all_models import CoursesRate
from uuid import UUID
from src.crud.user import get_by_id
from src.utils.custom_responses import NotFound, BadRequest
from src.utils.email_utils import send_email
from src.utils.token_utils import generate_student_approval_token
from src.core.config import settings

# def list_accessible_courses(current_user: User = Depends(get_current_user),
#                              db: Session = Depends(get_db)):
#     """
#     Lists all public courses and premium courses the student is subscribed to.
#     """
#
#     student = db.query(Student).options(joinedload(Student.courses))\
#         .filter(Student.id == current_user.student.id)\
#         .first()
#
#     public_courses = db.query(Course).filter(Course.is_premium == False).all()
#     subscribed_courses = student.courses
#
#     return {
#         "public_courses": public_courses,
#         "subscribed_courses": subscribed_courses
#     }


def subscribe_to_course(
    course_id: UUID,
    current_student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)):
    """
    Allows a student to subscribe to a premium course, if the Teacher who owns the Course approves him.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFound("Course not found")

    if not course.is_premium:
        raise BadRequest("No need to subscribe to a public course")

    existing = db.query(StudentCourse).filter_by(
        student_id=current_student.id, course_id=course.id
    ).first()
    if existing:
        if existing.is_approved:
            raise BadRequest("You are already subscribed and approved.")
        else:
            raise BadRequest("Subscription request already sent. Awaiting approval.")

    new_subscription = StudentCourse(
        student_id=current_student.id,
        course_id=course.id,
        is_approved=False
    )
    db.add(new_subscription)
    db.commit()

    token = generate_student_approval_token(str(current_student.id), str(course.id))
    approve_link = f"{settings.APP_BASE_URL}/api/v1/teachers/teachers/approval?token={token}"
    owner = course.owner
    to_email = owner.user.email
    subject = f"Student Subscription Request for {course.title}"
    body = (
        f"Hello {course.owner.first_name},\n\n"
        f"{current_student.student.first_name} {current_student.student.last_name} wants to subscribe to your premium course: {course.title}.\n"
        f"To approve this student and allow access, click the link below:\n\n"
        f"{approve_link}\n\n"
        "Thank you!"
    )

    send_email(to_email, subject, body)

    return {"message": "Approval request sent to the course owner. Awaiting approval."}


def unsubscribe_from_course(student_id: UUID,
                            course_id: UUID,
                            db: Session=Depends(get_db)):
    student_course = db.query(StudentCourse).filter(
        StudentCourse.course_id == course_id,
        StudentCourse.student_id == student_id).first()

    student = db.query(Student).filter(Student.id == student_id).first()
    course = db.query(Course).filter(Course.id == course_id).first()
    if not student_course:
        raise NotFound(f"Student : {student_id} not enrolled in course with ID: {course_id}")

    db.delete(student_course)
    db.commit()

    return {"message": f"{student.first_name} {student.last_name} unsubscribed from {course.title} successfully"}


# def view_course(course_id: UUID,
#                 current_student: Student = Depends(get_current_user),
#                 db: Session = Depends(get_db)):
#     """
#     View a single course if it is public or the student is subscribed.
#     """
#     course = db.query(Course).filter(Course.id == course_id).first()
#
#     if not course:
#         raise NotFound("Course not found")
#
#     if course.is_premium and course not in current_student.courses:
#         raise HTTPException(status_code=403, detail="You are not subscribed to this course")
#
#     return course


# def list_sections(course_id: UUID,
#                   current_student: Student = Depends(get_current_user),
#                   db: Session = Depends(get_db)):
#     """
#     Lists all sections of a course if accessible by the student.
#     """
#     course = db.query(Course).filter(Course.id == course_id).first()
#
#     if not course:
#         raise NotFound("Course not found")
#
#     if course.is_premium and course not in current_student.courses:
#         raise HTTPException(status_code=403, detail="You are not subscribed to this course")
#
#     return {
#         "sections": course.sections
#     }


# def view_section(course_id: UUID,
#                  section_id: UUID,
#                  current_student: Student = Depends(get_current_user),
#                  db: Session = Depends(get_db)):
#     """
#     View a single section of a course if accessible by the student.
#     """
#     course = db.query(Course).filter(Course.id == course_id).first()
#     if not course:
#         raise NotFound("Course not found")
#
#     if course.is_premium and course not in current_student.courses:
#         raise HTTPException(status_code=403, detail="You are not subscribed to this course")
#
#     section = db.query(Section).filter(Section.id == section_id, Section.course_id == course_id).first()
#     if not section:
#         raise NotFound("Section not found")
#
#     return section


def view_profile(current_student: Student = Depends(get_current_user),
                 db: Session = Depends(get_db)):

    student = get_by_id(db, current_student.id)
    return student


def rate_course(course_id: UUID, payload: CoursesRate, current_user: User, db: Session):
    course = db.query(Course).filter_by(id=course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == Role.STUDENT:
        student = db.query(Student).filter_by(id=current_user.id).first()
        if student not in course.students:
            raise HTTPException(status_code=403, detail="You are not enrolled in this course")

    course.rating = payload.rating
    db.commit()
    db.refresh(course)

    return {"message": "Course rating updated successfully", "rating": course.rating}