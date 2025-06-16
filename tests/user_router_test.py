import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from uuid import uuid4

from main import app
from src.models.models import Role, User
from src.api.deps import get_current_user, get_db

client = TestClient(app)


class TestUserRoutes(unittest.TestCase):
    def setUp(self):
        self.mock_user = User(
            id=uuid4(),
            email="user@example.com",
            password="hashed",
            role=Role.ADMIN,
            is_active=True,
        )
        self.mock_db = MagicMock()
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
        app.dependency_overrides[get_db] = lambda: self.mock_db

    def tearDown(self):
        app.dependency_overrides = {}

    @patch("src.api.deps.get_db")
    def test_login_invalid_credentials(self, mock_db):
        mock_db.return_value.query().filter().first.return_value = None
        response = client.post(
            "/api/v1/users/login",
            data={"username": "invalid@example.com", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 400)

    def test_get_me(self):
        self.mock_db.query().filter().first.return_value = MagicMock(first_name="F")
        response = client.get("/api/v1/users/me")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = client.post("/api/v1/users/logout")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Successfully logged out.")

    def test_update_me_admin(self):
        self.mock_db.query().filter().first.return_value = MagicMock()
        response = client.put(
            "/api/v1/users/me/admin",
            data={"first_name": "Updated", "last_name": "User", "password": "newpass"},
        )
        self.assertEqual(response.status_code, 200)

    def test_update_me_teacher(self):
        self.mock_user.role = Role.TEACHER
        self.mock_db.query().filter().first.return_value = MagicMock()
        response = client.put(
            "/api/v1/users/me/teacher",
            data={
                "first_name": "John",
                "last_name": "Doe",
                "password": "123",
                "phone_number": "123456789",
                "linked_in_acc": "https://linkedin.com/in/test",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_update_me_student(self):
        self.mock_user.role = Role.STUDENT
        self.mock_db.query().filter().first.return_value = MagicMock()
        response = client.put(
            "/api/v1/users/me/student",
            data={"first_name": "Alice", "last_name": "Smith", "password": "pass123"},
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_account(self):
        self.mock_db.query().filter().first.return_value = self.mock_user
        response = client.delete("/api/v1/users/delete")
        self.assertEqual(response.status_code, 200)

    def test_register_admin(self):
        self.mock_db.query().filter().first.return_value = None
        response = client.post(
            "/api/v1/users/register/admin",
            data={
                "first_name": "Admin",
                "last_name": "User",
                "email": "admin@example.com",
                "password": "123",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_register_teacher(self):
        self.mock_db.query().filter().first.return_value = None
        with patch("src.utils.s3.upload_image_to_s3", return_value=None):
            response = client.post(
                "/api/v1/users/register/teacher",
                data={
                    "first_name": "T",
                    "last_name": "T",
                    "email": "t@example.com",
                    "password": "123",
                    "phone_number": "123456789",
                    "linked_in_acc": "https://linkedin.com/in/test",
                },
            )
        self.assertEqual(response.status_code, 200)

    def test_register_student(self):
        self.mock_db.query().filter().first.return_value = None
        with patch("src.utils.s3.upload_image_to_s3", return_value=None):
            response = client.post(
                "/api/v1/users/register/student",
                data={
                    "first_name": "S",
                    "last_name": "S",
                    "email": "s@example.com",
                    "password": "123",
                },
            )
        self.assertEqual(response.status_code, 200)
