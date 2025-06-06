from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.models import Course, Role, StudentCourse, User
from src.schemas.all_models import CoursesUpdate


def get_course(db: Session, title: str, current_user: Optional[User] = None):
    read_courses = db.query(Course)
    if title:
        read_courses = read_courses.filter(Course.title.ilike(f"%{title}%"))

    if current_user is None:
        read_courses = read_courses.filter(Course.is_hidden is False)
        return [
            {"id": course.id, "title": course.title, "description": course.description}
            for course in read_courses.all()
        ]
    if current_user.role == Role.STUDENT:
        read_courses = read_courses.filter(Course.is_hidden is False)

        approved_student = (
            db.query(Course)
            .join(StudentCourse)
            .filter(
                StudentCourse.student_id == current_user.id,
                StudentCourse.is_approved is True,
            )
            .all()
        )

        approved_courses = [course.id for course in approved_student]

        result = []
        for course in read_courses.all():
            if not course.is_premium or course.id in approved_courses:
                result.append(
                    {
                        "id": course.id,
                        "title": course.title,
                        "description": course.description,
                        "objectives": course.objectives,
                        "picture": course.picture,
                        "rating": course.rating,
                    }
                )
            else:
                result.append(
                    {
                        "title": course.title,
                        "description": course.description,
                        "picture": course.picture,
                    }
                )
        return result
    if current_user.role == Role.TEACHER:
        courses = []
        for course in read_courses.all():
            if course.owner_id == current_user.id:
                courses.append(course)
            if not course.is_hidden:
                courses.append(
                    {"title": course.title, "description": course.description}
                )
        return courses
    return read_courses.all()


def get_course_by_id(db: Session, id: UUID, current_user: Optional[User] = None):
    course = db.query(Course).filter(Course.id == id).first()
    if not course:
        raise HTTPException(status_code=403, detail="Course not found")
    if current_user is None:
        if course.is_hidden or course.is_premium:
            raise HTTPException(status_code=403, detail="Access denied")
    if current_user.role == Role.STUDENT:
        if course.is_hidden:
            raise HTTPException(status_code=403, detail="This course is hidden")
        if course.is_premium:
            enrolled_premium = (
                db.query(StudentCourse)
                .filter(
                    StudentCourse.student_id == current_user.id,
                    StudentCourse.course_id == course.id,
                )
                .first()
            )
            if not enrolled_premium:
                raise HTTPException(
                    status_code=403,
                    detail="You do not have enrolled in this premium course",
                )
    elif current_user.role == Role.TEACHER:
        if course.is_hidden or course.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    return course


def create_courses(
    db: Session,
    title: str,
    description: str,
    objectives: str,
    picture: str,
    is_premium: bool,
    owner_id: UUID,
):
    existing_title = db.query(Course).filter(Course.title == title).first()
    if existing_title:
        raise HTTPException(status_code=400, detail="Title already exists")
    new_course = Course(
        title=title,
        description=description,
        objectives=objectives,
        picture=picture,
        is_premium=is_premium,
        owner_id=owner_id,
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


def update_specific_course(
    db: Session, id: UUID, payload: CoursesUpdate, current_user: Optional[User] = None
):
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    course = get_course_by_id(db, id)

    if course.owner_id == current_user.id or current_user.role == Role.ADMIN:
        if payload.title is not None:
            existing = (
                db.query(Course)
                .filter(Course.title == payload.title, Course.id != id)
                .first()
            )
            if existing:
                raise HTTPException(status_code=400, detail="Course already exists")
            course.title = payload.title
        if payload.description is not None:
            course.description = payload.description
        if payload.objectives is not None:
            course.objectives = payload.objectives
        if payload.picture is not None:
            course.picture = payload.picture
        if payload.is_premium is not None:
            course.is_premium = payload.is_premium
        db.commit()
        db.refresh(course)
        return course
    else:
        raise HTTPException(
            status_code=403, detail="You dont have permission to edit this course"
        )


def rating_course(db: Session, id: UUID):
    course = db.query(Course).filter(Course.id == id).first()
    if not course:
        raise HTTPException(status_code=403, detail="Course not found")
    ratings = (
        db.query(StudentCourse)
        .filter(StudentCourse.course_id == course.id, StudentCourse.score is not None)
        .all()
    )
    if not ratings:
        average_rating_score = 0.0
    else:
        total_score = sum(rating.score for rating in ratings)
        max_score = len(ratings) * 10
        avg_rating = total_score / max_score
        average_rating_score = avg_rating * 10
    course.rating = average_rating_score
    db.commit()
    db.refresh(course)
    return {"title": course.title, "rating": average_rating_score}
