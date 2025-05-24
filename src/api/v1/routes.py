from fastapi import APIRouter

from src.api.v1.endpoints import users, courses

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])

api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
