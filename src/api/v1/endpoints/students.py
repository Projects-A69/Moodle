from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.deps import get_db, get_current_user
from src.models.models import Course, Student

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/courses")
def list_accessible_courses(current_student: Student = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """
    Lists all public courses and premium courses the student is subscribed to.
    """
    public_courses = db.query(Course).filter(Course.is_public == True).all()
    subscribed_courses = current_student.courses

    return {
        "public_courses": public_courses,
        "subscribed_courses": subscribed_courses
    }


@router.post("/courses/{course_id}/subscribe")
def subscribe_to_course(course_id: int,
                        current_student: Student = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    """
    Subscribes the student to a premium course.
    """
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.is_public:
        raise HTTPException(status_code=400, detail="No need to subscribe to a public course")

    if course in current_student.courses:
        raise HTTPException(status_code=400, detail="Already subscribed to this course")

    current_student.courses.append(course)
    db.commit()

    return {"message": f"Successfully subscribed to {course.title}"}


@router.get("/courses/{course_id}")
def view_course(course_id: int,
                current_student: Student = Depends(get_current_user),
                db: Session = Depends(get_db)):
    pass


@router.get("/courses/{course_id}/sections")
def list_sections(course_id: int,
                current_student: Student = Depends(get_current_user),
                db: Session = Depends(get_db)):
    
    course_sections = db.query(Course).filter(Course.sections == True).all()

    return {
        "sections": course_sections,
    }


@router.get("/courses/{course_id}/sections/{section_id}")
def view_section(course_id: int,
                section_id: int,
                current_student: Student = Depends(get_current_user),
                db: Session = Depends(get_db)):
    pass


@router.get("/")
def view_profile(current_student:Student = Depends(get_current_user),
                 db:Session = Depends(get_db)):
    pass


@router.post("/courses/{course_id}")
def subscribe_to_course(course_id: int,
                        current_student: Student = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    pass


@router.post("/courses/{course_id}/rating")
def rate_course():
    pass


@router.post("/")
def register_as_student():
    pass


@router.put("/profile")
def edit_profile():
    pass