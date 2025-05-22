from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def list_all_users():
    pass

@router.put("/users/{user_id}/deactivate")
def deactivate_user(user_id: str):
    pass

@router.put("/users/{user_id}/reactivate")
def reactivate_user(user_id: str):
    pass

@router.get("/pending-teachers")
def list_pending_teachers():
    pass

@router.put("/teachers/{teacher_id}/approve")
def approve_teacher(teacher_id: str):
    pass

@router.get("/courses")
def list_all_courses():
    pass

@router.put("/courses/{course_id}/hide")
def hide_course(course_id: str):
    pass

@router.delete("/courses/{course_id}")
def delete_course(course_id: str):
    pass

@router.get("/courses/search")
def search_courses_by_teacher_or_student():
    pass

@router.delete("/courses/{course_id}/students/{student_id}")
def remove_student_from_course(course_id: str, student_id: str):
    pass

@router.get("/courses/{course_id}/ratings")
def trace_course_ratings(course_id: str):
    pass
