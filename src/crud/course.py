from typing import Optional
from uuid import UUID

from fastapi import File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.models.models import Course, Role, StudentCourse, User
from src.models.models import Tag as TagModel
from src.utils.s3 import upload_image_to_s3


def get_course(db: Session, title: str, current_user: Optional[User] = None):
    read_courses = db.query(Course)
    if title:
        read_courses = read_courses.filter(Course.title.ilike(f"%{title}%"))

    if current_user is None:
        return [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "objectives": course.objectives,
                "picture": course.picture,
                "rating": course.rating,
                "is_premium": course.is_premium,
                "owner_id": course.owner_id,
            }
            for course in read_courses.filter(Course.is_hidden == False).all()  # noqa: E712
        ]

    if current_user.role == Role.STUDENT:
        read_courses = read_courses.filter(Course.is_hidden == False)  # noqa: E712

        approved_student = (
            db.query(Course)
            .join(StudentCourse)
            .filter(
                StudentCourse.student_id == current_user.id,
                StudentCourse.is_approved == True,  # noqa: E712
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
                        "is_premium": course.is_premium,
                        "owner_id": course.owner_id,
                    }
                )
            else:
                result.append(
                    {
                        "title": course.title,
                        "description": course.description,
                        "objectives": course.objectives,
                        "picture": course.picture,
                        "is_premium": course.is_premium,
                        "owner_id": course.owner_id,
                    }
                )
        return result

    if current_user.role == Role.TEACHER:
        result = []
        for course in read_courses.all():
            if course.owner_id == current_user.id:
                result.append(
                    {
                        "id": course.id,
                        "title": course.title,
                        "description": course.description,
                        "objectives": course.objectives,
                        "picture": course.picture,
                        "rating": course.rating,
                        "is_premium": course.is_premium,
                        "owner_id": course.owner_id,
                    }
                )
            elif not course.is_hidden:
                result.append(
                    {
                        "id": course.id,
                        "title": course.title,
                        "description": course.description,
                        "objectives": course.objectives,
                        "picture": course.picture,
                        "rating": course.rating,
                        "is_premium": course.is_premium,
                        "owner_id": course.owner_id,
                    }
                )
        return result
    if current_user.role == Role.ADMIN:
        return [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "objectives": course.objectives,
                "picture": course.picture,
                "rating": course.rating,
                "is_premium": course.is_premium,
                "owner_id": course.owner_id,
            }
            for course in read_courses.all()
        ]

    return []

def get_course_by_id(db: Session, id: UUID, current_user: Optional[User] = None):
    course = db.query(Course).filter(Course.id == id).first()
    if not course:
        raise HTTPException(status_code=403, detail="Course not found")
    if current_user is None:
        if course.is_hidden or course.is_premium:
            raise HTTPException(status_code=403, detail="Access denied")
        return course
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
    if current_user.role == Role.TEACHER:
        if course.is_hidden or course.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        return course
    return course


def create_courses(
    db: Session,

    title: str,
    description: str,
    objectives: str,
    is_premium: bool,
    owner_id: UUID,
    picture: UploadFile = File(None)
):
    if picture:
        picture_path = upload_image_to_s3(picture)
    else:
        picture_path = None

    existing_title = db.query(Course).filter(Course.title == title).first()
    if existing_title:
        raise HTTPException(status_code=400, detail="Title already exists")
    new_course = Course(
        title=title,
        description=description,
        objectives=objectives,
        picture=picture_path,
        is_premium=is_premium,
        owner_id=owner_id,
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


def update_specific_course(
    db: Session,
    id: UUID,
    current_user: Optional[User] = None,
    title: str = None,
    description: str = None,
    objectives: str = None,
    is_premium: bool = None,
    picture: UploadFile = None,
):
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    course = get_course_by_id(db, id, current_user=current_user)

    if course.owner_id == current_user.id or current_user.role == Role.ADMIN:
        if title is not None:
            existing = (
                db.query(Course).filter(Course.title == title, Course.id != id).first()
            )
            if existing:
                raise HTTPException(status_code=400, detail="Course already exists")
            course.title = title
        if description is not None:
            course.description = description
        if objectives is not None:
            course.objectives = objectives
        if is_premium is not None:
            course.is_premium = is_premium
        if picture:
            course.picture = upload_image_to_s3(picture)
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


def get_courses_by_tag_id(
    db: Session, tag_id: UUID, current_user: Optional[User] = None
):
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    courses = tag.courses
    result = []

    for course in courses:
        if current_user is None:
            if course.is_hidden is False:
                result.append(course)
        elif current_user.role == Role.STUDENT:
            if not course.is_hidden and (
                not course.is_premium
                or any(c.id == course.id for c in current_user.student.courses)
            ):
                result.append(course)
        elif current_user.role == Role.TEACHER:
            if course.owner_id == current_user.id or not course.is_hidden:
                result.append(course)
        elif current_user.role == Role.ADMIN:
            result.append(course)

    return [
        {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "objectives": course.objectives,
            "picture": course.picture,
            "rating": course.rating,
            "is_premium": course.is_premium,
            "owner_id": course.owner_id,
        }
        for course in result
    ]
