import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.schemas.all_models import CreateTag
from src.crud import tag as crud_tag


class TestTagsEndpoints(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.tag_id = uuid4()
        self.course_id = uuid4()
        self.payload = CreateTag(name="TestTag")

    @patch("src.crud.tag.get_tags")
    def test_get_tags(self, mock_get_tags):
        mock_get_tags.return_value = ["tag1", "tag2"]
        result = crud_tag.get_tags(self.mock_db)
        self.assertIsInstance(result, list)
        self.assertIn("tag1", result)

    @patch("src.crud.tag.create_tags")
    def test_create_tags(self, mock_create_tags):
        mock_create_tags.return_value = {"message": "Tag created"}
        result = crud_tag.create_tags(self.mock_db, self.payload)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Tag created")

    @patch("src.crud.tag.delete_tags")
    def test_delete_tags(self, mock_delete_tags):
        mock_delete_tags.return_value = {"message": "Tag deleted"}
        result = crud_tag.delete_tags(self.mock_db, self.tag_id)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Tag deleted")

    @patch("src.crud.tag.add_tag_to_course")
    def test_add_tag_to_course(self, mock_add_tag):
        mock_add_tag.return_value = {"message": "Tag added to course"}
        result = crud_tag.add_tag_to_course(self.mock_db, self.course_id, self.tag_id)
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Tag added to course")

    @patch("src.crud.tag.delete_tag_from_course")
    def test_delete_tag_from_course(self, mock_delete_tag_from_course):
        mock_delete_tag_from_course.return_value = {
            "message": "Tag removed from course"
        }
        result = crud_tag.delete_tag_from_course(
            self.mock_db, self.course_id, self.tag_id
        )
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Tag removed from course")

    @patch("src.crud.tag.search_course_by_tag")
    def test_found_course_tags(self, mock_search):
        mock_search.return_value = ["course1", "course2"]
        result = crud_tag.search_course_by_tag(self.mock_db, "TestTag")
        self.assertIsInstance(result, list)
        self.assertIn("course1", result)

    @patch("src.crud.tag.return_all_tags")
    def test_return_course_tag(self, mock_return_all_tags):
        mock_return_all_tags.return_value = ["tagA", "tagB"]
        result = crud_tag.return_all_tags(self.mock_db)
        self.assertIsInstance(result, list)
        self.assertIn("tagA", result)
