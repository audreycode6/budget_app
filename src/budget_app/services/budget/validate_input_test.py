import unittest
from random import randint
from .validate_input import validate_month_duration, validate_positive_float


class ValidateMonthDuration(unittest.TestCase):
    non_int_message = "Month duration must be a whole number (1 or 12)."

    def test_success(self):
        response = validate_month_duration("1")
        self.assertFalse(response)

        response = validate_month_duration("12")
        self.assertFalse(response)

    def test_invalid_number(self):
        invalid_num_message = "Month duration must be 1 (month) or 12 (year)."
        random_number = randint(2, 11)

        response = validate_month_duration(str(random_number))
        self.assertEqual(response, invalid_num_message)

        response = validate_month_duration("123")
        self.assertEqual(response, invalid_num_message)

    def test_not_numeric(self):
        response = validate_month_duration("one")
        self.assertEqual(response, ValidateMonthDuration.non_int_message)

        response = validate_month_duration("1 month")
        self.assertEqual(response, ValidateMonthDuration.non_int_message)

    def test_float_input(self):
        response = validate_month_duration("1.5")
        self.assertEqual(response, ValidateMonthDuration.non_int_message)


class ValidatePositiveFloat(unittest.TestCase):

    def test_success(self):
        response = validate_positive_float("123")
        self.assertFalse(response)

        response = validate_positive_float("123.456")
        self.assertFalse(response)

    def test_not_numeric(self):
        response = validate_positive_float("one hundred")
        self.assertEqual(response, "must be a valid number.")

    def test_negative_number(self):
        response = validate_positive_float("-123")
        self.assertEqual(response, "must be a non negative number.")


if __name__ == "__main__":
    unittest.main()
