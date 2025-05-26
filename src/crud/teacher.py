from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.models.models import Course, Teacher, Student
from src.crud.user import get_by_id
from src.utils.custom_responses import NotFound, Forbidden, BadRequest
from uuid import UUID


def list_accessible_courses(current_teacher: Teacher = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """
    Lists all public and premium courses the teacher is owner of.
    """
    public_courses = db.query(Course).filter(Course.is_premium == False).all()
    owned_courses = current_teacher.courses

    return {
        "public_courses": public_courses,
        "owned_courses": owned_courses
    }


def list_sections(course_id: str,
                  current_teacher: Teacher = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """
    List all sections for a course owned by the current teacher.
    """
    course = db.query(Course).filter(Course.id == course_id, Course.owner_id == current_teacher.id).first()
    if not course:
        raise NotFound("Course not found")

    sections = course.sections
    return {"sections": sections}


def view_profile(current_teacher: Teacher = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    View teacher's profile info.
    """
    teacher = get_by_id(db, current_teacher.id)

    return teacher


def view_course(course_id: UUID, current_teacher: Teacher, db: Session):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise NotFound("Course not found")

    if course.owner_id != current_teacher.id:
        raise Forbidden("You can only view your own courses")

    return course


# def create_course(title: str, description: str, objectives: str,
#                   current_teacher: Teacher = Depends(get_current_user),
#                   db: Session = Depends(get_db)):
#     """
#     Create a new course owned by the current teacher.
#     """
#     existing = db.query(Course).filter(Course.title == title).first()
#     if existing:
#         raise BadRequest("Course title already exists")
#
#     new_course = Course(
#         title=title,
#         description=description,
#         objectives=objectives,
#         owner_id=current_teacher.id
#     )
#     db.add(new_course)
#     db.commit()
#     db.refresh(new_course)
#
#     return new_course


# def create_section(course_id: str, title: str, content: str = None, description: str = None,
#                    current_teacher: Teacher = Depends(get_current_user),
#                    db: Session = Depends(get_db)):
#     """
#     Create a new section in a course owned by the teacher.
#     """
#     course = db.query(Course).filter(Course.id == course_id, Course.owner_id == current_teacher.id).first()
#     if not course:
#         raise NotFound("Course not found")
#
#     if course.owner_id != current_teacher.id:
#         raise BadRequest("You do not own this course")
#
#     new_section = Section(
#         title=title,
#         content=content,
#         description=description,
#         course_id=course_id
#     )
#     db.add(new_section)
#     db.commit()
#     db.refresh(new_section)
#
#     return new_section



def register_as_teacher(first_name: str, last_name: str, phone_number: str = None, linked_in_acc: str = None,
                        current_user = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    """
    Register current user as a teacher (awaiting approval).
    """
    existing_teacher = db.query(Teacher).filter(Teacher.id == current_user.id).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="Already registered as teacher")

    new_teacher = Teacher(
        id=current_user.id,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        linked_in_acc=linked_in_acc
    )
    db.add(new_teacher)
    current_user.role = 'TEACHER'
    current_user.is_approved = False
    db.commit()
    db.refresh(new_teacher)

    return {"message": "Teacher registration submitted, awaiting approval."}


# def edit_course(course_id: str, title: str = None, description: str = None, objectives: str = None,
#                 current_teacher: Teacher = Depends(get_current_user),
#                 db: Session = Depends(get_db)):
#     """
#     Edit course details for a course owned by the current teacher.
#     """
#     course = db.query(Course).filter(Course.id == course_id, Course.owner_id == current_teacher.id).first()
#     if not course:
#         raise NotFound("Course not found")
#
#     if course.owner_id != current_teacher.id:
#         raise BadRequest("You do not own this course")
#
#     if title:
#         course.title = title
#     if description:
#         course.description = description
#     if objectives:
#         course.objectives = objectives
#
#     db.commit()
#     db.refresh(course)
#     return course


# def edit_section(course_id: str, section_id: str, title: str = None, content: str = None, description: str = None,
#                  current_teacher: Teacher = Depends(get_current_user),
#                  db: Session = Depends(get_db)):
#     """
#     Edit a section of a course owned by the teacher.
#     """
#     course = db.query(Course).filter(Course.id == course_id, Course.owner_id == current_teacher.id).first()
#     if not course:
#         raise NotFound("Course not found")
#
#     if course.owner_id != current_teacher.id:
#         raise BadRequest("You do not own this course")
#
#     section = db.query(Section).filter(Section.id == section_id, Section.course_id == course_id).first()
#     if not section:
#         raise NotFound("Section not found")
#
#     if title:
#         section.title = title
#     if content:
#         section.content = content
#     if description:
#         section.description = description
#
#     db.commit()
#     db.refresh(section)
#     return section


def edit_profile(first_name: str = None, last_name: str = None, phone_number: str = None, linked_in_acc: str = None,
                 current_teacher: Teacher = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    """
    Edit teacher profile details.
    """
    if first_name:
        current_teacher.first_name = first_name
    if last_name:
        current_teacher.last_name = last_name
    if phone_number:
        current_teacher.phone_number = phone_number
    if linked_in_acc:
        current_teacher.linked_in_acc = linked_in_acc

    db.commit()
    db.refresh(current_teacher)
    return current_teacher


def approve_student_subscription(student_id: UUID, course_id: UUID,
                                 current_teacher: Teacher = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise NotFound("Student not found")

    course = db.query(Course).filter(Course.id == course_id, Course.owner_id == current_teacher.id).first()
    if not course:
        raise NotFound("Course not found or you do not own it")

    if course in student.courses:
        raise BadRequest("Student already subscribed to this course")

    if not student.user.is_approved:
        raise BadRequest("Student's user account is not approved")

    student.courses.append(course)
    db.commit()

    return {"message": f"Student {student_id} successfully subscribed to course {course_id}"}

