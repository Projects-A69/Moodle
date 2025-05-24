from src.models.models import Section
from src.schemas.all_models import SectionInDB, SectionCreate, SectionUpdate
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

def get_all_sections(db: Session):
    section = db.query(Section).all()
    return section

def information_about_section(db: Session, section_id: UUID):
    section = db.query(Section).filter(Section.id == section_id).first()
    return section

def add_section_to_course(db: Session, payload: SectionCreate):
    new_section = Section(**payload.dict())
    db.add(new_section)
    db.commit()
    db.refresh(new_section)
    return new_section

def delete_section_from_course(db: Session, section: Section):
    db.delete(section)
    db.commit()
    return section

def update_info_about_section(db: Session, payload: SectionUpdate):
    section = get_section_by_id(db, payload.section_id)
    if payload.title:
        section.title = payload.title
    if payload.description:
        section.description = payload.description
    if payload.information:
        section.information = payload.information
    if payload.link:
        section.link = payload.link
    db.commit()
    db.refresh(section)
    return section