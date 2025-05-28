from sys import prefix
from src.api import deps
from src.crud import tag as crud_tag
from src.schemas.all_models import Tag, CreateTag, CourseTag
from src.models.models import Role
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user, get_teacher_user
from uuid import UUID
from src.utils.custom_responses import *

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("")
def get_tags(db: Session = Depends(get_db)):
    return crud_tag.get_tags(db)

@router.post("")
def create_tags(payload: CreateTag, db: Session = Depends(get_db), current_user = Depends(get_teacher_user)):
    return crud_tag.create_tags(db, payload)

@router.delete("/{tag_id}")
def delete_tags(tag_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_teacher_user)):
    return crud_tag.delete_tags(db, tag_id)

@router.post("/courses/{course_id}/tags")
def add_tag_to_course(course_id: UUID, tag_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_teacher_user)):
    return crud_tag.add_tag_to_course(db, course_id, tag_id)

@router.delete("/courses/{course_id}/tags/{tag_id}")
def delete_tag_from_course(course_id: UUID, tag_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_teacher_user)):
    return crud_tag.delete_tag_from_course(db, course_id, tag_id)

@router.get("/courses/{course_id}/tags")
def found_course_tags(tag_name: str, db: Session = Depends(get_db), current_user = Depends(get_teacher_user)):
    return crud_tag.search_course_by_tag(db, tag_name)