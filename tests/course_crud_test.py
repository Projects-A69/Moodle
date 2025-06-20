import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import HTTPException
from src.models.models import Course, Role, StudentCourse, User
from src.crud import course as course_crud


class TestCourseCrud(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.user_id = uuid4()
        self.course_id = uuid4()
        self.student_id = uuid4()
        self.tag_id = uuid4()

        self.mock_user = User(id=self.user_id, role=Role.STUDENT, is_active=True)
        self.mock_course = Course(
            id=self.course_id,
            title="Test Course",
            description="Desc",
            objectives="Goals",
            picture="pic.png",
            rating=8.0,
            is_premium=False,
            is_hidden=False,
            owner_id=self.user_id,
        )

    def test_get_course_no_user(self):
        query_mock = self.mock_db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.filter.return_value.all.return_value = [self.mock_course]

        result = course_crud.get_course(self.mock_db, title="Test")
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["title"], "Test Course")

    def test_get_course_by_id_not_found(self):
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(HTTPException):
            course_crud.get_course_by_id(self.mock_db, self.course_id)

    def test_get_course_by_id_as_student_not_enrolled(self):
        premium_course = Course(
            id=self.course_id, is_hidden=False, is_premium=True, owner_id=self.user_id
        )
        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            premium_course
        )
        self.mock_user.role = Role.STUDENT
        self.mock_user.id = self.user_id

        def filter_side_effect(*args, **kwargs):
            mock_q = MagicMock()
            mock_q.first.return_value = None
            return mock_q

        self.mock_db.query.return_value.filter.side_effect = filter_side_effect

        with self.assertRaises(HTTPException):
            course_crud.get_course_by_id(self.mock_db, self.course_id, self.mock_user)

    def test_create_course_title_exists(self):
        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            self.mock_course
        )
        with self.assertRaises(HTTPException):
            course_crud.create_courses(
                self.mock_db,
                title="Test Course",
                description="duplicate",
                objectives="none",
                is_premium=False,
                owner_id=self.user_id,
                picture=None,
            )

    def test_update_specific_course_not_owner(self):
        other_user = User(id=uuid4(), role=Role.STUDENT)
        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            self.mock_course
        )
        with self.assertRaises(HTTPException):
            course_crud.update_specific_course(
                self.mock_db,
                id=self.course_id,
                current_user=other_user,
                title="Updated",
            )

    def test_rating_course_success(self):
        student_course = StudentCourse(score=8.0)
        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            self.mock_course
        )
        self.mock_db.query.return_value.filter.return_value.all.return_value = [
            student_course
        ]

        student_course.student = MagicMock()
        student_course.student.first_name = "John"

        result = course_crud.rating_course(self.mock_db, self.course_id)
        self.assertIn("rating", result)
        self.assertEqual(result["rating"], 8.0)

    def test_rating_course_not_found(self):
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(HTTPException):
            course_crud.rating_course(self.mock_db, self.course_id)

    def test_get_courses_by_tag_id_as_admin(self):
        self.mock_user.role = Role.ADMIN

        tag = MagicMock()
        tag.course_tags = []

        course_tag_mock = MagicMock()
        course_tag_mock.course = self.mock_course
        tag.course_tags.append(course_tag_mock)

        self.mock_db.query.return_value.filter.return_value.first.return_value = tag

        self.mock_user.student = MagicMock()
        self.mock_user.student.courses = []

        result = course_crud.get_courses_by_tag_id(
            self.mock_db, self.tag_id, self.mock_user
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], self.mock_course.id)

    def test_get_courses_by_tag_id_not_found(self):
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(HTTPException):
            course_crud.get_courses_by_tag_id(self.mock_db, self.tag_id)
