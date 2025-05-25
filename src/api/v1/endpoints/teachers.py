from fastapi import APIRouter

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("/courses")
def list_accessible_courses():
    pass


@router.get("/courses/{course_id}")
def view_course_details():
    pass


@router.get("/courses/{course_id}/sections")
def list_sections():
    pass


@router.get("/")
def view_profile():
    pass


@router.post("/courses")
def create_course():
    pass


@router.post("/courses/{course_id}/sections")
def create_section():
    pass


@router.post("/")
def register_as_teacher(): # Awaiting approval
    pass


@router.put("/courses/{course_id}")
def edit_course():
    pass


@router.put("/courses/{course_id}/sections")
def edit_sections():
    pass


@router.put("/")
def edit_profile():
    pass


