from uuid import UUID

from sqlalchemy.orm import Session

from src.crud.user import get_by_id
from src.models.models import Admin, Course, Role, Student, StudentCourse, Teacher, User
from src.utils.custom_responses import BadRequest, NotFound
from src.utils.email_utils import send_email


def list_all_users(db: Session, role: str = None, search: str = None) -> list[User]:
    if role and role.upper() not in ["ADMIN", "TEACHER", "STUDENT"]:
        raise BadRequest("Invalid role. Must be one of: ADMIN, TEACHER, STUDENT.")

    if role and search:
        users = (
            db.query(User)
            .filter(User.role == Role(role.upper()), User.email.ilike(f"%{search}%"))
            .all()
        )
    elif role:
        users = db.query(User).filter(User.role == Role(role.upper())).all()
    elif search:
        users = db.query(User).filter(User.email.ilike(f"%{search}%")).all()
    else:
        users = db.query(User).all()

    result = []

    for user in users:
        user_info = {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
        }

        if user.role == Role.ADMIN:
            admin = db.query(Admin).filter(Admin.id == user.id).first()
            if admin:
                user_info.update(
                    {"first_name": admin.first_name, "last_name": admin.last_name}
                )

        elif user.role == Role.TEACHER:
            teacher = db.query(Teacher).filter(Teacher.id == user.id).first()
            if teacher:
                user_info.update(
                    {
                        "first_name": teacher.first_name,
                        "last_name": teacher.last_name,
                        "phone_number": teacher.phone_number,
                        "linked_in_acc": teacher.linked_in_acc,
                        "profile_picture": teacher.profile_picture,
                    }
                )

        elif user.role == Role.STUDENT:
            student = db.query(Student).filter(Student.id == user.id).first()
            if student:
                user_info.update(
                    {
                        "first_name": student.first_name,
                        "last_name": student.last_name,
                        "profile_picture": student.profile_picture,
                    }
                )

        result.append(user_info)

    return result


def update_user_active(db: Session, user_id: UUID):
    user = get_by_id(db, user_id)

    user.is_active = not user.is_active

    db.commit()

    status = "activated" if user.is_active else "deactivated"

    return {"message": f"User {status} successfully."}


def list_pending_teachers(db: Session):
    users = (
        db.query(User)
        .filter(User.role == Role.TEACHER, User.is_approved == False)  # noqa: E712
        .all()
    )

    result = []
    for user in users:
        teacher = user.teacher
        result.append(
            {
                "id": str(user.id),
                "email": user.email,
                "first_name": teacher.first_name if teacher else None,
                "last_name": teacher.last_name if teacher else None,
                "linked_in_acc": teacher.linked_in_acc if teacher else None,
                "is_active": user.is_active,
                "profile_picture": teacher.profile_picture if teacher else None,
                "phone_number": teacher.phone_number if teacher else None,
                "is_approved": user.is_approved,
            }
        )

    return result


def approve_teacher_by_id(db: Session, user_id: UUID):
    user = get_by_id(db, user_id)

    if not user:
        raise NotFound(f"User with ID: {user_id} not found")

    if user.role != Role.TEACHER:
        raise BadRequest("User is not a teacher")

    if user.is_approved:
        return {"message": "Teacher is already approved"}

    user.is_approved = True

    db.commit()

    return {"message": "Teacher approved successfully"}


def list_all_courses(
    db: Session,
    teacher_id: UUID = None,
    student_id: UUID = None,
    title: str = None,
    skip: int = 0,
    limit: int = 10,
):
    query = db.query(Course)

    if teacher_id:
        query = query.filter(Course.owner_id == teacher_id)

    if student_id:
        query = query.join(Course.students).filter(Student.id == student_id)

    if title:
        query = query.filter(Course.title.ilike(f"%{title}%"))

    courses = query.offset(skip).limit(limit).all()

    result = []
    for course in courses:
        result.append(
            {
                "id": str(course.id),
                "title": course.title,
                "description": course.description,
                "objectives": course.objectives,
                "owner_id": str(course.owner_id),
                "teacher_name": (
                    f"{course.owner.first_name} {course.owner.last_name}"
                    if course.owner
                    else None
                ),
                "is_premium": course.is_premium,
                "is_hidden": course.is_hidden,
                "picture": course.picture,
                "rating": course.rating,
                "students": [
                    {
                        "id": str(student.id),
                        "first_name": student.first_name,
                        "last_name": student.last_name,
                        "email": student.user.email if student.user else None,
                        "profile_picture": student.profile_picture,
                    }
                    for student in course.students
                ],
            }
        )

    return result


def toggle_course_visability(db: Session, course_id: UUID):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise NotFound(f"Course with ID: {course_id} not found")

    course.is_hidden = not course.is_hidden
    db.commit()

    if course.is_hidden:
        for student in course.students:
            user = db.query(User).filter(User.id == student.id).first()
            if user and user.email:
                send_email(
                    to=user.email,
                    subject="Course Hidden Notification",
                    body=f"The course '{course.title}' has been temporarily hidden by an administrator and is currently unavailable.",
                )

        return {"message": f"Course '{course.title}' hidden successfully."}

    return {"message": f"Course '{course.title}' is now visible again."}


def delete_course(db: Session, course_id: UUID):
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise NotFound(f"Course with ID: {course_id} not found")

    for student in course.students:
        user = db.query(User).filter(User.id == student.id).first()
        if user and user.email:
            send_email(
                to=user.email,
                subject="Course Deleted Notification",
                body=f"The course '{course.title}' has been deleted by an administrator and is no longer available.",
            )
    course.students.clear()
    db.flush()
    db.delete(course)
    db.commit()

    return {"message": f"Course {course.title} deleted successfully."}


def remove_student_from_course(db: Session, course_id: UUID, student_id: UUID):
    student_course = (
        db.query(StudentCourse)
        .filter(
            StudentCourse.course_id == course_id, StudentCourse.student_id == student_id
        )
        .first()
    )
    student = db.query(Student).filter(Student.id == student_id).first()
    course = db.query(Course).filter(Course.id == course_id).first()
    if not student_course:
        raise NotFound(
            f"Student : {student_id} not enrolled in course with ID: {course_id}"
        )

    db.delete(student_course)
    db.commit()

    return {
        "message": f"Student: {student.first_name} {student.last_name} removed from course: {course.title} successfully."
    }


def get_course_ratings(db: Session, course_id: UUID):
    ratings = (
        db.query(StudentCourse)
        .filter(StudentCourse.course_id == course_id, StudentCourse.score.isnot(None))
        .all()
    )

    result = []
    for rating in ratings:
        student = db.query(Student).filter(Student.id == rating.student_id).first()
        if student:
            result.append(
                {
                    "student_id": str(rating.student.id),
                    "student_name": (
                        f"{student.first_name} {student.last_name}" if student else None
                    ),
                    "score": rating.score,
                }
            )

    return result
