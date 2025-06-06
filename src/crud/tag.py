from typing import Optional
from src.models.models import Tag as TagModel, Course
from src.schemas.all_models import CreateTag, User
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID


def get_tags(db: Session):
    tag = db.query(TagModel).all()
    return tag


def get_tag_by_id(db: Session, tag_id: UUID):
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    return tag


def create_tags(db: Session, payload: CreateTag):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Tag name cannot be empty")
    existing_tag = db.query(TagModel).filter(TagModel.name == name).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag already exists")
    tag = TagModel(name=payload.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tags(db: Session, tag_id: UUID):
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.flush()
    db.commit()
    return {"message": f"{tag.name} is deleted"}


def add_tag_to_course(
    db: Session, course_id: UUID, tag_id: UUID, current_user: Optional[User] = None
):
    course = db.query(Course).filter(Course.id == course_id).first()
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    course.tags.append(tag)
    db.commit()
    db.refresh(course)
    return {"message": f"Tag {tag.name} added to {course.title}"}


def delete_tag_from_course(db: Session, course_id: UUID, tag_id: UUID):
    course = db.query(Course).filter(Course.id == course_id).first()
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if tag not in course.tags:
        raise HTTPException(status_code=404, detail="Tag not found")
    course.tags.remove(tag)
    db.commit()
    return {"message": f"Tag {tag.name} removed from {course.title}"}


def search_course_by_tag(db: Session, tag_name: Optional[str]):
    tag = db.query(TagModel).filter(TagModel.name.ilike(f"%{tag_name}%")).first()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return [
        {
            "title": course.title,
            "description": course.description,
            "objectives": course.objectives,
            "premium": course.is_premium,
        }
        for course in tag.courses
    ]
