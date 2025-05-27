from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.models.models import Course, Student, Section, Role,StudentCourse
from src.schemas.all_models import CoursesRate
from uuid import UUID
from src.crud.user import get_by_id
from src.utils.custom_responses import NotFound, BadRequest
from src.utils.email_utils import send_email
from src.utils.token_utils import generate_student_approval_token
from src.core.config import settings

def list_accessible_courses(current_student: Student = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """
    Lists all public courses and premium courses the student is subscribed to.
    """
    public_courses = db.query(Course).filter(Course.is_premium == False).all()
    subscribed_courses = current_student.courses

    return {
        "public_courses": public_courses,
        "subscribed_courses": subscribed_courses
    }


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

    # if course in current_student.courses:
    #     raise BadRequest("Already subscribed to this course")

    if current_student.is_approved:
        current_student.courses.append(course)
        db.commit()
        return {"message": "Successfully subscribed to the course."}

    token = generate_student_approval_token(str(current_student.id))
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


def unsubscribe_from_course(
    course_id: UUID,
    current_student: Student = Depends(get_current_user),
    db: Session = Depends(get_db)):
    """
    Allows a student to unsubscribe from any course.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFound("Course not found")

    if course not in current_student.courses:
        raise BadRequest("You are not subscribed to this course")

    current_student.courses.remove(course)
    db.commit()

    return {"message": f"Unsubscribed from {course.title} successfully."}


def view_course(course_id: UUID,
                current_student: Student = Depends(get_current_user),
                db: Session = Depends(get_db)):
    """
    View a single course if it is public or the student is subscribed.
    """
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise NotFound("Course not found")

    if course.is_premium and course not in current_student.courses:
        raise HTTPException(status_code=403, detail="You are not subscribed to this course")

    return course


def list_sections(course_id: UUID,
                  current_student: Student = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """
    Lists all sections of a course if accessible by the student.
    """
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise NotFound("Course not found")

    if course.is_premium and course not in current_student.courses:
        raise HTTPException(status_code=403, detail="You are not subscribed to this course")

    return {
        "sections": course.sections
    }


def view_section(course_id: UUID,
                 section_id: UUID,
                 current_student: Student = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    """
    View a single section of a course if accessible by the student.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFound("Course not found")

    if course.is_premium and course not in current_student.courses:
        raise HTTPException(status_code=403, detail="You are not subscribed to this course")

    section = db.query(Section).filter(Section.id == section_id, Section.course_id == course_id).first()
    if not section:
        raise NotFound("Section not found")

    return section


def view_profile(current_student: Student = Depends(get_current_user),
                 db: Session = Depends(get_db)):

    student = get_by_id(db, current_student.id)
    return student


def rate_course(course_id: UUID,
                payload: CoursesRate,
                current_student: Student = Depends(get_current_user),
                db: Session = Depends(get_db)):
    """
    Allows a student to rate a course.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_student != Role.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can rate courses")

    if not (1 <= payload.score <= 10):
        raise HTTPException(status_code=400, detail="Score must be between 1 and 10")

    existing_rating = db.query(CoursesRate).filter_by(user_id=current_student.id, course_id=course_id).first()

    if existing_rating:
        existing_rating.score = payload.score
    else:
        new_rating = CoursesRate(id=course_id, user_id=current_student.id, score=payload.score)
        db.add(new_rating)

    db.commit()

    return {"message": "Rating saved successfully"}