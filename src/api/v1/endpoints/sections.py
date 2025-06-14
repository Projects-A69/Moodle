from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from src.schemas.all_models import SectionCreate, SectionUpdate, User
from src.crud.section import (
    get_all_sections,
    information_about_section,
    add_section_to_course,
    delete_section_from_course,
    update_info_about_section,
    leave_section,
    mark_as_completed
)
from src.api.deps import get_db, get_teacher_user, get_student_user, optional_user
from uuid import UUID


router = APIRouter(tags=["sections"])


@router.get("/")
def get_sections(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(optional_user),
):
    return get_all_sections(db, course_id, current_user=current_user)


@router.get("/{section_id}")
def get_section_by_id(
    section_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(optional_user),
):
    section = information_about_section(db, section_id, current_user)
    return section

@router.post("/{section_id}/complete")
def complete_section(section_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(optional_user)):
    return mark_as_completed(db, section_id, current_user)


@router.post("/courses/{course_id}/sections")
def add_section(
    course_id: UUID,
    payload: SectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user),
):
    return add_section_to_course(db, payload, course_id, current_user)


@router.delete("/{section_id}")
def delete_section(
    section_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_teacher_user),
):
    section = information_about_section(db, section_id, current_user)
    return delete_section_from_course(db, section, current_user)


@router.put("/{section_id}")
def update_section(
    payload: SectionUpdate,
    section: UUID = Path(..., alias="section_id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user),
):
    return update_info_about_section(db, section, payload, current_user)

@router.post("/{section_id}/leave")
def leave_section_end(section_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_student_user)):
    return leave_section(db, section_id, current_user)
