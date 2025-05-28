from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.all_models import SectionCreate, SectionUpdate, SectionInDB, User
from src.crud.section import get_all_sections, information_about_section, add_section_to_course, delete_section_from_course, update_info_about_section
from src.api.deps import get_db, get_current_user
from src.models.models import Role, Course
from uuid import UUID

from src.utils.custom_responses import Unauthorized

router = APIRouter(prefix="/sections", tags=["sections"])

@router.get("/sections")
def get_sections(course_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_sections(db, course_id, current_user = current_user)

@router.get("/courses/{section_id}")
def get_section_by_id(section_id: UUID, db: Session = Depends(get_db)):
    section = information_about_section(db, section_id)
    return section

@router.post("/sections")
def add_section(course_id: UUID, payload: SectionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != Role.TEACHER:
        raise HTTPException(status_code=403, detail="Access for teachers only!")
    return add_section_to_course(db, payload, course_id, current_user)

@router.delete("/sections/{section_id}")
def delete_section(section_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != Role.TEACHER:
        raise Unauthorized("Access for owner only!")
    section = information_about_section(db, section_id)
    return delete_section_from_course(db, section, current_user)

@router.put("/sections/{section_id}")
def update_section(section: UUID, payload: SectionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != Role.TEACHER:
        raise Unauthorized("Access for owner only!")
    return update_info_about_section(db, section, payload, current_user)
