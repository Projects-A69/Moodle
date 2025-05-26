from src.api.deps import get_current_user, get_db
from src.schemas.all_models import CourseInDB, CoursesCreate, CoursesUpdate, CoursesRate, User
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from src.models.models import User, Role, StudentCourse, Course

def get_course(db: Session, is_hidden: bool, title: str):
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

def update_specific_course(db: Session, id: UUID, payload: CoursesUpdate):
    course = get_course_by_id(db, id)
    update_data = payload.dict(exclude_unset=True)
    if "title" in update_data:
        course.title = update_data["title"]
    if "description" in update_data:
        course.description = update_data["description"]
    if "objectives" in update_data:
        course.objectives = update_data["objectives"]
    db.commit()
    db.refresh(course)
    return course

def rating_course(db: Session, id: UUID, payload: CoursesRate, user = Depends(get_current_user)):
    if user.role != Role.STUDENT:
        raise HTTPException(status_code=403, detail="Only student can rate course")
    if payload.score is None:
        raise HTTPException(status_code=404, detail="No score")
    course = get_course_by_id(db, id)
    student = db.query(StudentCourse).filter(student_id =user.id, course_id = course.id).first()
    student.score = payload.score
    if not student:
        raise HTTPException(status_code=404, detail="Student not enrolled in this course")
    ratings = db.query(StudentCourse).filter(StudentCourse.course_id == course.id, StudentCourse.score != None).all()
    average_rating = sum(r.score for r in ratings) / len(ratings)
    course_rating = average_rating
    db.commit()
    db.refresh(course)
    return {"course_id": course.id, "rating": course_rating}
