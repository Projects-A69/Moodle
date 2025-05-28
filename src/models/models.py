from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from src.database.base import Base
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
import uuid

class Role(PyEnum):
    ADMIN = 'ADMIN'
    TEACHER = 'TEACHER'
    STUDENT = 'STUDENT'

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    
    admin = relationship("Admin", back_populates="user", uselist=False, cascade="all, delete-orphan")
    teacher = relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    user = relationship("User", back_populates="admin")

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_picture = Column(String(255))
    phone_number = Column(String(20))
    linked_in_acc = Column(String(255))
    
    user = relationship("User", back_populates="teacher")
    courses = relationship("Course", back_populates="owner", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = 'students'
    id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_picture = Column(String(255))

    user = relationship("User", back_populates="student")
    courses = relationship("Course", secondary="student_courses", back_populates="students")

class Course(Base):
    __tablename__ = 'courses'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    objectives = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('teachers.id'), nullable=False)
    is_premium = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)
    picture = Column(String(255))
    rating = Column(Float, default=0.0)
   
    owner = relationship("Teacher", back_populates="courses")
    students = relationship("Student", secondary="student_courses", back_populates="courses")
    tags = relationship("Tag", secondary="course_tags", back_populates="courses")
    sections = relationship("Section", back_populates="course", cascade="all, delete-orphan")

class Section(Base):
    __tablename__ = 'sections'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    description = Column(Text)
    information = Column(Text)
    link = Column(String(255))
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))

    course = relationship("Course", back_populates="sections")


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    
    courses = relationship("Course", secondary="course_tags", back_populates="tags")

class StudentCourse(Base):
    __tablename__ = 'student_courses'
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id'), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), primary_key=True)
    is_approved = Column(Boolean, default=False)
    progress = Column(Integer, default=0)
    score = Column(Float, nullable=True)
    
    student = relationship("Student", backref="course_associations")
    course = relationship("Course", backref="student_associations")

class CourseTag(Base):
    __tablename__ = 'course_tags'
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True)
    
    course = relationship("Course", backref="tag_associations")
    tag = relationship("Tag", backref="course_associations")


# class CoursesRate(Base):
#     __tablename__ = 'courses_ratings'
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
#     course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
#     rating = Column(Float, nullable=False)
#
#     user = relationship("User", backref="course_ratings")
#     course = relationship("Course", backref="ratings")