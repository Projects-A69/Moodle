import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient
from main import app
from src.api.deps import get_admin_user, get_db
from src.models.models import Role, User
from src.utils.token_utils import verify_approval_token

client = TestClient(app)


class TestAdminRoutes(unittest.TestCase):
    def setUp(self):
        self.admin_user = User(
            id=uuid4(),
            email="admin@example.com",
            role=Role.ADMIN,
            is_active=True
        )
        self.mock_db = MagicMock()
        app.dependency_overrides[get_admin_user] = lambda: self.admin_user
        app.dependency_overrides[get_db] = lambda: self.mock_db

    def tearDown(self):
        app.dependency_overrides = {}

    def test_list_users(self):
        self.mock_db.query().all.return_value = []
        response = client.get("/api/v1/admins/users")
        self.assertEqual(response.status_code, 200)

    def test_toggle_user_status(self):
        self.mock_db.query().filter().first.return_value = self.admin_user
        response = client.put(f"/api/v1/admins/users/{self.admin_user.id}/status")
        self.assertEqual(response.status_code, 200)

    def test_get_pending_teachers(self):
        self.mock_db.query().filter().all.return_value = []
        response = client.get("/api/v1/admins/teachers/pending")
        self.assertEqual(response.status_code, 200)

    def test_approve_teacher(self):
        self.mock_db.query().filter().first.return_value = self.admin_user
        response = client.put(f"/api/v1/admins/teachers/{self.admin_user.id}/approval")
        self.assertEqual(response.status_code, 400)

    def test_approve_teacher_by_token_valid(self):
        app.dependency_overrides[verify_approval_token] = lambda token: self.admin_user.id
        self.mock_db.query().filter().first.return_value = self.admin_user

        response = client.get("/api/v1/admins/teachers/approval?token=validtoken")
        self.assertEqual(response.status_code, 400)

    def test_list_courses(self):
        self.mock_db.query().offset().limit().all.return_value = []
        response = client.get("/api/v1/admins/courses")
        self.assertEqual(response.status_code, 200)

    def test_update_course_visability(self):
        course = MagicMock()
        course.is_hidden = False
        course.students = []
        self.mock_db.query().filter().first.return_value = course
        response = client.put(f"/api/v1/admins/courses/{uuid4()}/visability")
        self.assertEqual(response.status_code, 200)

    def test_delete_course(self):
        course = MagicMock()
        course.students = []
        self.mock_db.query().filter().first.side_effect = [course]
        response = client.delete(f"/api/v1/admins/courses/{uuid4()}")
        self.assertEqual(response.status_code, 200)

    def test_remove_student_from_course(self):
        self.mock_db.query().filter().first.side_effect = [MagicMock(), MagicMock(), MagicMock()]
        response = client.delete(f"/api/v1/admins/courses/{uuid4()}/students/{uuid4()}")
        self.assertEqual(response.status_code, 200)

    def test_get_course_ratings(self):
        mock_student_course = MagicMock()
        mock_student_course.score = 4.5
        mock_student_course.student_id = uuid4()
        mock_student_course.student = MagicMock()
        mock_student_course.student.first_name = "S"
        mock_student_course.student.last_name = "L"

        self.mock_db.query().filter().all.return_value = [mock_student_course]
        self.mock_db.query().filter().first.return_value = mock_student_course.student

        response = client.get(f"/api/v1/admins/courses/{uuid4()}/ratings")
        self.assertEqual(response.status_code, 200)
