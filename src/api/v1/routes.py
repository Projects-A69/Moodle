from fastapi import APIRouter

from src.api.v1.endpoints import (
    users,
    admins,
    courses,
    sections,
    tags,
    students,
    teachers,
)

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(sections.router, prefix="/sections", tags=["sections"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(admins.router, prefix="/admins", tags=["admins"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
