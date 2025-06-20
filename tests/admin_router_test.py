import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from src.models.models import Role, User
from src.crud import admin  # your admin CRUD module


class TestAdminRoutes(unittest.TestCase):
    def setUp(self):
        self.admin_user = User(
            id=uuid4(),
            email="admin@example.com",
            role=Role.ADMIN,
            is_active=True,
        )
        self.mock_db = MagicMock()

    def test_list_users_no_filters(self):
        # Simulate no users found
        self.mock_db.query().all.return_value = []
        result = admin.list_all_users(self.mock_db, role=None, search=None)
        self.assertIsInstance(result, list)

    def test_list_users_with_role_filter(self):
        self.mock_db.query().all.return_value = []
        result = admin.list_all_users(self.mock_db, role="student", search=None)
        self.assertIsInstance(result, list)

    def test_list_users_with_search(self):
        self.mock_db.query().all.return_value = []
        result = admin.list_all_users(self.mock_db, role=None, search="example")
        self.assertIsInstance(result, list)

    def test_get_pending_teachers_empty(self):
        self.mock_db.query().filter().all.return_value = []
        result = admin.list_pending_teachers(self.mock_db)
        self.assertIsInstance(result, list)

    def test_get_pending_teachers_with_data(self):
        teacher = MagicMock()
        teacher.id = uuid4()
        teacher.first_name = "Test"
        teacher.last_name = "User"
        self.mock_db.query().filter().all.return_value = [teacher]
        result = admin.list_pending_teachers(self.mock_db)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    def test_list_courses_empty(self):
        self.mock_db.query().offset().limit().all.return_value = []
        result = admin.list_all_courses(
            self.mock_db, teacher_id=None, student_id=None, title=None
        )
        self.assertIsInstance(result, list)

    def test_list_courses_with_pagination_params(self):
        self.mock_db.query().offset().limit().all.return_value = []
        # The pagination params are actually handled in the route, CRUD takes filters
        result = admin.list_all_courses(
            self.mock_db, teacher_id=None, student_id=None, title=None
        )
        self.assertIsInstance(result, list)

    def test_update_user_status_success(self):
        # Mock user found and updated
        user_mock = MagicMock()
        self.mock_db.query().filter().first.return_value = user_mock
        result = admin.update_user_active(self.mock_db, user_mock.id)
        self.assertIn("message", result)
        self.mock_db.commit.assert_called()

    def test_update_user_status_user_not_found_raises(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            admin.update_user_active(self.mock_db, uuid4())

    def test_approve_teacher_by_id_not_found_raises(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            admin.approve_teacher_by_id(self.mock_db, uuid4())

    def test_toggle_course_visability_success(self):
        course_mock = MagicMock()
        course_mock.is_hidden = False
        self.mock_db.query().filter().first.return_value = course_mock
        result = admin.toggle_course_visability(self.mock_db, course_mock.id)
        self.assertIn("message", result)
        self.assertEqual(course_mock.is_hidden, True)
        self.mock_db.commit.assert_called()

    def test_toggle_course_visability_not_found_raises(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            admin.toggle_course_visability(self.mock_db, uuid4())

    def test_delete_course_success(self):
        course_mock = MagicMock()
        self.mock_db.query().filter().first.return_value = course_mock
        result = admin.delete_course(self.mock_db, course_mock.id)
        self.assertIn("message", result)
        self.mock_db.delete.assert_called_with(course_mock)
        self.mock_db.commit.assert_called()

    def test_delete_course_not_found_raises(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            admin.delete_course(self.mock_db, uuid4())

    def test_remove_student_from_course_success(self):
        student_course_mock = MagicMock()
        self.mock_db.query().filter().first.return_value = student_course_mock
        result = admin.remove_student_from_course(self.mock_db, uuid4(), uuid4())
        self.assertIn("message", result)
        self.mock_db.delete.assert_called_with(student_course_mock)
        self.mock_db.commit.assert_called()

    def test_remove_student_from_course_not_found_raises(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            admin.remove_student_from_course(self.mock_db, uuid4(), uuid4())

    def test_get_course_ratings_empty(self):
        self.mock_db.query().filter().all.return_value = []
        result = admin.get_course_ratings(self.mock_db, uuid4())
        self.assertIsInstance(result, list)

    def test_invalid_route_raises(self):
        with self.assertRaises(AttributeError):
            getattr(admin, "invalid_route")()
