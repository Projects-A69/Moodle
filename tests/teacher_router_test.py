import unittest
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID
from itsdangerous import BadSignature, SignatureExpired

from src.utils.custom_responses import BadRequest


class TestTeachersEndpoints(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.course_id = uuid4()
        self.student_id = uuid4()
        self.user_id = uuid4()
        self.token = "sometoken"
        self.current_teacher = MagicMock()
        self.current_teacher.id = uuid4()

    @patch("src.crud.teacher.list_pending_students")
    def test_list_pending_students_endpoint(self, mock_list_pending):
        mock_list_pending.return_value = ["student1", "student2"]
        from src.api.v1.endpoints.teachers import list_pending_students_endpoint

        result = list_pending_students_endpoint(
            course_id=self.course_id,
            db=self.mock_db,
            current_teacher=self.current_teacher,
        )
        self.assertEqual(result, ["student1", "student2"])
        mock_list_pending.assert_called_once_with(
            db=self.mock_db, current_teacher=self.current_teacher, course_id=self.course_id
        )

    @patch("src.utils.token_utils.verify_student_approval_token")
    @patch("src.crud.teacher.approve_student_by_id")
    def test_approve_student_by_token_success(self, mock_approve, mock_verify):
        mock_verify.return_value = {
            "student_id": str(self.student_id),
            "course_id": str(self.course_id),
        }
        mock_approve.return_value = {"approved": True}
        from src.api.v1.endpoints.teachers import approve_student_by_token

        result = approve_student_by_token(token=self.token, db=self.mock_db)
        self.assertEqual(result, {"approved": True})
        mock_verify.assert_called_once_with(self.token)
        mock_approve.assert_called_once_with(
            self.mock_db, self.student_id, self.course_id
        )

    @patch("src.utils.token_utils.verify_student_approval_token")
    def test_approve_student_by_token_expired(self, mock_verify):
        from src.api.v1.endpoints.teachers import approve_student_by_token

        mock_verify.side_effect = SignatureExpired("expired")
        with self.assertRaises(BadRequest) as context:
            approve_student_by_token(token=self.token, db=self.mock_db)
        self.assertIn("Token has expired.", str(context.exception))

    @patch("src.utils.token_utils.verify_student_approval_token")
    def test_approve_student_by_token_bad_signature(self, mock_verify):
        from src.api.v1.endpoints.teachers import approve_student_by_token

        mock_verify.side_effect = BadSignature("bad signature")
        with self.assertRaises(BadRequest) as context:
            approve_student_by_token(token=self.token, db=self.mock_db)
        self.assertIn("Invalid approval token.", str(context.exception))

    @patch("src.utils.token_utils.verify_student_approval_token")
    def test_approve_student_by_token_invalid_data(self, mock_verify):
        from src.api.v1.endpoints.teachers import approve_student_by_token

        mock_verify.return_value = {"invalid": "data"}
        with self.assertRaises(BadRequest) as context:
            approve_student_by_token(token=self.token, db=self.mock_db)
        self.assertIn("Invalid data in token.", str(context.exception))

    @patch("src.crud.teacher.approve_student_by_id")
    def test_approve_student_endpoint(self, mock_approve):
        mock_approve.return_value = {"approved": True}
        from src.api.v1.endpoints.teachers import approve_student_endpoint

        result = approve_student_endpoint(
            user_id=self.user_id, course_id=self.course_id, db=self.mock_db
        )
        self.assertEqual(result, {"approved": True})
        mock_approve.assert_called_once_with(self.mock_db, self.user_id, self.course_id)

    @patch("src.crud.teacher.remove_student_from_course")
    def test_remove_student_from_course_endpoint(self, mock_remove):
        mock_remove.return_value = {"removed": True}
        from src.api.v1.endpoints.teachers import remove_student_from_course_endpoint

        result = remove_student_from_course_endpoint(
            course_id=self.course_id, student_id=self.student_id, db=self.mock_db
        )
        self.assertEqual(result, {"removed": True})
        mock_remove.assert_called_once_with(self.mock_db, self.course_id, self.student_id)

    @patch("src.crud.teacher.toggle_course_visibility_by_teacher")
    def test_toggle_course_visibility(self, mock_toggle):
        mock_toggle.return_value = {"visibility": "toggled"}
        from src.api.v1.endpoints.teachers import toggle_course_visibility

        result = toggle_course_visibility(
            course_id=self.course_id, db=self.mock_db, current_user=self.current_teacher
        )
        self.assertEqual(result, {"visibility": "toggled"})
        mock_toggle.assert_called_once_with(
            self.mock_db, self.course_id, self.current_teacher
        )