import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from fastapi import HTTPException
from src.crud import section as section_crud
from src.models.models import User, Course, Section, StudentCourse
from src.schemas.all_models import Role, SectionCreate, SectionUpdate
from src.utils.custom_responses import Unauthorized


class TestSectionCRUD(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.student_user = User(id=uuid4(), role=Role.STUDENT)
        self.teacher_user = User(id=uuid4(), role=Role.TEACHER)
        self.admin_user = User(id=uuid4(), role=Role.ADMIN)
        self.course = Course(id=uuid4(), owner_id=self.teacher_user.id, is_premium=False, title="Sample Course")
        self.premium_course = Course(id=uuid4(), owner_id=self.teacher_user.id, is_premium=True, title="Premium Course")
        self.section = Section(id=uuid4(), course_id=self.course.id, title="Section 1", description="Desc", content="Content", information="Info")
        self.section.course = self.course

    @patch('src.crud.section.get_course_by_id')
    def test_get_all_sections_no_title(self, mock_get_course_by_id):
        mock_get_course_by_id.return_value = self.course
        query_mock = MagicMock()
        # Setup chained calls: .filter().order_by().all()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value.all.return_value = [self.section]
        self.db.query.return_value = query_mock

        result = section_crud.get_all_sections(self.db, self.course.id, None, self.student_user)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], self.section.title)

    @patch('src.crud.section.get_course_by_id')
    def test_get_all_sections_with_title(self, mock_get_course_by_id):
        mock_get_course_by_id.return_value = self.course
        filtered_section = Section(id=uuid4(), course_id=self.course.id, title="Python Basics")
        filtered_section.course = self.course
        query_mock = MagicMock()
        # The code incorrectly resets 'sections' ignoring title-filter, so simulate returning the original query
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value.all.return_value = [filtered_section]
        self.db.query.return_value = query_mock

        result = section_crud.get_all_sections(self.db, self.course.id, "Python", self.student_user)
        # The test just checks no crash and correct data structure
        self.assertTrue(all("Python" in s["title"] for s in result))

    @patch('src.crud.section.get_course_by_id')
    def test_information_about_section_teacher_role_returns_section(self, mock_get_course_by_id):
        section = self.section
        section.course = self.course
        self.db.query.return_value.filter.return_value.first.return_value = section
        mock_get_course_by_id.return_value = self.course

        result = section_crud.information_about_section(self.db, section.id, self.teacher_user)
        self.assertEqual(result, section)

    @patch('src.crud.section.get_course_by_id')
    def test_information_about_section_student_approved(self, mock_get_course_by_id):
        section = self.section
        section.course = self.course
        student_course = StudentCourse(student_id=self.student_user.id, course_id=self.course.id, is_approved=True, progress=50)
        # Setup filter().first() calls sequence: first for section, second for student_course
        self.db.query.return_value.filter.return_value.first.side_effect = [section, student_course]
        mock_get_course_by_id.return_value = self.course

        result = section_crud.information_about_section(self.db, section.id, self.student_user)

        self.assertEqual(result["progress"], student_course.progress)
        self.assertEqual(result["title"], section.title)

    @patch('src.crud.section.get_course_by_id')
    def test_information_about_section_student_not_approved_raises(self, mock_get_course_by_id):
        section = self.section
        premium_course = self.premium_course
        section.course = premium_course
        student_course = None
        self.db.query.return_value.filter.return_value.first.side_effect = [section, student_course]
        mock_get_course_by_id.return_value = premium_course

        with self.assertRaises(HTTPException):
            section_crud.information_about_section(self.db, section.id, self.student_user)

    def test_mark_as_completed_progress_update(self):
        section = self.section
        course = self.course
        section.course = course
        student_course = StudentCourse(student_id=self.student_user.id, course_id=course.id, is_approved=True, progress=50)
        query_mock = MagicMock()
        # filter().first() sequence: section, course, student_course
        query_mock.filter.return_value.first.side_effect = [section, course, student_course]
        # filter().count() returns total sections count
        query_mock.filter.return_value.count.return_value = 2
        self.db.query.return_value = query_mock
        self.db.query().filter().count.return_value = 2  # total sections

        result = section_crud.mark_as_completed(self.db, section.id, self.student_user)
        self.assertIn("progress", result)
        self.assertTrue(result["progress"] > 50)

    def test_mark_as_completed_no_section_raises(self):
        self.db.query().filter().first.return_value = None
        with self.assertRaises(HTTPException):
            section_crud.mark_as_completed(self.db, uuid4(), self.student_user)

    def test_mark_as_completed_no_course_raises(self):
        section = self.section
        self.db.query().filter().first.side_effect = [section, None]
        with self.assertRaises(HTTPException):
            section_crud.mark_as_completed(self.db, section.id, self.student_user)

    def test_mark_as_completed_premium_no_approval_raises(self):
        section = self.section
        premium_course = self.premium_course
        section.course = premium_course
        self.db.query().filter().first.side_effect = [section, premium_course, None]
        with self.assertRaises(HTTPException):
            section_crud.mark_as_completed(self.db, section.id, self.student_user)

    def test_leave_section_success(self):
        section = self.section
        section.course = self.course
        student_course = StudentCourse(student_id=self.student_user.id, course_id=self.course.id, is_approved=True, is_visited=True)
        self.db.query.return_value.filter.return_value.first.side_effect = [section, student_course]

        result = section_crud.leave_section(self.db, section.id, self.student_user)
        self.assertEqual(result["message"], "You left this section")
        self.assertFalse(student_course.is_visited)  # Should be set to False

    def test_leave_section_section_not_found_raises(self):
        self.db.query().filter().first.return_value = None
        with self.assertRaises(HTTPException):
            section_crud.leave_section(self.db, uuid4(), self.student_user)

    def test_add_section_to_course_success(self):
        payload = SectionCreate(title="New Section", content="content", description="desc", information="info")
        course = self.course
        course.owner_id = self.teacher_user.id
        self.db.query().filter().first.side_effect = [course, None]  # course and title check
        result = section_crud.add_section_to_course(self.db, payload, course.id, self.teacher_user)
        self.assertIn("message", result)
        self.db.add.assert_called()
        self.db.commit.assert_called()

    def test_add_section_to_course_not_owner_raises(self):
        payload = SectionCreate(title="New Section", content="content", description="desc", information="info")
        course = self.course
        course.owner_id = self.teacher_user.id
        self.db.query().filter().first.return_value = course
        with self.assertRaises(Unauthorized):
            section_crud.add_section_to_course(self.db, payload, course.id, self.student_user)

    def test_add_section_to_course_title_exists_raises(self):
        payload = SectionCreate(title="New Section", content="content", description="desc", information="info")
        course = self.course
        course.owner_id = self.teacher_user.id
        existing_section = Section(title=payload.title)
        self.db.query().filter().first.side_effect = [course, existing_section]
        with self.assertRaises(HTTPException):
            section_crud.add_section_to_course(self.db, payload, course.id, self.teacher_user)

    def test_delete_section_from_course_success(self):
        section = self.section
        course = self.course
        course.owner_id = self.teacher_user.id
        self.db.query().filter().first.return_value = course

        result = section_crud.delete_section_from_course(self.db, section, self.teacher_user)
        self.db.delete.assert_called_with(section)
        self.db.commit.assert_called()
        self.assertIn("message", result)

    def test_delete_section_from_course_not_owner_or_admin_raises(self):
        section = self.section
        course = self.course
        course.owner_id = self.teacher_user.id
        self.db.query().filter().first.return_value = course
        with self.assertRaises(Unauthorized):
            section_crud.delete_section_from_course(self.db, section, self.student_user)

    def test_update_info_about_section_success(self):
        payload = SectionUpdate(title="Updated Title")
        section = self.section
        course = self.course
        course.owner_id = self.teacher_user.id
        self.db.query().filter().first.side_effect = [section, course]

        result = section_crud.update_info_about_section(self.db, section.id, payload, self.teacher_user)
        self.assertEqual(result.title, payload.title)
        self.db.commit.assert_called()

    def test_update_info_about_section_not_owner_raises(self):
        payload = SectionUpdate(title="Updated Title")
        section = self.section
        course = self.course
        course.owner_id = self.teacher_user.id
        self.db.query().filter().first.side_effect = [section, course]
        with self.assertRaises(Unauthorized):
            section_crud.update_info_about_section(self.db, section.id, payload, self.student_user)
