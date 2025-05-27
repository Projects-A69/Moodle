from src.crud.course import get_course_by_id
from src.models.models import Section, Course, User
from src.schemas.all_models import SectionInDB, SectionCreate, SectionUpdate, CourseInDB, Role
from fastapi import HTTPException
from src.utils.custom_responses import Unauthorized
from sqlalchemy.orm import Session
from uuid import UUID
from src.api.deps import get_db, get_current_user
from typing import Optional

def get_all_sections(db: Session, title: Optional[str] = None):
    section = db.query(Section)
    if title:
        section = section.filter(Section.title.ilike(f'%{title}%'))
    return section.all()

def information_about_section(db: Session, section_id: UUID):
    section = db.query(Section).filter(Section.id == section_id).first()
    return section

def add_section_to_course(db: Session, payload: SectionCreate, course_id: UUID):
    course = get_course_by_id(db, course_id)
    existing_title = db.query(Section).filter(Section.title == payload.title).first()
    if existing_title:
        raise HTTPException(status_code=400, detail='Title already exists')
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
    return {"message": f"Section {payload.title} added to course: {course.title}"}

def delete_section_from_course(db: Session, section: Section):
    if section is None:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(section)
    db.commit()
    return {"message": f"Section {section.title} deleted"}

def update_info_about_section(db: Session, section_id: UUID, payload: SectionUpdate, current_user: Optional[User] = None):
    section = information_about_section(db, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    course = get_course_by_id(db, section.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.owner_id == current_user.id or current_user.role == Role.ADMIN:
        if payload.title is not None:
            section.title = payload.title
        if payload.description is not None:
            section.description = payload.description
        if payload.information is not None:
            section.information = payload.information
        if payload.link is not None:
            section.link = payload.link
        db.commit()
        db.refresh(section)
        return section
    else:
        raise HTTPException(status_code=403, detail="You dont have permission to edit this section")