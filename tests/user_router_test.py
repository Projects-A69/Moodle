import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from uuid import uuid4

from main import app
from src.api.deps import get_current_user, get_db
from src.models.models import Role, User

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
        self.mock_db.commit.side_effect = Exception("DB commit should not be called")
        self.mock_db.flush.side_effect = Exception("DB flush should not be called")
        self.mock_db.add.side_effect = Exception("DB add should not be called")
        self.mock_db.delete.side_effect = Exception("DB delete should not be called")

        app.dependency_overrides[get_current_user] = lambda: self.mock_user
        app.dependency_overrides[get_db] = lambda: self.mock_db

    def tearDown(self):
        app.dependency_overrides = {}

    def test_login_invalid_credentials(self):
        self.mock_db.query().filter().first.return_value = None
        response = client.post(
            "/api/v1/users/login",
            data={"username": "invalid@example.com", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 400)


    def test_get_me(self):
        self.mock_db.query().filter().first.return_value = MagicMock(first_name="Mock")
        response = client.get("/api/v1/users/me")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = client.post("/api/v1/users/logout")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Successfully logged out.")

    def test_get_me_as_student(self):
        self.mock_user.role = Role.STUDENT
        self.mock_db.query().filter().first.return_value = MagicMock(first_name="Student")
        response = client.get("/api/v1/users/me")
        self.assertEqual(response.status_code, 200)

    def test_get_me_response_structure(self):
        self.mock_db.query().filter().first.return_value = MagicMock(first_name="Test", last_name="User")
        response = client.get("/api/v1/users/me")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("first_name", data)
        self.assertIn("last_name", data)
        
    def test_logout_without_auth_token(self):
        app.dependency_overrides[get_current_user] = lambda: None
        response = client.post("/api/v1/users/logout")
        self.assertEqual(response.status_code, 200)

    def test_logout_invalid_method(self):
        response = client.get("/api/v1/users/logout")
        self.assertEqual(response.status_code, 405)
        
    def test_get_me_user_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        response = client.get("/api/v1/users/me")
        self.assertEqual(response.status_code, 200)

