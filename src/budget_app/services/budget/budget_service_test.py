import unittest

from budget_app import create_app
from budget_app.models import Budget, BudgetItem
from budget_app.services.budget.budget_service import (
    attributes_to_update_dict,
    create_new_budget,
    create_new_budget_item,
    delete_budget,
    delete_budget_item,
    edit_budget,
    edit_budget_item,
    get_budget,
    get_user_budgets,
)
from ...extensions import db
import re


class BaseTestCase(unittest.TestCase):
    """
    Creates an application context object,
    activates that context, telling Flask “everything that runs now belongs to this app.”
    Creates all database tables inside that context.
    """

    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            }
        )
        self.client = self.app.test_client()

        self.context = self.app.app_context()  # creates an application context object
        self.context.push()  # activates that context
        db.create_all()

    def tearDown(self):
        """
        Clear the current database session,
        drops all tables (each test starts fresh with a clean in-memory DB).
        Deactivates the app context,so Flask doesn’t think your test app is
        still active after the test ends.
        """
        db.session.remove()  # clears current database session
        db.drop_all()  # drops all tables
        self.context.pop()  # deactivates the app context

    def create_budget(
        self, user_id=10, name="default", month_duration="1", gross_income="3500"
    ):
        budget = Budget(
            user_id=user_id,
            name=name,
            month_duration=month_duration,
            gross_income=gross_income,
        )
        db.session.add(budget)
        db.session.flush()
        return budget

    def create_item(self, budget, name, category, total="1000"):
        item = BudgetItem(
            budget_id=budget.id,
            name=name,
            category=category,
            total=total,
        )
        db.session.add(item)
        db.session.flush()
        return item


class BudgetDataFixture(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.raw_budget = self.create_budget(name="mock_name")
        self.item1 = self.create_item(
            self.raw_budget, name="Rent", category="bills", total="1200"
        )
        self.item2 = self.create_item(
            self.raw_budget, name="Groceries", category="bills", total="400"
        )
        db.session.commit()


# @unittest.skip
class GetBudget(BudgetDataFixture):  # TODO fix name
    def setUp(self):
        super().setUp()

    def test_success(self):
        response = get_budget(budget_id=self.raw_budget.id, user_id=10)
        budget = {
            "id": self.raw_budget.id,
            "name": "mock_name",
            "month_duration": 1,
            "gross_income": "$3,500.00",
            "items": [
                {
                    "id": self.item1.id,
                    "name": "Rent",
                    "category": "bills",
                    "total": "$1,200.00",
                },
                {
                    "id": self.item2.id,
                    "name": "Groceries",
                    "category": "bills",
                    "total": "$400.00",
                },
            ],
        }
        self.assertEqual(response, budget)

    def test_invalid_args(self):
        response = get_budget(2, 2)
        self.assertEqual(response, {})

    def test_invalid_budget_id(self):
        response = get_budget(2, 10)
        self.assertEqual(response, {})

    def test_invalid_user_id(self):
        response = get_budget(self.raw_budget.id, 2)
        self.assertEqual(response, {})


# @unittest.skip
class GetUserBudgets(BudgetDataFixture):

    def setUp(self):
        super().setUp()

        # Create sample data
        self.raw_budget2 = self.create_budget(
            name="mock_name2", month_duration="12", gross_income="123456"
        )
        self.budget2_item1 = self.create_item(
            budget=self.raw_budget2,
            name="401k",
            category="deductions",
            total="250",
        )

        self.raw_budget3 = self.create_budget(
            user_id=3,
            name="mock_name3",
            month_duration="12",
            gross_income="246810",
        )

        db.session.commit()

    def test_many_budgets_success(self):
        # user with id 10 has many budgets
        response = get_user_budgets(10)
        formatted_budgets = [
            {
                "id": self.raw_budget.id,
                "name": "mock_name",
                "month_duration": 1,
                "gross_income": "$3,500.00",
                "items": [
                    {
                        "id": self.item1.id,
                        "name": "Rent",
                        "category": "bills",
                        "total": "$1,200.00",
                    },
                    {
                        "id": self.item2.id,
                        "name": "Groceries",
                        "category": "bills",
                        "total": "$400.00",
                    },
                ],
            },
            {
                "id": self.raw_budget2.id,
                "name": "mock_name2",
                "month_duration": 12,
                "gross_income": "$123,456.00",
                "items": [
                    {
                        "id": 3,
                        "name": "401k",
                        "category": "deductions",
                        "total": "$250.00",
                    }
                ],
            },
        ]

        self.assertEqual(response, formatted_budgets)

    def test_single_budget_success(self):
        # user has a single budget
        response = get_user_budgets(self.raw_budget3.id)
        formatted_budget = [
            {
                "id": self.raw_budget3.id,
                "name": "mock_name3",
                "month_duration": 12,
                "gross_income": "$246,810.00",
                "items": [],
            }
        ]
        self.assertEqual(response, formatted_budget)

    def test_invalid_budget_id(self):
        # user with id 1 doesnt exist
        response = get_user_budgets(1)
        self.assertEqual(response, [])


# @unittest.skip
class CreateNewBudget(BudgetDataFixture):
    def setUp(self):
        super().setUp()

    def test_no_name_error(self):
        expected_error = "Budget name must not be empty."
        with self.assertRaisesRegex(ValueError, expected_error):
            create_new_budget(
                user_id=10, name=None, month_duration_raw="1", gross_income_raw="1234"
            )

    def test_name_already_exists_error(self):
        expected_error = "You already have a budget with that name."
        with self.assertRaisesRegex(ValueError, expected_error):
            create_new_budget(
                user_id=10,
                name="mock_name",
                month_duration_raw="1",
                gross_income_raw="123",
            )

    def test_invalid_month_duration(self):
        expected_error_invalid_int = "Month duration must be 1 (month) or 12 (year)."
        # use re.escape because of use of regex reserved chars in message
        with self.assertRaisesRegex(ValueError, re.escape(expected_error_invalid_int)):
            create_new_budget(
                user_id=10,
                name="test_invalid_month",
                month_duration_raw="3",
                gross_income_raw="123",
            )

        expected_error_invalid_value = (
            "Month duration must be a whole number (1 or 12)."
        )
        with self.assertRaisesRegex(
            ValueError, re.escape(expected_error_invalid_value)
        ):
            create_new_budget(
                user_id=10,
                name="test_invalid_month",
                month_duration_raw="1.5",
                gross_income_raw="123",
            )

    def test_invalid_gross_income(self):
        expected_error_negative_num = "Gross income must be a non negative number."
        with self.assertRaisesRegex(ValueError, expected_error_negative_num):
            create_new_budget(
                user_id=10,
                name="test_invalid_gross",
                month_duration_raw="1",
                gross_income_raw="-23",
            )

        expected_error_not_num = "Gross income must be a valid number."
        with self.assertRaisesRegex(ValueError, expected_error_not_num):
            create_new_budget(
                user_id=10,
                name="test_invalid_gross",
                month_duration_raw="1",
                gross_income_raw="one hundred",
            )

    def test_success(self):
        response = create_new_budget(
            user_id=10,
            name="test_success",
            month_duration_raw="1",
            gross_income_raw="1234",
        )
        self.assertIsInstance(response, int)
        formatted_budget = get_budget(response, 10)
        self.assertEqual("test_success", formatted_budget.get("name"))


# @unittest.skip
class CreateNewBudgetItem(BudgetDataFixture):
    def setUp(self):
        super().setUp()

    def test_invalid_budget(self):
        error_message = "Invalid budget."
        with self.assertRaisesRegex(ValueError, error_message):
            create_new_budget_item(
                name="test", category="savings", total="1234", budget_id=4, user_id=10
            )

    def test_missing_name(self):
        error_message = "Budget item name must not be empty."
        with self.assertRaisesRegex(ValueError, error_message):
            create_new_budget_item(
                name="", category="savings", total="1234", budget_id=1, user_id=10
            )

    def test_invalid_category(self):
        error_message = "Category: 'test' is not valid"
        with self.assertRaisesRegex(ValueError, error_message):
            create_new_budget_item(
                name="test", category="test", total="1234", budget_id=1, user_id=10
            )

    def test_invalid_total(self):
        error_message_negative_num = "Total must be a non negative number."
        with self.assertRaisesRegex(ValueError, error_message_negative_num):
            create_new_budget_item(
                name="test", category="savings", total="-1234", budget_id=1, user_id=10
            )

        error_message_not_num = "Total must be a valid number."
        with self.assertRaisesRegex(ValueError, error_message_not_num):
            create_new_budget_item(
                name="test",
                category="savings",
                total="1 hundred",
                budget_id=1,
                user_id=10,
            )

    def test_success(self):
        response = create_new_budget_item(
            name="test_success",
            category="savings",
            total="1234",
            budget_id=1,
            user_id=10,
        )
        self.assertEqual(response, 3)  # 3rd item added to budget:1, for user:10
        budget_items = get_budget(1, 10).get("items")
        expected_item = {
            "id": 3,
            "name": "test_success",
            "category": "savings",
            "total": "$1,234.00",
        }
        self.assertIn(expected_item, budget_items)


# @unittest.skip
class AttributesToUpdateDict(unittest.TestCase):
    def setUp(self):
        self.attributes = ["name", "total", "category"]

    def test_success(self):
        body = {"name": "test", "total": "1234", "category": "savings", "key": "value"}
        expected_response = body = {
            "name": "test",
            "total": "1234",
            "category": "savings",
        }
        response = attributes_to_update_dict(body, self.attributes)
        self.assertEqual(response, expected_response)

    def test_no_attributes_to_update(self):
        body = {"key": "value"}
        response = attributes_to_update_dict(body, self.attributes)
        self.assertEqual(response, {})


# @unittest.skip
class EditBudget(BudgetDataFixture):
    def setUp(self):
        super().setUp()

    def test_invalid_budget(self):
        with self.assertRaisesRegex(ValueError, "Invalid budget."):  # invalid budget_id
            edit_budget(2, 10, {"name": "test_invalid_budget"})

        with self.assertRaisesRegex(ValueError, "Invalid budget."):  # invalid_user
            edit_budget(1, 1, {"name": "test_invalid_budget"})

    def test_missing_name_value(self):
        with self.assertRaisesRegex(ValueError, "New name must not be empty."):
            edit_budget(1, 10, {"name": ""})

    def test_name_value_already_exists(self):
        self.create_budget(name="test_dont_dupe")
        with self.assertRaisesRegex(
            ValueError, "You already have a budget with that name."
        ):
            edit_budget(1, 10, {"name": "test_dont_dupe"})

    def test_invalid_gross_income_value(self):
        error_message_negative_num = "gross_income must be a non negative number."
        with self.assertRaisesRegex(ValueError, error_message_negative_num):
            edit_budget(1, 10, {"gross_income": "-123"})

        expected_error_not_num = "gross_income must be a valid number."
        with self.assertRaisesRegex(ValueError, expected_error_not_num):
            edit_budget(1, 10, {"gross_income": ""})

    def test_invalid_month_duration_value(self):
        expected_error_invalid_int = "Month duration must be 1 (month) or 12 (year)."
        with self.assertRaisesRegex(ValueError, re.escape(expected_error_invalid_int)):
            edit_budget(1, 10, {"month_duration": "2"})

        expected_error_invalid_value = (
            "Month duration must be a whole number (1 or 12)."
        )
        with self.assertRaisesRegex(
            ValueError, re.escape(expected_error_invalid_value)
        ):
            edit_budget(1, 10, {"month_duration": ""})

    def test_success_all_attributes(self):
        response = edit_budget(
            1,
            10,
            {"name": "test_success", "month_duration": "12", "gross_income": "22222"},
        )
        self.assertEqual(response, 1)

        budget = get_budget(1, 10)

        self.assertEqual(budget.get("name"), "test_success")
        self.assertEqual(budget.get("month_duration"), 12)
        self.assertEqual(budget.get("gross_income"), "$22,222.00")

    def test_success_one_attribute(self):
        response = edit_budget(
            1,
            10,
            {"name": "test_success"},
        )
        self.assertEqual(response, 1)

        budget = get_budget(1, 10)

        self.assertEqual(budget.get("name"), "test_success")  # changed
        # attributes stayed the same
        self.assertEqual(budget.get("month_duration"), 1)
        self.assertEqual(budget.get("gross_income"), "$3,500.00")


# @unittest.skip
class EditBudgetItem(BudgetDataFixture):
    def setUp(self):
        super().setUp()

    def test_invalid_budget_item(self):
        with self.assertRaisesRegex(ValueError, "Invalid budget item."):
            edit_budget_item(12, 1, {"name": "foo"})  # invalid item_id

        with self.assertRaisesRegex(ValueError, "Invalid budget item."):
            edit_budget_item(1, 12, {"name": "foo"})  # invalid budget_id

    def test_missing_name_value(self):
        with self.assertRaisesRegex(ValueError, "New name must not be empty."):
            edit_budget_item(1, 1, {"name": ""})

    def test_invalid_category(self):
        with self.assertRaisesRegex(
            ValueError, "Category: 'invalid_category' is not valid"
        ):
            edit_budget_item(1, 1, {"category": "invalid_category"})

    def test_invalid_total_value(self):
        error_message_negative_num = "Total must be a non negative number."
        with self.assertRaisesRegex(ValueError, error_message_negative_num):
            edit_budget_item(1, 1, {"total": "-123"})

        expected_error_not_num = "Total must be a valid number."
        with self.assertRaisesRegex(ValueError, expected_error_not_num):
            edit_budget_item(1, 1, {"total": ""})

    def test_success_all_attributes(self):
        # original budget_item
        budget_items = get_budget(1, 10).get("items")
        original_item = {
            "id": 1,
            "name": "Rent",
            "category": "bills",
            "total": "$1,200.00",
        }
        self.assertIn(original_item, budget_items)

        # edit budget_item
        edit_budget_item(
            1, 1, {"name": "test_success", "category": "savings", "total": "123"}
        )
        budget_items = get_budget(1, 10).get("items")
        expected_item = {
            "id": 1,
            "name": "test_success",
            "category": "savings",
            "total": "$123.00",
        }
        self.assertIn(expected_item, budget_items)

    def test_success_one_attribute(self):
        # original budget_item
        budget_items = get_budget(1, 10).get("items")
        original_item = {
            "id": 1,
            "name": "Rent",
            "category": "bills",
            "total": "$1,200.00",
        }

        self.assertIn(original_item, budget_items)

        # edit budget_item
        edit_budget_item(1, 1, {"name": "test_success"})
        budget_items = get_budget(1, 10).get("items")
        expected_item = {
            "id": 1,
            "name": "test_success",  # changed attribute
            "category": "bills",  # unchanged
            "total": "$1,200.00",  # unchanged
        }
        self.assertIn(expected_item, budget_items)


# @unittest.skip
class DeleteBudget(BudgetDataFixture):
    def setUp(self):
        super().setUp()

    def test_invalid_budget(self):
        with self.assertRaisesRegex(ValueError, "Invalid budget."):
            delete_budget(12, 10)  # invalid budget_id

        with self.assertRaisesRegex(ValueError, "Invalid budget."):
            delete_budget(1, 12)  # invalid user_id

    def test_success(self):
        response = delete_budget(1, 10)
        self.assertEqual(response, "mock_name")

        budget = Budget.query.filter_by(id=1, user_id=10).first()
        self.assertIsNone(budget)


class DeleteBudgetItem(BudgetDataFixture):
    def setUp(self):
        super().setUp()

    def test_invalid_budget_item(self):
        with self.assertRaisesRegex(ValueError, "Invalid budget item."):
            delete_budget_item(12, 1)  # invalid item_id

        with self.assertRaisesRegex(ValueError, "Invalid budget item."):
            delete_budget_item(1, 3)  # invalid budget_id

    def test_success(self):
        # check budget_item exists
        budget_item = BudgetItem.query.filter_by(id=1, budget_id=1).first()
        self.assertIsNotNone(budget_item)

        response = delete_budget_item(1, 1)
        item_description = "Category: 'bills' and with Name:'Rent'"
        self.assertEqual(response, item_description)

        # check budget_item no longer exists
        budget_item = BudgetItem.query.filter_by(id=1, budget_id=1).first()
        self.assertIsNone(budget_item)


if __name__ == "__main__":
    unittest.main()
