from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_student_user
from src.core.config import settings
from src.models.models import Course, Student, StudentCourse
from src.models.models import User as UserModel
from src.schemas.all_models import CoursesRate
from src.utils.custom_responses import BadRequest, NotFound
from src.utils.email_utils import send_email
from src.utils.token_utils import generate_student_approval_token


def subscribe_to_course(
    course_id: UUID,
    current_student: UserModel = Depends(get_student_user),
    db: Session = Depends(get_db),
):
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
        .filter(
            StudentCourse.student_id == current_student.id,
            Course.is_premium is True,
            StudentCourse.is_approved is True,
        )
        .scalar()
    )
    if premium_courses_count >= 5:
        raise BadRequest("You can only be subscribed up to 5 premium courses")

    existing = (
        db.query(StudentCourse)
        .filter_by(student_id=current_student.id, course_id=course.id)
        .first()
    )
    if existing:
        if existing.is_approved:
            raise BadRequest("You are already subscribed and approved.")
        else:
            raise BadRequest("Subscription request already sent. Awaiting approval.")

    new_subscription = StudentCourse(
        student_id=current_student.id, course_id=course.id, is_approved=False
    )
    db.add(new_subscription)
    db.commit()

    token = generate_student_approval_token(str(current_student.id), str(course.id))
    approve_link = (
        f"{settings.APP_BASE_URL}/api/v1/teachers/teachers/approval?token={token}"
    )
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
    student_id: UUID, course_id: UUID, db: Session = Depends(get_db)
):
    """
    Unsubscribe a student from a course.
    """
    student_course = (
        db.query(StudentCourse)
        .filter(
            StudentCourse.course_id == course_id, StudentCourse.student_id == student_id
        )
        .first()
    )

    student = db.query(Student).filter(Student.id == student_id).first()
    course = db.query(Course).filter(Course.id == course_id).first()
    if not student_course:
        raise NotFound(
            f"Student : {student_id} not enrolled in course with ID: {course_id}"
        )

    db.delete(student_course)
    db.commit()

    return {
        "message": f"{student.first_name} {student.last_name} unsubscribed from {course.title} successfully"
    }


def rate_course(
    db: Session, course_id: UUID, payload: CoursesRate, current_student: UserModel
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    student_course = (
        db.query(StudentCourse)
        .filter(
            StudentCourse.course_id == course_id,
            StudentCourse.student_id == current_student.id,
            StudentCourse.is_approved.is_(True),
        )
        .first()
    )

    if not student_course:
        if course.is_premium:
            raise HTTPException(
                status_code=403, detail="You are not enrolled in this premium course"
            )
        else:
            raise HTTPException(
                status_code=403,
                detail="You cannot rate this public course. Please access it first.",
            )

    if student_course.progress == 0:
        raise HTTPException(
            status_code=403, detail="You must see the course before rating it"
        )

    if not (0 <= payload.score <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")

    student_course.score = payload.score
    db.commit()
    db.refresh(student_course)

    return {"message": "Course rated successfully", "score": student_course.score}


def get_all_favorite_courses(db: Session, current_student: UserModel):
    favorites_course = (
        db.query(StudentCourse)
        .join(Course)
        .filter(
            StudentCourse.student_id == current_student.id,
            StudentCourse.is_favorite is True,
        )
        .all()
    )
    if not favorites_course:
        return {"message": "No favorite courses found."}
    my_courses = []
    for favorite in favorites_course:
        course = favorite.course
        if course.is_premium and not favorite.is_approved:
            my_courses.append(
                {"title": course.title, "description": course.description}
            )
        else:
            my_courses.append(
                {
                    "title": course.title,
                    "description": course.description,
                    "objectives": course.objectives,
                    "picture": course.picture,
                }
            )
    return my_courses


def toggle_favorite_course(
    course_id: UUID,
    current_student: UserModel = Depends(get_student_user),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFound("Course not found")

    student_course = (
        db.query(StudentCourse)
        .filter_by(student_id=current_student.id, course_id=course.id)
        .first()
    )

    if student_course:
        student_course.is_favorite = not student_course.is_favorite
        db.commit()
        return {
            "message": (
                "Course added to favorites."
                if student_course.is_favorite
                else "Course removed from favorites."
            )
        }
    else:
        student_course = StudentCourse(
            student_id=current_student.id,
            course_id=course.id,
            is_favorite=True,
            is_approved=False,
        )
        db.add(student_course)
        db.commit()
        return {"message": "Course added to favorites."}
