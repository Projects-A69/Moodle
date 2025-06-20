import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException

from src.models.models import User, Role, Course, Tag
from src.crud import course as course_crud


class TestCourseCrud(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.course_id = uuid4()
        self.teacher_id = uuid4()
        self.tag_id = uuid4()
        self.user = User(id=self.teacher_id, role=Role.TEACHER, is_active=True)
        self.mock_course = Course(
            id=self.course_id, title="Test Course", owner_id=self.teacher_id
        )

    def test_get_course_with_title_and_user(self):
        self.mock_db.query().all.return_value = [self.mock_course]
        result = course_crud.get_course(
            self.mock_db, title="Test", current_user=self.user
        )
        self.assertIsInstance(result, list)

    def test_get_course_by_id_found(self):
        course = Course(id=self.course_id, title="Course 1", owner_id=self.teacher_id)
        self.mock_db.query().filter().first.return_value = course
        result = course_crud.get_course_by_id(
            self.mock_db, self.course_id, current_user=self.user
        )
        self.assertEqual(result, course)

    def test_get_course_by_id_not_found(self):
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        query_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        self.mock_db.query.return_value = query_mock

        with self.assertRaises(HTTPException):
            course_crud.get_course_by_id(
                self.mock_db, self.course_id, current_user=self.user
            )

    def test_create_courses_success(self):
        self.mock_db.query().filter().first.return_value = (
            None  # Simulate title not existing
        )
        result_course = Course(id=self.course_id, title="New Course")
        with patch("src.crud.course.Course") as mock_course:
            mock_course.return_value = result_course
            self.mock_db.add = MagicMock()
            self.mock_db.commit = MagicMock()
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
        rating = MagicMock(score=5, student=MagicMock(first_name="John"))
        self.mock_db.query().filter().all.return_value = [rating]
        self.mock_db.query().filter().first.return_value = MagicMock(score=5)
        result = course_crud.rating_course(self.mock_db, self.course_id)
        self.assertIsInstance(result, dict)

    def test_get_courses_by_tag_id_found(self):
        tag = Tag(id=self.tag_id)
        tag.courses = [self.mock_course]
        self.mock_db.query().filter().first.return_value = tag
        result = course_crud.get_courses_by_tag_id(
            self.mock_db, tag_id=self.tag_id, current_user=self.user
        )
        self.assertIsInstance(result, list)

    def test_get_courses_by_tag_id_empty(self):
        tag = Tag(id=self.tag_id)
        tag.courses = []
        self.mock_db.query().filter().first.return_value = tag
        result = course_crud.get_courses_by_tag_id(
            self.mock_db, tag_id=self.tag_id, current_user=self.user
        )
        self.assertEqual(result, [])
