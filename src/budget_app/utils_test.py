import unittest
from .utils import (
    format_float_to_usd,
    validate_request_body_keys_exist,
    stringify_attributes,
)


class FormatFloatToUsd(unittest.TestCase):
    """
    take in num and return
    with 2 leading decimals with $
    """

    def test_sucess(self):
        response = format_float_to_usd(123)
        self.assertEqual(response, "$123.00")

    def test_negative_number(self):
        response = format_float_to_usd(-123)
        self.assertEqual(response, "$-123.00")

    def test_with_2_decimal_places(self):
        response = format_float_to_usd(123.45)
        self.assertEqual(response, "$123.45")

    # if more than 2 decimal points provided
    #  rounds to nearest decimal point
    def test_decimal_round_up(self):
        response = format_float_to_usd(123.456)
        self.assertEqual(response, "$123.46")

    def test_decimal_round_down(self):
        response = format_float_to_usd(123.451)
        self.assertEqual(response, "$123.45")

    def test_4plus_digits(self):
        # add commas for 4+ digits
        response = format_float_to_usd(1234567)
        self.assertEqual(response, "$1,234,567.00")


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
