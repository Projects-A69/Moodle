import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.crud import student as student_crud
from src.schemas.all_models import CoursesRate
from src.utils.custom_responses import BadRequest, NotFound


class TestStudentCrud(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.course_id = uuid4()
        self.student_id = uuid4()
        self.current_student = MagicMock()
        self.current_student.id = self.student_id
        self.course = MagicMock()
        self.course.id = self.course_id
        self.course.title = "Math 101"
        self.course.is_premium = True
        self.course.owner = MagicMock(first_name="Alice", user=MagicMock(email="alice@example.com"))
        self.current_student.student = MagicMock(first_name="Bob", last_name="Smith")

    @patch("src.crud.student.send_email")
    @patch("src.crud.student.generate_student_approval_token")
    def test_subscribe_to_course_success(self, mock_generate_token, mock_send_email):
        self.db.query().filter().first.side_effect = [self.course, None]
        self.db.query().join().filter().scalar.return_value = 0
        mock_generate_token.return_value = "fake-token"

        response = student_crud.subscribe_to_course(self.course_id, self.current_student, self.db)

        self.assertIn("message", response)
        mock_send_email.assert_called_once()

    def test_subscribe_to_course_already_subscribed(self):
        self.db.query().filter().first.side_effect = [self.course, MagicMock()]
        with self.assertRaises(BadRequest):
            student_crud.subscribe_to_course(self.course_id, self.current_student, self.db)

    def test_subscribe_to_public_course_raises(self):
        self.course.is_premium = False
        self.db.query().filter().first.return_value = self.course
        with self.assertRaises(BadRequest):
            student_crud.subscribe_to_course(self.course_id, self.current_student, self.db)

    def test_unsubscribe_success(self):
        student_course = MagicMock()
        student = MagicMock(first_name="John", last_name="Doe")
        course = MagicMock(title="Biology")

        self.db.query().filter().first.side_effect = [student_course, student, course]

        response = student_crud.unsubscribe_from_course(self.student_id, self.course_id, self.db)
        self.assertEqual(response["message"], "John Doe unsubscribed from Biology successfully")

    def test_unsubscribe_not_found(self):
        self.db.query().filter().first.return_value = None
        with self.assertRaises(NotFound):
            student_crud.unsubscribe_from_course(self.student_id, self.course_id, self.db)

    def test_rate_course_success(self):
        course = MagicMock()
        student_course = MagicMock(progress=50)
        payload = CoursesRate(score=4)

        self.db.query().filter().first.side_effect = [course, student_course]

        response = student_crud.rate_course(self.db, self.course_id, payload, self.current_student)
        self.assertEqual(response["score"], 4)

    def test_rate_course_not_enrolled(self):
        course = MagicMock()
        self.db.query().filter().first.side_effect = [course, None]
        with self.assertRaises(Exception):
            student_crud.rate_course(self.db, self.course_id, CoursesRate(score=4), self.current_student)

    def test_get_all_favorites_success(self):
        course1 = MagicMock(is_premium=False, title="A", description="desc", objectives="obj", picture="pic.png")
        course2 = MagicMock(is_premium=True, title="B", description="desc")
        favorite1 = MagicMock(course=course1, is_approved=True)
        favorite2 = MagicMock(course=course2, is_approved=False)
        self.db.query().join().filter().all.return_value = [favorite1, favorite2]

        result = student_crud.get_all_favorite_courses(self.db, self.current_student)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "A")
        self.assertEqual(result[1]["title"], "B")

    def test_get_all_favorites_none(self):
        self.db.query().join().filter().all.return_value = []
        result = student_crud.get_all_favorite_courses(self.db, self.current_student)
        self.assertEqual(result["message"], "No favorite courses found.")

    def test_toggle_favorite_course_add(self):
        self.db.query().filter().first.side_effect = [self.course, None]
        result = student_crud.toggle_favorite_course(self.course_id, self.current_student, self.db)
        self.assertEqual(result["message"], "Course added to favorites.")

    def test_toggle_favorite_course_remove(self):
        self.db.query().filter().first.side_effect = [self.course, MagicMock(is_favorite=True)]
        result = student_crud.toggle_favorite_course(self.course_id, self.current_student, self.db)
        self.assertIn("Course", result["message"])
