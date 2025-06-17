import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException
from src.models.models import User, Role, Course
from src.crud import course as course_crud


class TestCourseCrud(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.course_id = uuid4()
        self.teacher_id = uuid4()
        self.user = User(id=self.teacher_id, role=Role.TEACHER, is_active=True)

    def test_get_course_with_title_and_user(self):
        self.mock_db.query.return_value.all.return_value = [Course(id=self.course_id, title="Test Course")]
        result = course_crud.get_course(self.mock_db, title="Test", current_user=self.user)
        self.assertIsInstance(result, list)

    def test_get_course_by_id_found(self):
        course = Course(id=self.course_id, title="Course 1")
        filter_mock = MagicMock()
        filter_mock.first.return_value = course
        query_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        self.mock_db.query.return_value = query_mock

        result = course_crud.get_course_by_id(self.mock_db, self.course_id, current_user=self.user)
        self.assertEqual(result, course)

    def test_get_course_by_id_not_found(self):
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        query_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        self.mock_db.query.return_value = query_mock

        with self.assertRaises(HTTPException):
            course_crud.get_course_by_id(self.mock_db, self.course_id, current_user=self.user)

    def test_create_courses_success(self):
        # Assume title does not exist
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        query_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        self.mock_db.query.return_value = query_mock

        self.mock_db.add = MagicMock()
        self.mock_db.commit = MagicMock()
        self.mock_db.flush = MagicMock()

        result = course_crud.create_courses(
            self.mock_db,
            title="New Course",
            description="Description",
            objectives="Objectives",
            is_premium=True,
            owner_id=self.teacher_id,
            picture=None,
        )
        self.assertIsInstance(result, Course)

    def test_update_specific_course_success(self):
        course = Course(id=self.course_id, title="Old Title")
        filter_mock = MagicMock()
        filter_mock.first.side_effect = [course, None]  # 1st call: course found, 2nd call: title check returns None
        query_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        self.mock_db.query.return_value = query_mock

        self.mock_db.add = MagicMock()
        self.mock_db.commit = MagicMock()
        self.mock_db.flush = MagicMock()

        updated_course = course_crud.update_specific_course(
            db=self.mock_db,
            id=self.course_id,
            current_user=self.user,
            title="Updated Title",
            description=None,
            objectives=None,
            is_premium=None,
            picture=None,
        )
        self.assertEqual(updated_course.title, "Updated Title")

    def test_update_specific_course_not_found(self):
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        query_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        self.mock_db.query.return_value = query_mock

        with self.assertRaises(HTTPException):
            course_crud.update_specific_course(
                db=self.mock_db,
                id=self.course_id,
                current_user=self.user,
                title="Updated Title",
            )

    def test_rating_course_with_ratings(self):
        rating = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = Course(id=self.course_id)
        query_mock = MagicMock()
        query_mock.filter.side_effect = [filter_mock, filter_mock]
        self.mock_db.query.return_value = query_mock
        self.mock_db.query().filter().all.return_value = [rating]

        result = course_crud.rating_course(self.mock_db, self.course_id)
        self.assertIsInstance(result, dict)
        self.assertIn("rating", result)

    def test_rating_course_no_ratings(self):
        filter_mock = MagicMock()
        filter_mock.first.return_value = Course(id=self.course_id)
        query_mock = MagicMock()
        query_mock.filter.side_effect = [filter_mock, filter_mock]
        self.mock_db.query.return_value = query_mock
        self.mock_db.query().filter().all.return_value = []

        with self.assertRaises(HTTPException):
            course_crud.rating_course(self.mock_db, self.course_id)

    def test_get_courses_by_tag_id_found(self):
        courses = [Course(id=self.course_id, title="Course by tag")]
        tag_mock = MagicMock()
        tag_mock.courses = courses

        filter_mock = MagicMock()
        filter_mock.first.return_value = tag_mock
        query_mock = MagicMock()
        query_mock.query.return_value = query_mock
        self.mock_db.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock

        result = course_crud.get_courses_by_tag_id(self.mock_db, tag_id=uuid4(), current_user=None)
        self.assertIsInstance(result, list)

    def test_get_courses_by_tag_id_empty(self):
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        query_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        self.mock_db.query.return_value = query_mock

        with self.assertRaises(HTTPException):
            course_crud.get_courses_by_tag_id(self.mock_db, tag_id=uuid4(), current_user=None)
