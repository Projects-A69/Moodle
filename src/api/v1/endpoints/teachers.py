from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.models.models import Course, Teacher

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("/courses")
def list_accessible_courses(current_teacher: Teacher = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """
    Lists all public and premium courses the teacher is owner of.
    """
    public_courses = db.query(Course).filter(Course.is_public == True).all()
    owned_courses = current_teacher.courses

    return {
        "public_courses": public_courses,
        "owned_courses": owned_courses
    }


@router.get("/courses/{course_id}")
def view_course_details():
    pass


@router.get("/courses/{course_id}/sections")
def list_sections():
    pass


@router.get("/")
def view_profile(current_teacher:Teacher = Depends(get_current_user),
                 db:Session = Depends(get_db)):
    pass


@router.post("/courses")
def create_course():
    pass


@router.post("/courses/{course_id}/sections")
def create_section():
    pass


@router.post("/")
def register_as_teacher(): # Awaiting approval
    pass


@router.put("/courses/{course_id}")
def edit_course():
    pass


@router.put("/courses/{course_id}/sections")
def edit_sections():
    pass


@router.put("/")
def edit_profile():
    pass


