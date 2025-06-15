import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from src.models.models import Role, User, Teacher, Student, Course, StudentCourse
from src.crud import admin as admin_crud


class TestAdminCrud(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.user_id = uuid4()
        self.course_id = uuid4()
        self.student_id = uuid4()

        self.mock_admin = User(
            id=self.user_id, email="admin@example.com", role=Role.ADMIN, is_active=True
        )
        self.mock_teacher = User(
            id=self.user_id,
            email="teacher@example.com",
            role=Role.TEACHER,
            is_active=True,
            is_approved=False,
        )
        self.mock_student = User(
            id=self.user_id,
            email="student@example.com",
            role=Role.STUDENT,
            is_active=True,
        )

    def test_list_all_users_no_filters(self):
        self.mock_db.query().all.return_value = [self.mock_admin]
        result = admin_crud.list_all_users(self.mock_db)
        self.assertIsInstance(result, list)

    def test_list_all_users_invalid_role(self):
        with self.assertRaises(Exception):
            admin_crud.list_all_users(self.mock_db, role="INVALID")

    def test_update_user_active_toggle(self):
        self.mock_db.query().filter().first.return_value = self.mock_admin
        result = admin_crud.update_user_active(self.mock_db, self.user_id)
        self.assertIn("message", result)

    def test_list_pending_teachers(self):
        teacher = Teacher(
            id=self.user_id,
            first_name="T",
            last_name="T",
            linked_in_acc="linkedin",
            profile_picture=None,
            phone_number="123",
        )
        self.mock_teacher.teacher = teacher
        self.mock_db.query().filter().all.return_value = [self.mock_teacher]
        result = admin_crud.list_pending_teachers(self.mock_db)
        self.assertIsInstance(result, list)

    def test_approve_teacher_by_id(self):
        self.mock_teacher.is_approved = False
        self.mock_db.query().filter().first.return_value = self.mock_teacher
        result = admin_crud.approve_teacher_by_id(self.mock_db, self.user_id)
        self.assertEqual(result["message"], "Teacher approved successfully")

    def test_approve_teacher_already_approved(self):
        self.mock_teacher.is_approved = True
        self.mock_db.query().filter().first.return_value = self.mock_teacher
        result = admin_crud.approve_teacher_by_id(self.mock_db, self.user_id)
        self.assertEqual(result["message"], "Teacher is already approved")

    def test_list_all_courses_empty(self):
        self.mock_db.query().offset().limit().all.return_value = []
        result = admin_crud.list_all_courses(self.mock_db)
        self.assertIsInstance(result, list)

    def test_toggle_course_visibility(self):
        course = Course(
            id=self.course_id, title="Course A", is_hidden=False, students=[]
        )
        self.mock_db.query().filter().first.return_value = course
        result = admin_crud.toggle_course_visability(self.mock_db, self.course_id)
        self.assertIn("message", result)

    def test_delete_course_successfully(self):
        course = Course(id=self.course_id, title="Course A", students=[])
        self.mock_db.query().filter().first.side_effect = [course]
        self.mock_db.flush = MagicMock()
        self.mock_db.commit = MagicMock()
        result = admin_crud.delete_course(self.mock_db, self.course_id)
        self.assertIn("message", result)

    def test_remove_student_from_course(self):
        student = Student(id=self.student_id, first_name="S", last_name="L")
        course = Course(id=self.course_id, title="C")
        self.mock_db.query().filter().first.side_effect = [
            StudentCourse(),
            student,
            course,
        ]
        result = admin_crud.remove_student_from_course(
            self.mock_db, self.course_id, self.student_id
        )
        self.assertIn("message", result)

    def test_get_course_ratings(self):
        student = Student(id=self.student_id, first_name="S", last_name="T")
        student_course = StudentCourse(
            course_id=self.course_id, score=4.5, student_id=self.student_id
        )
        student_course.student = student
        self.mock_db.query().filter().all.return_value = [student_course]
        self.mock_db.query().filter().first.return_value = student

        result = admin_crud.get_course_ratings(self.mock_db, self.course_id)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["student_id"], str(self.student_id))

    def test_approve_teacher_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            admin_crud.approve_teacher_by_id(self.mock_db, self.user_id)

    def test_approve_teacher_wrong_role(self):
        user = User(id=self.user_id, role=Role.STUDENT, is_active=True)
        self.mock_db.query().filter().first.return_value = user
        with self.assertRaises(Exception):
            admin_crud.approve_teacher_by_id(self.mock_db, self.user_id)

    def test_get_course_ratings_not_found(self):
        self.mock_db.query().filter().all.return_value = []
        with self.assertRaises(Exception):
            admin_crud.get_course_ratings(self.mock_db, self.course_id)

    def test_toggle_course_visibility_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            admin_crud.toggle_course_visability(self.mock_db, self.course_id)

    def test_remove_student_not_enrolled(self):
        self.mock_db.query().filter().first.side_effect = [None, None, None]
        with self.assertRaises(Exception):
            admin_crud.remove_student_from_course(
                self.mock_db, self.course_id, self.student_id
            )

    def test_delete_course_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            admin_crud.delete_course(self.mock_db, self.course_id)
