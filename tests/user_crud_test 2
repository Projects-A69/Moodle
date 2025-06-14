import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.crud import user as user_crud
from src.schemas.all_models import (
    AdminCreate,
    LoginRequest,
    StudentCreate,
    TeacherCreate,
)
from src.models.models import Role, User, Admin, Student, Teacher


class TestUserCrud(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.user_id = uuid4()
        self.mock_user = User(id=self.user_id, email="test@example.com", password="hashed", role=Role.ADMIN, is_active=True)

    def test_get_by_id_success(self):
        self.mock_db.query().filter().first.return_value = self.mock_user
        user = user_crud.get_by_id(self.mock_db, self.user_id)
        self.assertEqual(user.email, "test@example.com")

    def test_get_by_id_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            user_crud.get_by_id(self.mock_db, self.user_id)

    def test_get_by_email_found(self):
        self.mock_db.query().filter().first.return_value = self.mock_user
        user = user_crud.get_by_email(self.mock_db, "test@example.com")
        self.assertEqual(user.email, "test@example.com")

    def test_get_by_email_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        user = user_crud.get_by_email(self.mock_db, "missing@example.com")
        self.assertIsNone(user)

    def test_get_by_email_case_insensitive(self):
        self.mock_db.query().filter().first.return_value = self.mock_user
        user = user_crud.get_by_email(self.mock_db, "Test@Example.com")
        self.assertEqual(user.email, "test@example.com")

    @patch("src.crud.user.verify_password", return_value=True)
    def test_login_user_success(self, mock_verify):
        self.mock_db.query().filter().first.return_value = self.mock_user
        payload = LoginRequest(email="test@example.com", password="secret")
        user = user_crud.login_user(self.mock_db, payload)
        self.assertEqual(user.email, "test@example.com")

    @patch("src.crud.user.verify_password", return_value=False)
    def test_login_user_wrong_password(self, mock_verify):
        self.mock_db.query().filter().first.return_value = self.mock_user
        payload = LoginRequest(email="test@example.com", password="wrong")
        with self.assertRaises(Exception):
            user_crud.login_user(self.mock_db, payload)

    def test_login_user_inactive(self):
        inactive_user = User(email="test@example.com", password="hashed", role=Role.ADMIN, is_active=False)
        self.mock_db.query().filter().first.return_value = inactive_user
        payload = LoginRequest(email="test@example.com", password="123")
        with patch("src.crud.user.verify_password", return_value=True):
            with self.assertRaises(Exception):
                user_crud.login_user(self.mock_db, payload)

    @patch("src.crud.user.verify_password")
    def test_login_calls_verify_password(self, mock_verify):
        mock_verify.return_value = True
        self.mock_db.query().filter().first.return_value = self.mock_user
        payload = LoginRequest(email="test@example.com", password="secret")
        user_crud.login_user(self.mock_db, payload)
        mock_verify.assert_called_once_with("secret", self.mock_user.password)

    @patch("src.crud.user.hash_password", return_value="hashed")
    def test_register_admin(self, mock_hash):
        payload = AdminCreate(email="admin@example.com", password="123", first_name="A", last_name="B")
        self.mock_db.flush = MagicMock()
        self.mock_db.commit = MagicMock()
        result = user_crud.register_admin(self.mock_db, payload)
        self.assertEqual(result["role"], Role.ADMIN)

    def test_register_admin_missing_fields(self):
        payload = AdminCreate(email="admin@example.com", password="123", first_name="", last_name="")
        with self.assertRaises(Exception):
            user_crud.register_admin(self.mock_db, payload)

    @patch("src.crud.user.hash_password", return_value="hashed")
    @patch("src.crud.user.send_email")
    @patch("src.crud.user.generate_approval_token", return_value="abc123")
    def test_register_teacher(self, mock_token, mock_email, mock_hash):
        payload = TeacherCreate(
            email="teacher@example.com",
            password="123",
            first_name="T",
            last_name="T",
            phone_number="123456789",
            linked_in_acc="linkedin.com",
            profile_picture=None,
        )
        self.mock_db.flush = MagicMock()
        self.mock_db.commit = MagicMock()
        result = user_crud.register_teacher(self.mock_db, payload)
        self.assertEqual(result["role"], Role.TEACHER)

    def test_register_teacher_missing_fields(self):
        incomplete = TeacherCreate(
            email="teacher@example.com",
            password="123",
            first_name="",
            last_name="",
            phone_number="",
            linked_in_acc="",
            profile_picture=None,
        )
        with self.assertRaises(Exception):
            user_crud.register_teacher(self.mock_db, incomplete)

    @patch("src.crud.user.hash_password", return_value="hashed")
    @patch("src.crud.user.send_email")
    @patch("src.crud.user.generate_approval_token", return_value="abc123")
    def test_register_teacher_email_contains_token(self, mock_token, mock_email, mock_hash):
        payload = TeacherCreate(
            email="teacher@example.com",
            password="123",
            first_name="John",
            last_name="Doe",
            phone_number="123456789",
            linked_in_acc="linkedin.com",
            profile_picture=None,
        )
        self.mock_db.flush = MagicMock()
        self.mock_db.commit = MagicMock()
        user_crud.register_teacher(self.mock_db, payload)
        body = mock_email.call_args.kwargs["body"]
        self.assertIn("abc123", body)
        self.assertIn("approve", body)

    @patch("src.crud.user.hash_password", return_value="hashed")
    def test_register_student(self, mock_hash):
        payload = StudentCreate(
            email="student@example.com",
            password="123",
            first_name="S",
            last_name="S",
            profile_picture=None,
        )
        self.mock_db.flush = MagicMock()
        self.mock_db.commit = MagicMock()
        result = user_crud.register_student(self.mock_db, payload)
        self.assertEqual(result["role"], Role.STUDENT)

    def test_register_student_missing_fields(self):
        payload = StudentCreate(
            email="student@example.com",
            password="123",
            first_name="",
            last_name="",
            profile_picture=None,
        )
        with self.assertRaises(Exception):
            user_crud.register_student(self.mock_db, payload)

    def test_get_user_info_admin(self):
        admin = Admin(id=self.user_id, first_name="A", last_name="B")
        self.mock_db.query().filter().first.return_value = admin
        info = user_crud.get_user_info(self.mock_db, self.mock_user)
        self.assertEqual(info["first_name"], "A")

    def test_get_user_info_teacher(self):
        self.mock_user.role = Role.TEACHER
        teacher = Teacher(id=self.user_id, first_name="T", last_name="T", phone_number="123", linked_in_acc="acc", profile_picture=None)
        self.mock_db.query().filter().first.return_value = teacher
        info = user_crud.get_user_info(self.mock_db, self.mock_user)
        self.assertEqual(info["phone_number"], "123")

    def test_get_user_info_student(self):
        self.mock_user.role = Role.STUDENT
        student = Student(id=self.user_id, first_name="S", last_name="S", profile_picture=None)
        self.mock_db.query().filter().first.return_value = student
        info = user_crud.get_user_info(self.mock_db, self.mock_user)
        self.assertEqual(info["last_name"], "S")

    @patch("src.crud.user.hash_password", return_value="hashed")
    def test_update_admin_info(self, mock_hash):
        payload = MagicMock(password="new", first_name="A", last_name="B")
        admin = Admin(id=self.user_id, first_name="X", last_name="Y")
        self.mock_db.query().filter().first.return_value = admin
        self.mock_db.commit = MagicMock()
        result = user_crud.update_admin_info(self.mock_db, self.mock_user, payload)
        self.assertEqual(result["first_name"], "A")

    def test_update_admin_info_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        payload = MagicMock(password=None, first_name="A", last_name="B")
        with self.assertRaises(Exception):
            user_crud.update_admin_info(self.mock_db, self.mock_user, payload)

    @patch("src.crud.user.hash_password", return_value="hashed")
    def test_update_teacher_info(self, mock_hash):
        self.mock_user.role = Role.TEACHER
        payload = MagicMock(password="new", first_name="T", last_name="T", phone_number="123", linked_in_acc="acc", profile_picture="pic")
        teacher = Teacher(id=self.user_id, first_name="X", last_name="Y", phone_number="000", linked_in_acc="link", profile_picture="old")
        self.mock_db.query().filter().first.return_value = teacher
        self.mock_db.commit = MagicMock()
        result = user_crud.update_teacher_info(self.mock_db, self.mock_user, payload)
        self.assertEqual(result["first_name"], "T")

    def test_update_teacher_info_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        payload = MagicMock(password=None, first_name="T", last_name="T", phone_number="123", linked_in_acc="acc", profile_picture="pic")
        with self.assertRaises(Exception):
            user_crud.update_teacher_info(self.mock_db, self.mock_user, payload)

    @patch("src.crud.user.hash_password", return_value="hashed")
    def test_update_student_info(self, mock_hash):
        self.mock_user.role = Role.STUDENT
        payload = MagicMock(password="new", first_name="S", last_name="S", profile_picture="pic")
        student = Student(id=self.user_id, first_name="X", last_name="Y", profile_picture="old")
        self.mock_db.query().filter().first.return_value = student
        self.mock_db.commit = MagicMock()
        result = user_crud.update_student_info(self.mock_db, self.mock_user, payload)
        self.assertEqual(result["first_name"], "S")

    def test_update_student_info_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        payload = MagicMock(password="new", first_name="S", last_name="S", profile_picture="pic")
        with self.assertRaises(Exception):
            user_crud.update_student_info(self.mock_db, self.mock_user, payload)

    def test_delete_user(self):
        self.mock_db.query().filter().first.return_value = self.mock_user
        self.mock_db.delete = MagicMock()
        self.mock_db.commit = MagicMock()
        result = user_crud.delete_user(self.mock_db, self.user_id)
        self.assertEqual(result["message"], "Account deleted successfully.")

    def test_delete_user_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            user_crud.delete_user(self.mock_db, self.user_id)
