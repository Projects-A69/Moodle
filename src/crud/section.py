from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.crud.course import get_course_by_id
from src.models.models import Course, Section, StudentCourse, User
from src.schemas.all_models import Role, SectionCreate, SectionUpdate
from src.utils.custom_responses import Unauthorized


def get_all_sections(
    db: Session,
    course_id: UUID,
    title: Optional[str] = None,
    current_user: Optional[User] = None,
):
    get_course_by_id(db, course_id, current_user)
    sections1 = db.query(Section).filter(Section.course_id == course_id)
    if title:
        sections = db.query(Section).filter(Section.title.ilike(f"%{title}%"))
    sections = sections1.all()
    return [
        {"title": section.title, "content": section.content} for section in sections
    ]


def information_about_section(
    db: Session, section_id: UUID, current_user: Optional[User] = None
):
    section = db.query(Section).filter(Section.id == section_id).first()
    get_course_by_id(db, section.course_id, current_user)
    course = section.course
    if not section:
        raise HTTPException(status_code=403, detail="Section not found")
    if current_user.role in [Role.TEACHER, Role.ADMIN]:
        return section
    student_course = (
        db.query(StudentCourse)
        .filter(
            StudentCourse.student_id == current_user.id,
            StudentCourse.course_id == section.course_id,
        )
        .first()
    )
    if not student_course and not course.is_premium:
        student_course = StudentCourse(
            student_id=current_user.id,
            course_id=course.id,
            is_approved=True,
            progress=0,
            is_visited=False,
        )
        db.add(student_course)
        db.commit()
        db.refresh(student_course)
    if course.is_premium:
        if not student_course or not student_course.is_approved:
            raise HTTPException(
                status_code=403, detail="You are not approved for this course!"
            )
    if not student_course.is_visited:
        total_section = (
            db.query(Section).filter(Section.course_id == section.course_id).count()
        )
        if student_course.progress < 100:
            formula_progress = 100 / total_section
            sum_progress = formula_progress + student_course.progress
            if sum_progress > 100:
                student_course.progress = 100
            else:
                student_course.progress = sum_progress
        student_course.is_visited = True
        db.commit()
        db.refresh(student_course)
    return {
        "title": section.title,
        "content": section.content,
        "description": section.description,
        "information": section.information,
        "progress": student_course.progress,
    }


def add_section_to_course(
    db: Session,
    payload: SectionCreate,
    course_id: UUID,
    current_user: Optional[User] = None,
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.owner_id != current_user.id:
        raise Unauthorized("Only owner can create sections")
    existing_title = db.query(Section).filter(Section.title == payload.title).first()
    if existing_title:
        raise HTTPException(status_code=400, detail="Title already exists")
    new_section = Section(
        title=payload.title,
        content=payload.content,
        description=payload.description,
        information=payload.information,
        course_id=course_id,
    )
    db.add(new_section)
    db.commit()
    db.refresh(new_section)
    return {"message": f"Section {payload.title} added to course: {course.title}"}


def delete_section_from_course(
    db: Session, section: Section, current_user: Optional[User] = None
):
    if section is None:
        raise HTTPException(status_code=404, detail="Course not found")
    course = db.query(Course).filter(Course.id == section.course_id).first()
    if course.owner_id != current_user.id and current_user.role != Role.ADMIN:
        raise Unauthorized("Only owner can delete sections")
    db.delete(section)
    db.commit()
    return {"message": f"Section {section.title} deleted"}


def update_info_about_section(
    db: Session,
    section_id: UUID,
    payload: SectionUpdate,
    current_user: Optional[User] = None,
):
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    course = db.query(Course).filter(Course.id == section.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.owner_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=403, detail="You dont have permission to edit this section"
        )
    if payload.title is not None:
        section.title = payload.title
    if payload.content is not None:
        section.content = payload.content
    if payload.description is not None:
        section.description = payload.description
    if payload.information is not None:
        section.information = payload.information
    if payload.link is not None:
        section.link = payload.link
    db.commit()
    db.refresh(section)
    return section
