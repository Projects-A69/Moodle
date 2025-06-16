import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import UploadFile, HTTPException
from src.models.models import Course, Role, Student, StudentCourse, Tag, User
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
        self.mock_db.query().filter().all.return_value = [self.mock_course]
        result = course_crud.get_course(self.mock_db, title="Test")
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["title"], "Test Course")

    def test_get_course_as_admin(self):
        self.mock_db.query().all.return_value = [self.mock_course]
        self.mock_user.role = Role.ADMIN
        result = course_crud.get_course(self.mock_db, "", current_user=self.mock_user)
        self.assertEqual(result[0]["id"], self.mock_course.id)

    def test_get_course_by_id_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(HTTPException):
            course_crud.get_course_by_id(self.mock_db, self.course_id)

    def test_get_course_by_id_as_student_not_enrolled(self):
        premium_course = Course(id=self.course_id, is_hidden=False, is_premium=True)
        self.mock_db.query().filter().first.return_value = premium_course
        self.mock_user.role = Role.STUDENT
        self.mock_user.id = self.user_id
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(HTTPException):
            course_crud.get_course_by_id(self.mock_db, self.course_id, self.mock_user)

    @patch("src.crud.course.upload_image_to_s3", return_value="uploaded.png")
    def test_create_course_with_image(self, mock_upload):
        self.mock_db.query().filter().first.return_value = None
        file_mock = MagicMock(spec=UploadFile)
        result = course_crud.create_courses(
            self.mock_db,
            title="New Course",
            description="A new course",
            objectives="Learn fast",
            is_premium=True,
            owner_id=self.user_id,
            picture=file_mock,
        )
        self.assertEqual(result.title, "New Course")

    def test_create_course_title_exists(self):
        self.mock_db.query().filter().first.return_value = self.mock_course
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
        self.mock_db.query().filter().first.return_value = self.mock_course
        with self.assertRaises(HTTPException):
            course_crud.update_specific_course(
                self.mock_db,
                id=self.course_id,
                current_user=other_user,
                title="Updated",
            )

    @patch("src.crud.course.upload_image_to_s3", return_value="new.png")
    def test_update_specific_course_success(self, mock_upload):
        self.mock_db.query().filter().first.side_effect = [self.mock_course, None]
        self.mock_user.role = Role.TEACHER
        result = course_crud.update_specific_course(
            self.mock_db,
            id=self.course_id,
            current_user=self.mock_user,
            title="Updated Title",
            picture=MagicMock(),
        )
        self.assertEqual(result.title, "Updated Title")

    def test_rating_course_success(self):
        student_course = StudentCourse(score=8.0)
        self.mock_db.query().filter().first.return_value = self.mock_course
        self.mock_db.query().filter().all.return_value = [student_course]
        result = course_crud.rating_course(self.mock_db, self.course_id)
        self.assertIn("rating", result)

    def test_rating_course_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(HTTPException):
            course_crud.rating_course(self.mock_db, self.course_id)

    def test_get_courses_by_tag_id_as_admin(self):
        self.mock_user.role = Role.ADMIN
        tag = Tag(id=self.tag_id, courses=[self.mock_course])
        self.mock_db.query().filter().first.return_value = tag
        result = course_crud.get_courses_by_tag_id(self.mock_db, self.tag_id, self.mock_user)
        self.assertEqual(len(result), 1)

    def test_get_courses_by_tag_id_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(HTTPException):
            course_crud.get_courses_by_tag_id(self.mock_db, self.tag_id)