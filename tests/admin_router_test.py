import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient
from main import app
from src.api.deps import get_admin_user, get_db
from src.models.models import Role, User

client = TestClient(app)


class TestAdminRoutes(unittest.TestCase):
    def setUp(self):
        self.admin_user = User(
            id=uuid4(),
            email="admin@example.com",
            role=Role.ADMIN,
            is_active=True,
        )
        self.mock_db = MagicMock()
        self.mock_db.commit.side_effect = Exception("DB commit should not be called")
        self.mock_db.flush.side_effect = Exception("DB flush should not be called")
        self.mock_db.add.side_effect = Exception("DB add should not be called")
        self.mock_db.delete.side_effect = Exception("DB delete should not be called")

        app.dependency_overrides[get_admin_user] = lambda: self.admin_user
        app.dependency_overrides[get_db] = lambda: self.mock_db

    def tearDown(self):
        app.dependency_overrides = {}

    def test_list_users(self):
        self.mock_db.query().all.return_value = []
        response = client.get("/api/v1/admins/users")
        self.assertEqual(response.status_code, 200)

    def test_get_pending_teachers(self):
        self.mock_db.query().filter().all.return_value = []
        response = client.get("/api/v1/admins/teachers/pending")
        self.assertEqual(response.status_code, 200)

    def test_list_courses(self):
        self.mock_db.query().offset().limit().all.return_value = []
        response = client.get("/api/v1/admins/courses")
        self.assertEqual(response.status_code, 200)

    def test_list_users_with_role_filter(self):
        self.mock_db.query().all.return_value = []
        response = client.get("/api/v1/admins/users?role=student")
        self.assertEqual(response.status_code, 200)

    def test_list_users_with_search(self):
        self.mock_db.query().all.return_value = []
        response = client.get("/api/v1/admins/users?search=example")
        self.assertEqual(response.status_code, 200)

    def test_get_pending_teachers_with_results(self):
        teacher = MagicMock()
        teacher.id = uuid4()
        teacher.first_name = "T"
        teacher.last_name = "L"
        self.mock_db.query().filter().all.return_value = [teacher]

        response = client.get("/api/v1/admins/teachers/pending")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_list_courses_pagination(self):
        self.mock_db.query().offset().limit().all.return_value = []
        response = client.get("/api/v1/admins/courses?page=1&page_size=10")
        self.assertEqual(response.status_code, 200)

    def test_invalid_route(self):
        response = client.get("/api/v1/admins/unknown")
        self.assertEqual(response.status_code, 404)
