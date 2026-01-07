"""TODO start tests for budget.py,

test all funcs in budgetHandler class"""

"""
@patch("budget_app.routes.handlers.http.budget..")

# 1. What does validate_request_body_keys_exist need to return?
# 2. Does get_session get called?
# 3. Does the service get called?
# 4. What is the earliest return path?
"""

import unittest
from unittest.mock import patch

from budget_app import create_app
from budget_app.routes.handlers.http.budget import BudgetHandler


class BaseBudgetHandlerTest(unittest.TestCase):
    SESSION_USER_ID_SHAPE = {
        "id": 1
    }  # session['user_id'] -> needs to be indexable by "id"
    VALID_BUDGET_OBJECT = {
        "id": 1,
        "name": "Test Budget",
        "month_duration": 1,
        "gross_income": 1000,
    }
    VALID_BUDGET_OBJECT_WITH_ITEMS = {
        "id": 1,
        "name": "Test Budget",
        "month_duration": 1,
        "gross_income": 1000,
        "items": [
            {"id": 1, "name": "test_item", "category": "bills", "total": "$200.00"}
        ],
    }
    VALID_BUDGET_ITEM_BODY = {"name": "test_item", "category": "bills", "total": 200}
    VALID_GET_BUDGETS_BODY = [{"id": 1, "name": "test"}, {}]
    VALID_CREATE_BUDGET_BODY = {
        "name": "Test Budget",
        "month_duration": 1,
        "gross_income": 1000,
    }

    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.handler = BudgetHandler()


@unittest.skip
class TestGetBudget(BaseBudgetHandlerTest):

    @patch("budget_app.routes.handlers.http.budget.get_budget_by_budget_and_user_id")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_success(
        self,
        mock_validate_request_body_keys_exist,
        mock_get_session,
        mock_get_budget_by_budget_and_user_id,
    ):
        mock_validate_request_body_keys_exist.return_value = (
            True  # check ['budget_id'] is in body
        )
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_get_budget_by_budget_and_user_id.return_value = (
            BaseBudgetHandlerTest.VALID_BUDGET_OBJECT
        )

        with self.app.test_request_context():
            response, status = self.handler.get_budget(
                BaseBudgetHandlerTest.VALID_CREATE_BUDGET_BODY
            )
            self.assertEqual(status, 200)
            self.assertEqual(
                BaseBudgetHandlerTest.VALID_BUDGET_OBJECT, response["budget"]
            )

    @patch("budget_app.routes.handlers.http.budget.get_budget_by_budget_and_user_id")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_exception_raised(
        self,
        mock_validate_request_body_keys_exist,
        mock_get_session,
        mock_get_budget_by_budget_and_user_id,
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_get_budget_by_budget_and_user_id.side_effect = Exception(
            "service unavailable"
        )

        with self.app.test_request_context():
            response, status = self.handler.get_budget({"budget_id": 1})
            self.assertEqual(status, 503)
            self.assertIn("Unable to retreive budget.", response["message"])

    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_missing_body_keys(self, mock_validate_request_body_keys_exist):
        mock_validate_request_body_keys_exist.return_value = False

        with self.app.test_request_context():
            response, status = self.handler.get_budget({})
            self.assertEqual(status, 422)
            self.assertIn("No budget_id provided", response["message"])


@unittest.skip
class TestGetBudgets(BaseBudgetHandlerTest):

    @patch("budget_app.routes.handlers.http.budget.get_budgets_by_user_id")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    def test_success(self, mock_get_session, mock_get_budgets_by_user_id):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_get_budgets_by_user_id.return_value = (
            BaseBudgetHandlerTest.VALID_GET_BUDGETS_BODY
        )

        with self.app.test_request_context():
            response, status = self.handler.get_budgets()
            self.assertEqual(status, 200)
            self.assertEqual(
                BaseBudgetHandlerTest.VALID_GET_BUDGETS_BODY, response["budgets"]
            )

    @patch("budget_app.routes.handlers.http.budget.get_budgets_by_user_id")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    def test_exception_raised(self, mock_get_session, mock_get_budgets_by_user_id):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_get_budgets_by_user_id.side_effect = Exception("service unavailable")

        with self.app.test_request_context():
            response, status = self.handler.get_budgets()
            self.assertEqual(status, 503)
            self.assertIn("Unable to retreive budget(s).", response["message"])


@unittest.skip
class TestCreateBudget(BaseBudgetHandlerTest):

    @patch("budget_app.routes.handlers.http.budget.get_budget_by_budget_and_user_id")
    @patch("budget_app.routes.handlers.http.budget.create_new_budget")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_success(
        self,
        mock_validate_request_body_keys_exist,
        mock_get_session,
        mock_create_new_budget,
        mock_get_budget_by_budget_and_user_id,
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_create_new_budget.return_value = 1  # new_budget.id is int shape
        mock_get_budget_by_budget_and_user_id.return_value = (
            BaseBudgetHandlerTest.VALID_BUDGET_OBJECT
        )

        with self.app.test_request_context():
            response, status = self.handler.create_budget(
                BaseBudgetHandlerTest.VALID_CREATE_BUDGET_BODY
            )
            self.assertEqual(200, status)
            self.assertEqual(
                BaseBudgetHandlerTest.VALID_BUDGET_OBJECT,
                response["budget"],
            )  # response["budget"] == mocked object

    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_missing_body_keys(
        self,
        mock_validate_request_body_keys_exist,
    ):
        mock_validate_request_body_keys_exist.return_value = False

        with self.app.test_request_context():
            response, status = self.handler.create_budget({})
            self.assertEqual(status, 422)
            self.assertIn(
                "Missing attribute(s) to update. Valid attributes are: ",
                response["message"],
            )

    @patch("budget_app.routes.handlers.http.budget.create_new_budget")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_value_error_exception(
        self,
        mock_validate_request_body_keys_exist,
        mock_get_session,
        mock_create_new_budget,
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_create_new_budget.side_effect = ValueError("bad request")

        with self.app.test_request_context():
            response, status = self.handler.create_budget(
                BaseBudgetHandlerTest.VALID_CREATE_BUDGET_BODY
            )
            self.assertEqual(status, 422)
            self.assertIn("bad request", response["message"])

    @patch("budget_app.routes.handlers.http.budget.create_new_budget")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_exception_raised(
        self,
        mock_validate_request_body_keys_exist,
        mock_get_session,
        mock_create_new_budget,
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_create_new_budget.side_effect = Exception("service unavailable")

        with self.app.test_request_context():
            response, status = self.handler.create_budget(
                BaseBudgetHandlerTest.VALID_CREATE_BUDGET_BODY
            )
            self.assertEqual(503, status)
            self.assertIn("Unable to fetch budget.", response["message"])


@unittest.skip
class TestCreateBudgetItem(BaseBudgetHandlerTest):
    @patch("budget_app.routes.handlers.http.budget.get_budget_by_budget_and_user_id")
    @patch("budget_app.routes.handlers.http.budget.create_new_budget_item")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_success(
        self,
        mock_validate_request_body_keys_exist,
        mock_get_session,
        mock_create_new_budget_item,
        mock_get_budget_by_budget_and_user_id,
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_create_new_budget_item.return_value = 1  # new_budget_item.id -> int shape
        mock_get_budget_by_budget_and_user_id.return_value = (
            BaseBudgetHandlerTest.VALID_BUDGET_OBJECT_WITH_ITEMS
        )

        with self.app.test_request_context():
            response, status = self.handler.create_budget_item(
                BaseBudgetHandlerTest.VALID_BUDGET_ITEM_BODY
            )
            self.assertEqual(200, status)
            self.assertEqual(
                BaseBudgetHandlerTest.VALID_BUDGET_OBJECT_WITH_ITEMS,
                response["budget"],
            )  # response["budget"] == mocked object
            self.assertEqual(1, response["budget_item_id"])

    @patch("budget_app.routes.handlers.http.budget.create_new_budget_item")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_value_error_exception(
        self,
        mock_validate_request_body_keys_exist,
        mock_get_session,
        mock_create_new_budget_item,
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_create_new_budget_item.side_effect = ValueError("Bad request")

        with self.app.test_request_context():
            response, status = self.handler.create_budget_item(
                BaseBudgetHandlerTest.VALID_BUDGET_ITEM_BODY
            )
            self.assertEqual(422, status)
            self.assertIn("Bad request", response["message"])

    @patch("budget_app.routes.handlers.http.budget.create_new_budget_item")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_exception_raised(
        self,
        mock_validate_request_body_keys_exist,
        mock_get_session,
        mock_create_new_budget_item,
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_create_new_budget_item.side_effect = Exception("Service unavailable")

        with self.app.test_request_context():
            response, status = self.handler.create_budget_item(
                BaseBudgetHandlerTest.VALID_BUDGET_ITEM_BODY
            )
            self.assertEqual(503, status)
            self.assertIn("Unable to fetch budget item", response["message"])

    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_missing_body_keys(self, mock_validate_request_body_keys_exist):
        mock_validate_request_body_keys_exist.return_value = False

        with self.app.test_request_context():
            response, status = self.handler.create_budget_item({})
            self.assertEqual(status, 422)
            self.assertIn(
                "Missing attribute(s) to update. Valid attributes are:",
                response["message"],
            )


class TestEditBudget(BaseBudgetHandlerTest):
    VALID_EDIT_BUDGET_BODY = {
        "budget_id": 1,
        "attributes": {
            "name": "new name",
            "month_duration": 12,
        },
    }
    ATTRIBUTES_TO_UPDATE_BODY = {
        "name": "new name",
        "month_duration": 12,
    }
    EDITED_BUDGET_OBJ = {
        "id": 1,
        "name": "new name",
        "month_duration": 12,
        "gross_income": 1000,
    }

    @patch("budget_app.routes.handlers.http.budget.get_budget_by_budget_and_user_id")
    @patch("budget_app.routes.handlers.http.budget.edit_budget_attributes")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    @patch("budget_app.routes.handlers.http.budget.attributes_to_update_dict")
    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_success(
        self,
        mock_validate_request_body_keys_exist,
        mock_attributes_to_update_dict,
        mock_get_session,
        mock_edit_budget_attributes,
        mock_get_budget_by_budget_and_user_id,
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_attributes_to_update_dict.return_value = (
            TestEditBudget.ATTRIBUTES_TO_UPDATE_BODY
        )
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_edit_budget_attributes.return_value = 1  # budget.id -> int shape
        mock_get_budget_by_budget_and_user_id.return_value = (
            TestEditBudget.EDITED_BUDGET_OBJ
        )

        with self.app.test_request_context():
            response, status = self.handler.edit_budget(
                TestEditBudget.VALID_EDIT_BUDGET_BODY
            )
            self.assertEqual(200, status)
            self.assertEqual(1, response["budget_id"])
            self.assertEqual(TestEditBudget.EDITED_BUDGET_OBJ, response["budget"])

    @patch("budget_app.routes.handlers.http.budget.attributes_to_update_dict")
    def test_missing_attributes_to_update(
        self,
        mock_attributes_to_update_dict,
    ):
        mock_attributes_to_update_dict.return_value = {}

        with self.app.test_request_context():
            response, status = self.handler.edit_budget(
                {"budget_id": 1, "attributes": {}}
            )
            self.assertEqual(422, status)
            self.assertIn(
                "Missing attribute(s) to update. Valid attributes are:",
                response["message"],
            )

    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_missing_body_keys(self, mock_validate_request_body_keys_exist):
        mock_validate_request_body_keys_exist.return_value = False

        with self.app.test_request_context():
            response, status = self.handler.edit_budget(
                TestEditBudget.VALID_EDIT_BUDGET_BODY
            )
            self.assertEqual(422, status)
            self.assertEqual("Missing budget_id", response["message"])

    @patch("budget_app.routes.handlers.http.budget.get_budget_by_budget_and_user_id")
    @patch("budget_app.routes.handlers.http.budget.edit_budget_attributes")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    @patch("budget_app.routes.handlers.http.budget.attributes_to_update_dict")
    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_value_error_raised(
        self,
        mock_validate_request_body_keys_exist,
        mock_attributes_to_update_dict,
        mock_get_session,
        mock_edit_budget_attributes,
        mock_get_budget_by_budget_and_user_id,  # just prevent accidental execution
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_attributes_to_update_dict.return_value = (
            TestEditBudget.ATTRIBUTES_TO_UPDATE_BODY
        )
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_edit_budget_attributes.side_effect = ValueError("Bad request")

        with self.app.test_request_context():
            response, status = self.handler.edit_budget(
                TestEditBudget.VALID_EDIT_BUDGET_BODY
            )
            self.assertEqual(422, status)
            self.assertEqual("Bad request", response["message"])

    @patch("budget_app.routes.handlers.http.budget.get_budget_by_budget_and_user_id")
    @patch("budget_app.routes.handlers.http.budget.edit_budget_attributes")
    @patch("budget_app.routes.handlers.http.budget.get_session")
    @patch("budget_app.routes.handlers.http.budget.attributes_to_update_dict")
    @patch("budget_app.routes.handlers.http.budget.validate_request_body_keys_exist")
    def test_exception_raised(
        self,
        mock_validate_request_body_keys_exist,
        mock_attributes_to_update_dict,
        mock_get_session,
        mock_edit_budget_attributes,
        mock_get_budget_by_budget_and_user_id,  # just prevent accidental execution
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_attributes_to_update_dict.return_value = (
            TestEditBudget.ATTRIBUTES_TO_UPDATE_BODY
        )
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_edit_budget_attributes.side_effect = Exception("Service unavailable")

        with self.app.test_request_context():
            response, status = self.handler.edit_budget(
                TestEditBudget.VALID_EDIT_BUDGET_BODY
            )
            self.assertEqual(503, status)
            self.assertIn("Unable to update budget", response["message"])


class TestEditBudgetItem(BaseBudgetHandlerTest):
    pass


class TestDeleteBudget(BaseBudgetHandlerTest):
    pass


class TestDeleteBudgetItem(BaseBudgetHandlerTest):
    pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
