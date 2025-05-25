from pydantic import BaseModel,EmailStr
from uuid import UUID
from src.models.models import Role

class User(BaseModel):
    email: EmailStr
    password: str
    role: Role
    is_active: bool = True
    is_approved: bool = False
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role
    first_name: str
    last_name: str
    profile_picture: str | None = None
    phone_number: str | None = None
    linked_in_acc: str| None = None

class UserUpdate(BaseModel):
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    linked_in_acc: str | None = None
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
    is_premium: bool
    is_hidden: bool
    picture: str
    rating: float
    score: float

class CoursesCreate(BaseModel):
    title: str
    description: str
    objectives: str

class CoursesUpdate(BaseModel):
    title: str
    description: str
    objectives: str
    picture: str

class CoursesRate(BaseModel):
    id: UUID
    user_id: UUID
    score: float

class Tag(BaseModel):
    name: str
    
class SectionInDB(BaseModel):
    title: str
    content: str
    description: str | None = None
    information: str | None = None
    link: str | None = None
    course_id: UUID

class SectionCreate(BaseModel):
    title: str
    content: str
    description: str
    information: str

class SectionUpdate(BaseModel):
    title: str
    description: str
    information: str
    link: str
    section_id: UUID

class StudentCourse(BaseModel):
    student_id: UUID
    course_id: UUID
    status: str
    progress: int

class CourseTag(BaseModel):
    course_id: UUID
    tag_id: UUID