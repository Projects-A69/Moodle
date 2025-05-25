from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.models.models import Course, Student, Section, Role
from src.schemas.all_models import CoursesRate, UserUpdate
from uuid import UUID
from src.utils.common import get_by_id
from src.utils.custom_responses import NotFound, BadRequest

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/courses")
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


@router.post("/courses/{course_id}/subscribe")
def subscribe_to_course(course_id: UUID,
                        current_student: Student = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    """
    Subscribes the student to a premium course.
    """
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise NotFound("Course not found")

    if not course.is_premium:
        raise BadRequest("No need to subscribe to a public course")

    if course in current_student.courses:
        raise BadRequest("Already subscribed to this course")

    current_student.courses.append(course)
    db.commit()

    return {"message": f"Successfully subscribed to {course.title}"}


@router.get("/courses/{course_id}")
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




@router.get("/courses/{course_id}/sections")
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


@router.get("/courses/{course_id}/sections/{section_id}")
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


@router.get("/profile")
def view_profile(current_student: Student = Depends(get_current_user), db: Session = Depends(get_db)):

    student = get_by_id(db, current_student.id)
    return student


@router.post("/courses/{course_id}/rating")
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

    if current_student.user.role != Role.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can rate courses")

    existing_rating = db.query(CoursesRate).filter_by(user_id=current_student.id, course_id=course_id).first()

    if existing_rating:
        existing_rating.score = payload.score
    else:
        new_rating = CoursesRate(id=course_id, user_id=current_student.id, score=payload.score)
        db.add(new_rating)

    db.commit()

    return {"message": "Rating saved successfully"}



@router.put("/profile")
def edit_profile(payload: UserUpdate,
                 current_student: Student = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    """
    Update current student's profile fields.
    """
    if payload.password:
        current_student.user.password = payload.password
    if payload.first_name:
        current_student.first_name = payload.first_name
    if payload.last_name:
        current_student.last_name = payload.last_name
    if payload.phone_number:
        current_student.phone_number = payload.phone_number
    if payload.linked_in_acc:
        current_student.linked_in_acc = payload.linked_in_acc
    if payload.profile_picture:
        current_student.profile_picture = payload.profile_picture

    db.commit()
    db.refresh(current_student)

    return current_student


