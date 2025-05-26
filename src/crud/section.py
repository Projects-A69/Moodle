from src.crud.course import get_course_by_id
from src.models.models import Section, Course
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

def add_section_to_course(db: Session, payload: SectionCreate, course_id: UUID):
    course = get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    new_section = Section(title = payload.title,
                          content=payload.content,
                          description = payload.description,
                          information=payload.information,
                          course_id=course_id)
    db.add(new_section)
    db.commit()
    db.refresh(new_section)
    return {"message": f"Section {payload.title} added to {course_id}"}

def delete_section_from_course(db: Session, section: Section):
    db.delete(section)
    db.commit()
    return section

def update_info_about_section(db: Session, payload: SectionUpdate):
    section = information_about_section(db, payload.section_id)
    update_data = payload.dict(exclude_unset=True)
    if "title" in update_data:
        section.title = update_data["title"]
    if "description" in update_data:
        section.description = update_data["description"]
    if "information" in update_data:
        section.information = update_data["information"]
    if "link" in update_data:
        section.link = update_data["link"]
    db.commit()
    db.refresh(section)
    return section