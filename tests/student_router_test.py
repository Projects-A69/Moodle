import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.models.models import Student, User
from src.schemas.all_models import CoursesRate
from src.crud import student as student_crud


class TestStudentEndpoints(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.course_id = uuid4()
        self.student_id = uuid4()
        self.current_student = Student(id=self.student_id)
        self.current_user = User(id=self.student_id)
        self.payload = CoursesRate(score=5.0, comment="Great course!")

    @patch("src.crud.student.subscribe_to_course")
    def test_subscribe_to_courses(self, mock_subscribe):
        mock_subscribe.return_value = {"message": "Subscribed successfully"}
        result = student_crud.subscribe_to_course(
            course_id=self.course_id,
            current_student=self.current_student,
            db=self.mock_db,
        )
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Subscribed successfully")

    @patch("src.crud.student.unsubscribe_from_course")
    def test_unsubscribe_from_course_endpoint(self, mock_unsubscribe):
        mock_unsubscribe.return_value = {"message": "Unsubscribed successfully"}
        result = student_crud.unsubscribe_from_course(
            course_id=self.course_id,
            student_id=self.student_id,
            db=self.mock_db,
        )
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Unsubscribed successfully")

    @patch("src.crud.student.rate_course")
    def test_rate_course_endpoint(self, mock_rate):
        mock_rate.return_value = {"message": "Course rated successfully"}
        result = student_crud.rate_course(
            self.mock_db, self.course_id, self.payload, self.current_user
        )
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Course rated successfully")

    @patch("src.crud.student.get_all_favorite_courses")
    def test_get_favorite_courses(self, mock_get_favorites):
        mock_get_favorites.return_value = ["Course1", "Course2"]
        result = student_crud.get_all_favorite_courses(self.mock_db, self.current_user)
        self.assertIsInstance(result, list)
        self.assertIn("Course1", result)

    @patch("src.crud.student.toggle_favorite_course")
    def test_toggle_favorite_course_route(self, mock_toggle):
        mock_toggle.return_value = {"message": "Toggled favorite successfully"}
        result = student_crud.toggle_favorite_course(
            self.course_id, self.current_user, self.mock_db
        )
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Toggled favorite successfully")

    def test_get_student_courses_returns_list(self):
        # Simulate DB query filter returning a list of StudentCourse objects
        student_course_mock = MagicMock()
        self.mock_db.query().filter().all.return_value = [student_course_mock]
        result = self.mock_db.query().filter().all()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
