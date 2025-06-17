import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from src.models.models import User, Role, Section


class TestSectionCrud(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.section_id = uuid4()
        self.course_id = uuid4()
        self.teacher_id = uuid4()
        self.student_id = uuid4()
        self.teacher_user = User(id=self.teacher_id, role=Role.TEACHER, is_active=True)
        self.student_user = User(id=self.student_id, role=Role.STUDENT, is_active=True)
        self.optional_user = User(id=uuid4(), role=Role.STUDENT, is_active=True)

    def test_get_all_sections_returns_list(self):
        self.mock_db.query().filter().all.return_value = [Section(id=self.section_id)]
        result = section_crud.get_all_sections(self.mock_db, self.course_id, current_user=self.optional_user)
        self.assertIsInstance(result, list)

    def test_information_about_section_found(self):
        section = Section(id=self.section_id)
        self.mock_db.query().filter().first.return_value = section
        result = section_crud.information_about_section(self.mock_db, self.section_id, self.optional_user)
        self.assertEqual(result, section)

    def test_information_about_section_not_found(self):
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            section_crud.information_about_section(self.mock_db, self.section_id, self.optional_user)

    def test_add_section_to_course_success(self):
        payload = MagicMock()
        result_section = Section(id=self.section_id)
        self.mock_db.add = MagicMock()
        self.mock_db.commit = MagicMock()
        with unittest.mock.patch('src.crud.section.Section', return_value=result_section):
            result = section_crud.add_section_to_course(self.mock_db, payload, self.course_id, self.teacher_user)
            self.assertIsInstance(result, Section)

    def test_delete_section_from_course_success(self):
        section = Section(id=self.section_id)
        self.mock_db.commit = MagicMock()
        result = section_crud.delete_section_from_course(self.mock_db, section, self.teacher_user)
        self.assertIn("message", result)

    def test_update_info_about_section_success(self):
        payload = MagicMock()
        section = Section(id=self.section_id)
        self.mock_db.query().filter().first.return_value = section
        self.mock_db.commit = MagicMock()
        result = section_crud.update_info_about_section(self.mock_db, self.section_id, payload, self.teacher_user)
        self.assertEqual(result.id, self.section_id)

    def test_update_info_about_section_not_found(self):
        payload = MagicMock()
        self.mock_db.query().filter().first.return_value = None
        with self.assertRaises(Exception):
            section_crud.update_info_about_section(self.mock_db, self.section_id, payload, self.teacher_user)

    def test_mark_as_completed_success(self):
        self.mock_db.commit = MagicMock()
        result = section_crud.mark_as_completed(self.mock_db, self.section_id, self.optional_user)
        self.assertIn("message", result)

    def test_leave_section_success(self):
        self.mock_db.commit = MagicMock()
        result = section_crud.leave_section(self.mock_db, self.section_id, self.student_user)
        self.assertIn("message", result)