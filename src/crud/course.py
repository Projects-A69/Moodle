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
        enrolled_premium = db.query(StudentCourse.course_id).filter(StudentCourse.student_id == current_user.id, StudentCourse.course.has(is_premium=True)).all()
        premium_course = [row.course_id for row in enrolled_premium]
        premium_courses = read_courses.filter(Course.id.in_(premium_course)).all()
        return public_course + premium_courses
    if current_user.role == Role.TEACHER:
        courses = []
        for course in read_courses.all():
            if course.owner_id == current_user.id:
                courses.append(course)
            elif not course.is_hidden:
                courses.append({"title": course.title, "description": course.description})
        return courses
    return read_courses.all()

def get_course_by_id(db: Session, id: UUID):
    cousers = db.query(Course).filter(Course.id == id).first()
    if not cousers:
        raise HTTPException(status_code=404, detail="Course not found")
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
    update_data = payload.dict(exclude_unset=True)
    if course.owner_id == current_user.id or current_user.role == Role.ADMIN:
        if "title" in update_data:
            existing = db.query(Course).filter(Course.title == update_data["title"], Course.id != id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Course already exists")
            course.title = update_data["title"]
        if "description" in update_data:
            course.description = update_data["description"]
        if "objectives" in update_data:
            course.objectives = update_data["objectives"]
        if "picture" in update_data:
            course.picture = update_data["picture"]
        if "is_premium" in update_data:
            course.is_premium = update_data["is_premium"]
        db.commit()
        db.refresh(course)
        return course
    else:
        raise HTTPException(status_code=403, detail="You dont have permission to edit this course")

def rating_course(db: Session, id: UUID, payload: CoursesRate, user: User):
    if user.role != Role.STUDENT:
        raise HTTPException(status_code=403, detail="Only student can rate course")
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
    return {"course_id": course.id, "rating": course_rating}
