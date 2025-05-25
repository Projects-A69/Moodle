from sys import prefix

from src.crud.course import get_course_by_id
from src.models.models import Tag as TagModel
from src.schemas.all_models import Tag, CourseTag, CreateTag
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

def get_tags(db: Session):
    tag = db.query(TagModel).all()
    return tag

def get_tag_by_id(db: Session, tag_id: UUID):
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    return tag

def create_tags(db: Session, payload: CreateTag):
    tag = TagModel(name=payload.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

def delete_tags(db: Session, tag_id: UUID):
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    db.delete(tag)
    db.commit()
    return {"message": f"{tag_id} is deleted"}

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
    return {"message": f"Tag {payload.tag_id} added to {course.title}"}

def delete_tag_from_course(db: Session, course_id: UUID, tag_id: UUID):
    course = get_course_by_id(db, course_id)
    tag = get_tag_by_id(db, tag_id)
    if tag not in course.tags:
        raise HTTPException(status_code=404, detail="Tag not found")
    course.tags.remove(tag)
    db.commit()
    return {"message": f"Tag {tag.id} removed from {course.title}"}