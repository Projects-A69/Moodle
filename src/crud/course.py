from src.api.deps import get_current_user, get_db
from src.schemas.all_models import CourseInDB, CoursesCreate, CoursesUpdate, CoursesRate, User
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from src.models.models import User, Role, StudentCourse, Course
from typing import Optional

def get_course(db: Session, title: str, current_user: Optional[User] = None):
    read_courses = db.query(Course)
    if title:
        read_courses = read_courses.filter(Course.title.ilike(f"%{title}%"))

    if current_user is None:
        read_courses = read_courses.filter(Course.is_hidden == False)
        return [{
            "title": course.title,
            "description": course.description} for course in read_courses.all()]
    if current_user.role == Role.STUDENT:
        public_course = read_courses.filter(Course.is_hidden == False, Course.is_premium == False).all()
        premium_courses = read_courses.join(StudentCourse).filter(Course.is_hidden == False, Course.is_premium == True, StudentCourse.student_id == current_user.id)
        return public_course.all() + premium_courses.all()
    if current_user.role == Role.TEACHER:
        courses = []
        for course in read_courses.all():
            if course.owner_id == current_user.id:
                courses.append(course)
            elif not course.is_hidden:
                courses.append({"title": course.title, "description": course.description})
        return courses
    return read_courses.all()

def get_course_by_id(db: Session, id: UUID, current_user: Optional[User] = None):
    cousers = db.query(Course).filter(Course.id == id).first()
    if not cousers:
        raise HTTPException(status_code=403, detail="Course not found")
    if current_user is None:
        if course.is_hidden or course.is_premium:
            raise HTTPException(status_code=403, detail="Access denied")
    if current_user.role == Role.STUDENT:
        if course.is_hidden:
            raise HTTPException(status_code=403, detail="This course is hidden")
        if course.is_premium:
            enrolled_premium = db.query(StudentCourse).filterby(student_id == current_user.id, course_id = course.id).first()
            if not enrolled_premium:
                raise HTTPException(status_code=403, detail="You do not have enrolled in this premium course")
    elif current_user.role == Role.TEACHER:
        if course.is_hidden and course.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    return cousers

def create_courses(db: Session, title: str, description: str, objectives: str, picture: str, is_premium: bool, owner_id: UUID):
    existing_title = db.query(Course).filter(Course.title == title).first()
    if existing_title:
        raise HTTPException(status_code=400, detail="Title already exists")
    new_course = Course(title = title, description = description, objectives = objectives, picture= picture, is_premium = is_premium, owner_id= owner_id)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

def update_specific_course(db: Session, id: UUID, payload: CoursesUpdate, current_user: Optional[User] = None):
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    course = get_course_by_id(db, id)

    if course.owner_id == current_user.id or current_user.role == Role.ADMIN:
        if payload.title is not None:
            existing = db.query(Course).filter(Course.title == payload.title, Course.id != id).first()
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
        raise HTTPException(status_code=403, detail="You dont have permission to edit this course")

def rating_course(db: Session, id: UUID, payload: CoursesRate, user: User):
    if payload.score is None:
        raise HTTPException(status_code=404, detail="No score")
    course = get_course_by_id(db, id)
    student = db.query(StudentCourse).filter(StudentCourse.student_id==user.id, course_id = course.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not enrolled in this course")
    student.score = payload.score
    ratings = db.query(StudentCourse).filter(StudentCourse.course_id == course.id, StudentCourse.score != None).all()
    average_rating = sum(r.score for r in ratings) / len(ratings)
    course.rating = average_rating
    db.commit()
    db.refresh(course)
    return {"course_id": course.id, "rating": average_rating}
