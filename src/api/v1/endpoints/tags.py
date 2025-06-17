from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_db, teacher_or_admin
from src.crud import tag as crud_tag
from src.schemas.all_models import CreateTag

router = APIRouter(tags=["tags"])


@router.get("")
def get_tags(db: Session = Depends(get_db)):
    return crud_tag.get_tags(db)


@router.post("")
def create_tags(
    payload: CreateTag,
    db: Session = Depends(get_db),
    current_user=Depends(teacher_or_admin),
):
    return crud_tag.create_tags(db, payload)


@router.delete("/{tag_id}")
def delete_tags(
    tag_id: UUID, db: Session = Depends(get_db), current_user=Depends(teacher_or_admin)
):
    return crud_tag.delete_tags(db, tag_id)


@router.post("/courses/{course_id}/tags")
def add_tag_to_course(
    course_id: UUID,
    tag_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(teacher_or_admin),
):
    return crud_tag.add_tag_to_course(db, course_id, tag_id)


@router.delete("/courses/{course_id}/tags/{tag_id}")
def delete_tag_from_course(
    course_id: UUID,
    tag_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(teacher_or_admin),
):
    return crud_tag.delete_tag_from_course(db, course_id, tag_id)


@router.get("/courses")
def found_course_tags(
    tag_name: str, db: Session = Depends(get_db), current_user=Depends(teacher_or_admin)
):
    return crud_tag.search_course_by_tag(db, tag_name)


@router.get("/map")
def return_course_tag(
    db: Session = Depends(get_db), current_user=Depends(teacher_or_admin)
):
    return crud_tag.return_all_tags(db)
