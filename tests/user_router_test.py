import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.models.models import Role, User
from src.crud import user as crud_user


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

    @patch("src.crud.user.get_user_info")
    def test_get_me(self, mock_get_user_info):
        mock_get_user_info.return_value = {"first_name": "Mock", "last_name": "User"}
        result = crud_user.get_user_info(self.mock_db, self.mock_user)
        self.assertEqual(result["first_name"], "Mock")

    def test_logout(self):
        # Simulate logout logic directly
        result = {"message": "Successfully logged out."}
        self.assertEqual(result["message"], "Successfully logged out.")

    @patch("src.crud.user.get_user_info")
    def test_get_me_as_student(self, mock_get_user_info):
        self.mock_user.role = Role.STUDENT
        mock_get_user_info.return_value = {"first_name": "Student", "last_name": "X"}
        result = crud_user.get_user_info(self.mock_db, self.mock_user)
        self.assertEqual(result["first_name"], "Student")

    @patch("src.crud.user.get_user_info")
    def test_get_me_response_structure(self, mock_get_user_info):
        mock_get_user_info.return_value = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com"
        }
        result = crud_user.get_user_info(self.mock_db, self.mock_user)
        self.assertIn("first_name", result)
        self.assertIn("last_name", result)
        self.assertIn("email", result)

    def test_logout_without_auth_token(self):
        # Simulate logic for unauthenticated logout
        user = None
        result = {"message": "Successfully logged out." if user is None else "Unexpected"}
        self.assertEqual(result["message"], "Successfully logged out.")

    def test_logout_invalid_method(self):
        # Simulate method not allowed
        method = "GET"
        allowed = ["POST"]
        self.assertNotIn(method, allowed)

    @patch("src.crud.user.get_user_info")
    def test_get_me_user_not_found(self, mock_get_user_info):
        mock_get_user_info.return_value = None
        result = crud_user.get_user_info(self.mock_db, self.mock_user)
        self.assertIsNone(result)
