from fastapi import APIRouter

from src.api.v1.endpoints import users,admins,courses

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(admins.router, prefix="/admins", tags=["admins"])
