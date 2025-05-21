from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from database.session import Base
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship

class Role(PyEnum):
    ADMIN = 'ADMIN'
    TEACHER = 'TEACHER'
    STUDENT = 'STUDENT'

class User(Base):
    __tablename__ = 'users'
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(Role))
    
    admin = relationship("Admin", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)
    student = relationship("Student", back_populates="user", uselist=False)

class Admin(Base):
    __tablename__ = 'admins'
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid'), unique=True)
    
    user = relationship("User", back_populates="admin")

class Teacher(Base):
    __tablename__ = 'teachers'
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_picture = Column(String(255))
    phone_number = Column(String(20))
    linked_in_acc = Column(String(255))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid'))
    
    user = relationship("User", back_populates="teacher")
    courses = relationship("Course", back_populates="owner")

class Student(Base):
    __tablename__ = 'students'
    first_name = Column(String(100))
    last_name = Column(String(100))
    subscribed = Column(Boolean)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid'))
    
    user = relationship("User", back_populates="student")
    courses = relationship("Course", secondary="student_courses",back_populates="students")

class Course(Base):
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
    
    owner = relationship("Teacher", back_populates="courses")
    students = relationship("Student",secondary="student_courses",back_populates="courses")
    tags = relationship("Tag",secondary="course_tags",back_populates="courses")

class Tag(Base):
    __tablename__ = 'tags'
    name = Column(String(100), unique=True)
    
    courses = relationship("Course",secondary="course_tags",back_populates="tags")

class StudentCourse(Base):
    __tablename__ = 'student_courses'
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.uuid'), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.uuid'), primary_key=True)
    status = Column(String(50))
    progress = Column(Integer)
    
    student = relationship("Student", backref="course_associations")
    course = relationship("Course", backref="student_associations")

class CourseTag(Base):
    __tablename__ = 'course_tags'
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.uuid'), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.uuid'), primary_key=True)
    
    course = relationship("Course", backref="tag_associations")
    tag = relationship("Tag", backref="course_associations")