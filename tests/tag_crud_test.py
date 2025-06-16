import unittest
from unittest.mock import MagicMock
from uuid import uuid4
from src.crud import tag as tag_crud
from src.schemas.all_models import CreateTag, User
from fastapi import HTTPException


class TestTagCrud(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.tag_id = uuid4()
        self.course_id = uuid4()
        self.course = MagicMock(id=self.course_id, title="Algebra 1", tags=[])
        self.tag = MagicMock(id=self.tag_id, name="Math", courses=[self.course])

    def test_get_tags(self):
        self.db.query().all.return_value = [self.tag]
        result = tag_crud.get_tags(self.db)
        self.assertEqual(result, [self.tag])

    def test_get_tag_by_id(self):
        self.db.query().filter().first.return_value = self.tag
        result = tag_crud.get_tag_by_id(self.db, self.tag_id)
        self.assertEqual(result, self.tag)

    def test_create_tags_success(self):
        self.db.query().filter().first.return_value = None
        payload = CreateTag(name=" Science ")
        result = tag_crud.create_tags(self.db, payload)
        self.assertEqual(result.name, payload.name.strip())

    def test_create_tags_empty_name(self):
        payload = CreateTag(name="   ")
        with self.assertRaises(HTTPException) as ctx:
            tag_crud.create_tags(self.db, payload)
        self.assertEqual(ctx.exception.status_code, 400)

    def test_create_tags_already_exists(self):
        self.db.query().filter().first.return_value = self.tag
        payload = CreateTag(name="Math")
        with self.assertRaises(HTTPException) as ctx:
            tag_crud.create_tags(self.db, payload)
        self.assertEqual(ctx.exception.status_code, 400)

    def test_delete_tags_success(self):
        self.db.query().filter().first.return_value = self.tag
        result = tag_crud.delete_tags(self.db, self.tag_id)
        self.assertIn("deleted", result["message"])

    def test_delete_tags_not_found(self):
        self.db.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as ctx:
            tag_crud.delete_tags(self.db, self.tag_id)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_add_tag_to_course_success(self):
        self.course.tags = []
        self.db.query().filter().first.side_effect = [self.course, self.tag]
        result = tag_crud.add_tag_to_course(self.db, self.course_id, self.tag_id)
        self.assertIn("added", result["message"])

    def test_add_tag_to_course_already_exists(self):
        self.course.tags = [self.tag]
        self.db.query().filter().first.side_effect = [self.course, self.tag]
        with self.assertRaises(HTTPException) as ctx:
            tag_crud.add_tag_to_course(self.db, self.course_id, self.tag_id)
        self.assertEqual(ctx.exception.detail, "Tag already attached to course")

    def test_add_tag_to_course_missing_course_or_tag(self):
        self.db.query().filter().first.side_effect = [None, self.tag]
        with self.assertRaises(HTTPException) as ctx:
            tag_crud.add_tag_to_course(self.db, self.course_id, self.tag_id)
        self.assertEqual(ctx.exception.detail, "Course not found")

    def test_delete_tag_from_course_success(self):
        self.course.tags = [self.tag]
        self.db.query().filter().first.side_effect = [self.course, self.tag]
        result = tag_crud.delete_tag_from_course(self.db, self.course_id, self.tag_id)
        self.assertIn("removed", result["message"])

    def test_delete_tag_from_course_tag_not_found(self):
        self.course.tags = []
        self.db.query().filter().first.side_effect = [self.course, self.tag]
        with self.assertRaises(HTTPException) as ctx:
            tag_crud.delete_tag_from_course(self.db, self.course_id, self.tag_id)
        self.assertEqual(ctx.exception.detail, "Tag not found")

    def test_search_course_by_tag_success(self):
        self.db.query().filter().first.return_value = self.tag
        result = tag_crud.search_course_by_tag(self.db, "math")
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["title"], "Algebra 1")

    def test_search_course_by_tag_not_found(self):
        self.db.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as ctx:
            tag_crud.search_course_by_tag(self.db, "nonexistent")
        self.assertEqual(ctx.exception.status_code, 404)

    def test_return_all_tags(self):
        course_with_tags = MagicMock()
        course_with_tags.id = self.course_id
        course_with_tags.tags = [MagicMock(name="Science"), MagicMock(name="Math")]
        self.db.query().filter().all.return_value = [course_with_tags]

        result = tag_crud.return_all_tags(self.db)
        self.assertIn(str(self.course_id), result)
        self.assertIn("Math", result[str(self.course_id)])
        self.assertIn("Science", result[str(self.course_id)])