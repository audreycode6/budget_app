import unittest
from .utils import (
    validate_request_body_keys_exist,
    stringify_attributes,
)


class ValidateRequestBodyKeysExist(unittest.TestCase):

    def setUp(self):
        self.test_keys = ["budget_id", "item_id", "name"]

    def test_success(self):
        test_success_body = {"budget_id": 1, "item_id": 2, "name": "foo"}
        response = validate_request_body_keys_exist(self.test_keys, test_success_body)
        self.assertTrue(response)

    def test_missing_key(self):
        test_fail_body = {"budget_id": 1, "name": "foo"}
        response = validate_request_body_keys_exist(self.test_keys, test_fail_body)
        self.assertFalse(response)

    def test_empty_body(self):
        test_empty_body = {}
        response = validate_request_body_keys_exist(self.test_keys, test_empty_body)
        self.assertFalse(response)


class StringifyAttributes(unittest.TestCase):

    def setUp(self):
        self.list_of_attributes = ["foo", "bar", "baz"]

    def test_successful_stringify(self):
        response = stringify_attributes(self.list_of_attributes)
        self.assertEqual(response, "foo, bar, baz")


if __name__ == "__main__":
    unittest.main()
