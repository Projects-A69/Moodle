from sys import prefix

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="tags", tags=["tags"])

@router.get("/")
def get_tags():
    pass

@router.post("/")
def create_tags():
    pass

@router.delete("/{tag_id}")
def delete_tags():
    pass

@router.post("/courses/{course_id}/tags")
def add_tag_to_course():
    pass

@router.delete("/courses/{course_id}/tags/{tag_id}")
def delete_tag_from_course():
    pass