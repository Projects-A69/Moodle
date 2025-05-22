from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("/")
def get_courses():
    pass

@router.post("/{course_id}")
def get_courses_by_id():
    pass

@router.post("/courses")
def create_course():
    pass

@router.post("/{course_id}")
def update_course():
    pass

@router.delete("/")
def delete_course():
    pass

@router.post("/{course_id}/subscribe")
def subcribe_to_course():
    pass

@router.delete("/{course_id}/unsubscribe")
def unsubcribe_to_course():
    pass

@router.get("rating/{course_id}")
def get_rating_course():
    pass


