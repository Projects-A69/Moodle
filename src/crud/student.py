from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.api.deps import get_db, get_student_user
from src.models.models import Course, Student, Role, StudentCourse, User
from src.schemas.all_models import CoursesRate
from uuid import UUID
from src.utils.custom_responses import NotFound, BadRequest
from src.utils.email_utils import send_email
from src.utils.token_utils import generate_student_approval_token
from src.core.config import settings
from src.models.models import User as UserModel

def subscribe_to_course(course_id: UUID,
                        current_student: UserModel = Depends(get_student_user),
                        db: Session = Depends(get_db)):
    """
    Allows a student to subscribe to a premium course when the Teacher who owns the Course approves him.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFound("Course not found")

    if not course.is_premium:
        raise BadRequest("No need to subscribe to a public course")

    premium_courses_count = (
        db.query(func.count(StudentCourse.course_id))
        .join(Course, StudentCourse.course_id == Course.id)
        .filter
        (StudentCourse.student_id == current_student.id,
                  Course.is_premium == True,
                  StudentCourse.is_approved == True).scalar())
    if premium_courses_count >=5:
        raise BadRequest("You can only be subscribed up to 5 premium courses")

    existing = db.query(StudentCourse).filter_by(student_id=current_student.id, course_id=course.id).first()
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
    """
    Unsubscribe a student from a course.
    """
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


def rate_course(course_id: UUID,
                payload: CoursesRate,
                current_user: User,
                db: Session):
    """
    Allows a student to rate a course.
    """
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