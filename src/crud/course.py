from src.api.deps import get_current_user
from src.models.models import Course
from src.schemas.all_models import CourseInDB, CoursesCreate, CoursesUpdate, CoursesRate, User
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

def get_courses(db: Session, is_hidden: bool):
    read_courses = db.query(Course)
    if is_hidden is not None:
        read_courses = read_courses.filter(Course.is_hidden == is_hidden)
    result = read_courses.all()
    if not result:
        raise HTTPException(status_code=404, detail="No courses")
    return result

def get_course_by_id(db: Session, id: UUID):
    cousers = db.query(Course).filter(Course.id == id).first()
    if not cousers:
        raise HTTPException(status_code=404, detail="Course not found")
    return cousers

def create_courses(db: Session, title: str, description: str, objectives: str, owner_id: UUID):
    existing_title = db.query(Course).filter(Course.title == title).first()
    if existing_title:
        raise HTTPException(status_code=400, detail="Title already exists")
    new_course = Course(title = title, description = description, objectives = objectives, owner_id= owner_id)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

def delete_course(db: Session, course: Course):
    if not course:
        raise HTTPException(status_code=404, detail="Course not found to delete")
    db.delete(course)
    db.commit()
    return course

def update_specific_course(db: Session, id: UUID, payload: CoursesUpdate):
    course = get_course_by_id(db, id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if payload.title:
        course.title = payload.title
    if payload.description:
        course.description = payload.description
    if payload.objectives:
        course.objectives = payload.objectives
    db.commit()
    db.refresh(course)
    return course

# def rating_course(db: Session, id: UUID, payload: CoursesRate, user = Depends(get_current_user)):
#     course = get_course_by_id(db, id)
#     if user.role != Role.STUDENT:
#         raise HTTPException(status_code=403, detail="Only student can rate course")
#     if payload.score is None:
#         raise HTTPException(status_code=404, detail="No score")
#
#     existing_vote = db.query(CoursesRate).filter_by(user_id = user.id, course_id = course.id).first()
#     if existing_vote:
#         existing_vote.rating = payload.score

