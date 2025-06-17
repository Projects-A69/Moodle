import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.models.models import Role
from src.crud.teacher import approve_student_by_id
from src.utils.custom_responses import NotFound, BadRequest


class TestApproveStudentById(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.student_id = uuid4()
        self.course_id = uuid4()

        self.student_user = MagicMock(id=self.student_id, role=Role.STUDENT)
        self.teacher_user = MagicMock(id=self.student_id, role=Role.TEACHER)
        self.course = MagicMock(id=self.course_id, title="Physics")

    @patch("src.crud.teacher.get_by_id")
    def test_approve_student_success_existing_enrollment(self, mock_get_by_id):
        mock_get_by_id.return_value = self.student_user
        self.db.query().filter().first.side_effect = [self.course, MagicMock(is_approved=False)]

        response = approve_student_by_id(self.db, self.student_id, self.course_id)
        self.assertIn("approved", response["message"])
        self.db.commit.assert_called_once()

    @patch("src.crud.teacher.get_by_id")
    def test_approve_student_user_not_found(self, mock_get_by_id):
        mock_get_by_id.return_value = None
        with self.assertRaises(NotFound) as ctx:
            approve_student_by_id(self.db, self.student_id, self.course_id)
        self.assertIn("User with ID", str(ctx.exception))

    @patch("src.crud.teacher.get_by_id")
    def test_approve_student_user_not_a_student(self, mock_get_by_id):
        mock_get_by_id.return_value = self.teacher_user
        with self.assertRaises(BadRequest) as ctx:
            approve_student_by_id(self.db, self.student_id, self.course_id)
        self.assertIn("not a student", str(ctx.exception))

    @patch("src.crud.teacher.get_by_id")
    def test_approve_student_course_not_found(self, mock_get_by_id):
        mock_get_by_id.return_value = self.student_user
        self.db.query().filter().first.side_effect = [None]

        with self.assertRaises(NotFound) as ctx:
            approve_student_by_id(self.db, self.student_id, self.course_id)
        self.assertIn("Course not found", str(ctx.exception))
