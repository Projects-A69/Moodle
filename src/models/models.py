from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
from enum import Enum as PyEnum

class Role(PyEnum):
    ADMIN = 'ADMIN'
    TEACHER = 'TEACHER'
    STUDENT = 'STUDENT'

class User(BaseModel):
    __tablename__ = 'users'
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(Role))

class Admin(BaseModel):
    __tablename__ = 'admins'
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid'), unique=True)

class Teacher(BaseModel):
    __tablename__ = 'teachers'
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True)
    password = Column(String(255))
    profile_picture = Column(String(255))
    phone_number = Column(String(20))
    linked_in_acc = Column(String(255))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid'))

class Student(BaseModel):
    __tablename__ = 'students'
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True)
    password = Column(String(255))
    subscribed = Column(Boolean)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid'))

class Course(BaseModel):
    __tablename__ = 'courses'
    title = Column(String(255))
    description = Column(Text)
    objectives = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('teachers.uuid'))
    is_premium = Column(Boolean)
    is_hidden = Column(Boolean)
    picture = Column(String(255))
    rating = Column(Float)
    score = Column(Float)

class Tag(BaseModel):
    __tablename__ = 'tags'
    name = Column(String(100), unique=True)

class StudentCourse(BaseModel):
    __tablename__ = 'student_courses'
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.uuid'), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.uuid'), primary_key=True)
    status = Column(String(50))
    progress = Column(Integer)

class CourseTag(BaseModel):
    __tablename__ = 'course_tags'
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.uuid'), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.uuid'), primary_key=True)