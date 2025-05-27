from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.all_models import SectionCreate, SectionUpdate, SectionInDB
from src.crud.section import get_all_sections, information_about_section, add_section_to_course, delete_section_from_course, update_info_about_section
from src.api.deps import get_db, get_current_user
from src.models.models import Role
from uuid import UUID
router = APIRouter(prefix="/sections", tags=["sections"])

@router.get("/")
def get_sections(db: Session = Depends(get_db)):
    return get_all_sections(db)

@router.get("/{section_id}")
def get_section_by_id(section_id: UUID, db: Session = Depends(get_db)):
    section = information_about_section(db, section_id)
    return section

@router.post("/")
def add_section(course_id: UUID, payload: SectionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        raise Unauthorized("Access for teacher only!")
    section = add_section_to_course(db, payload, course_id)
    return section

@router.delete("/{section_id}")
def delete_section(section_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        raise Unauthorized("Access for teacher only!")
    section = information_about_section(db, section_id)
    return delete_section_from_course(db, section)

@router.put("/{section_id}")
def update_section(section: UUID, payload: SectionUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        raise Unauthorized("Access for teacher only!")
    return update_info_about_section(db, section, payload, current_user = current_user)
