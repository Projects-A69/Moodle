from fastapi import APIRouter

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/courses")
def list_accessible_courses():
    pass


@router.post("/courses/{course_id}/subscribe")
def subscribe_to_course():
    pass


@router.get("/courses/{course_id}")
def view_course():
    pass


@router.get("/courses/{course_id}/sections")
def list_sections():
    pass


@router.get("/courses/{course_id}/sections/{section_id}")
def view_section():
    pass


@router.get("/")
def view_profile():
    pass


@router.post("/courses/{course_id}/rating")
def rate_course():
    pass


@router.put("/profile")
def edit_profile():
    pass