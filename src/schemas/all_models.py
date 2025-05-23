from pydantic import BaseModel,EmailStr
from uuid import UUID
from src.models.models import Role

class User(BaseModel):
    email: str
    password: str
    role: Role
    
class UserCreate(BaseModel):
    email: str
    password: str
    role: Role

    first_name: str
    last_name: str

    profile_picture: str | None = None
    phone_number: str | None = None
    linked_in_acc: str| None = None

    subscribed: bool = False

class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Admin(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    user_id: UUID

class Teacher(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    profile_picture: str
    phone_number: str
    linked_in_acc: str
    user_id: UUID

class Student(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    subscribed: bool
    user_id: UUID

class Course(BaseModel):
    title: str
    description: str
    objectives: str
    owner_id: UUID
    is_premium: bool
    is_hidden: bool
    picture: str
    rating: float
    score: float

class Tag(BaseModel):
    name: str
    
class Section(BaseModel):
    title: str
    content: str
    description: str | None = None
    information: str | None = None
    link: str | None = None
    course_id: UUID

class StudentCourse(BaseModel):
    student_id: UUID
    course_id: UUID
    status: str
    progress: int

class CourseTag(BaseModel):
    course_id: UUID
    tag_id: UUID