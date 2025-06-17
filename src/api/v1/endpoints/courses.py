from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_teacher_user, optional_user
from src.crud.course import (
    create_courses,
    get_course,
    get_course_by_id,
    get_courses_by_tag_id,
    rating_course,
    update_specific_course,
)
from src.schemas.all_models import User, CourseWithRatings

router = APIRouter(tags=["courses"])


@router.get("/")
def get_courses(
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_user),
):
    return get_course(db, title=title, current_user=current_user)

@router.get("/courses/{course_id}", response_model=CourseWithRatings)
def get_rating_course(course_id: UUID, db: Session = Depends(get_db)):
    return rating_course(db, course_id)

@router.get("/{course_id}")
def get_courses_by_id(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_teacher_user),
):
    course = get_course_by_id(db, course_id, current_user=current_user)
    return course


@router.post("/")
def create_course(
    title: str = Form(...),
    description: str = Form(...),
    objectives: str = Form(""),
    is_premium: bool = Form(...),
    picture: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_teacher_user),
):
    owner_id = current_user.id
    new_courses = create_courses(
        db,
        title,
        description,
        objectives,
        is_premium,
        owner_id,
        picture,
    )
    return new_courses


@router.put("/{course_id}")
def update_course(
    course_id: UUID,
    title: str = Form(None),
    description: str = Form(None),
    objectives: str = Form(None),
    is_premium: bool = Form(None),
    picture: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_teacher_user),
):
    return update_specific_course(
        db=db,
        id=course_id,
        current_user=current_user,
        title=title,
        description=description,
        objectives=objectives,
        is_premium=is_premium,
        picture=picture,
    )


@router.get("/by-tag/{tag_id}")
def get_courses_by_tag(
    tag_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_user),
):
    return get_courses_by_tag_id(db, tag_id, current_user)
