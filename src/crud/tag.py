from sys import prefix

from src.crud.course import get_course_by_id
from src.models.models import CourseTag, Tag
from src.schemas.all_models import Tag, CourseTag, CreateTag
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="tags", tags=["tags"])

def get_tags(db: Session):
    tag = db.query(Tag).all()
    return tag

def get_tag_by_id(db: Session, tag_id: int):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    return tag

def create_tags(db: Session, payload: CreateTag):
    tag = Tag(name=payload.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

def delete_tags(db: Session, tag_id: int):
    pass

def add_tag_to_course(db: Session, payload: CourseTag):
    course = get_course_by_id(db, payload.course_id)
    tag = get_tag_by_id(db, payload.tag_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    course.tags.append(tag)
    db.commit()
    db.refresh(course)
    return {"message": f"Tag {tag_id} added to {course.title}"}

def delete_tag_from_course():
    pass