from uuid import UUID

from pydantic import BaseModel, EmailStr

from src.models.models import Role

from typing import Optional


class User(BaseModel):
    email: EmailStr
    password: str
    role: Role
    is_active: bool = True
    is_approved: bool = False


class BaseUserCreate(BaseModel):
    email: EmailStr
    password: str


class AdminCreate(BaseUserCreate):
    first_name: str
    last_name: str


class TeacherCreate(BaseUserCreate):
    first_name: str
    last_name: str
    profile_picture: str | None = None
    phone_number: str
    linked_in_acc: str


class StudentCreate(BaseUserCreate):
    first_name: str
    last_name: str
    profile_picture: str | None = None


class AdminUpdate(BaseModel):
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class TeacherUpdate(BaseModel):
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    linked_in_acc: str | None = None
    profile_picture: str | None = None


class StudentUpdate(BaseModel):
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    profile_picture: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Admin(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class Teacher(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    profile_picture: str
    phone_number: str
    linked_in_acc: str


class Student(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    profile_picture: str
    user_id: UUID


class CourseInDB(BaseModel):
    id: UUID
    title: str
    description: str
    objectives: str
    owner_id: UUID
    is_premium: bool = False
    is_hidden: bool = False
    picture: str
    rating: float


class CoursesCreate(BaseModel):
    title: str
    description: str
    objectives: str
    picture: str
    is_premium: bool = False


class CoursesUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    objectives: str | None = None
    picture: str | None = None
    is_premium: bool | None = None
    is_hidden: bool | None = None


class CoursesRate(BaseModel):
    score: float


class Tag(BaseModel):
    name: str


class CourseTag(BaseModel):
    course_id: UUID
    tag_id: UUID


class CreateTag(BaseModel):
    name: str


class SectionInDB(BaseModel):
    title: str
    content: str
    description: str | None = None
    information: str | None = None
    link: str | None = None
    is_visited: bool = False
    course_id: UUID


class SectionCreate(BaseModel):
    title: str
    content: Optional[str] = ""
    description: Optional[str] = ""
    information: Optional[str] = ""
    link: Optional[str] = ""


class SectionUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    description: str | None = None
    information: str | None = None
    link: str | None = None


class SectionVisit(BaseModel):
    student_id: UUID
    section_id: UUID


class StudentCourse(BaseModel):
    student_id: UUID
    course_id: UUID
    score: float
    is_visited: bool = False
    is_approved: bool
    progress: int
    is_favorite: bool = False
