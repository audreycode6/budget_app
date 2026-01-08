import unittest
from unittest.mock import patch

from budget_app import create_app
from budget_app.routes.handlers.http.budget import BudgetHandler

BUDGET_HANDLER_PATH = "budget_app.routes.handlers.http.budget"


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
    VALID_BUDGET_ITEM_BODY = {
        "budget_id": 1,
        "name": "test_item",
        "category": "bills",
        "total": 200,
    }
    VALID_GET_BUDGET_BODY = {"budget_id": 1}
    VALID_GET_BUDGETS_BODY = [{"id": 1, "name": "test"}, {}]
    VALID_CREATE_BUDGET_BODY = {
        "name": "Test Budget",
        "month_duration": 1,
        "gross_income": 1000,
    }

    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.handler = BudgetHandler()


class TestGetBudget(BaseBudgetHandlerTest):

    @patch(f"{BUDGET_HANDLER_PATH}.get_budget_by_budget_and_user_id")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_success(self, mock_get_session, mock_get_budget_by_budget_and_user_id):
        mock_get_session.return_value = (
            BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        )  # TODO do i need to mock for use of session value?
        mock_get_budget_by_budget_and_user_id.return_value = (
            BaseBudgetHandlerTest.VALID_BUDGET_OBJECT
        )

        with self.app.test_request_context():
            response, status = self.handler.get_budget(
                BaseBudgetHandlerTest.VALID_GET_BUDGET_BODY
            )
            self.assertEqual(status, 200)
            self.assertEqual(
                BaseBudgetHandlerTest.VALID_BUDGET_OBJECT, response["budget"]
            )

    @patch(f"{BUDGET_HANDLER_PATH}.get_budget_by_budget_and_user_id")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_exception_raised(
        self,
        mock_get_session,
        mock_get_budget_by_budget_and_user_id,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_get_budget_by_budget_and_user_id.side_effect = Exception(
            "service unavailable"
        )

        with self.app.test_request_context():
            response, status = self.handler.get_budget(
                BaseBudgetHandlerTest.VALID_GET_BUDGET_BODY
            )
            self.assertEqual(status, 503)
            self.assertIn("Unable to retreive budget.", response["message"])

    def test_missing_body_keys(self):
        with self.app.test_request_context():
            response, status = self.handler.get_budget("bad input")
            self.assertEqual(status, 422)
            self.assertIn("No budget_id provided", response["message"])


class TestGetBudgets(BaseBudgetHandlerTest):

    @patch(f"{BUDGET_HANDLER_PATH}.get_budgets_by_user_id")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
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

    @patch(f"{BUDGET_HANDLER_PATH}.get_budgets_by_user_id")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_exception_raised(self, mock_get_session, mock_get_budgets_by_user_id):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_get_budgets_by_user_id.side_effect = Exception("service unavailable")

        with self.app.test_request_context():
            response, status = self.handler.get_budgets()
            self.assertEqual(status, 503)
            self.assertIn("Unable to retreive budget(s).", response["message"])


class TestCreateBudget(BaseBudgetHandlerTest):

    @patch(
        f"{BUDGET_HANDLER_PATH}.get_budget_by_budget_and_user_id"
    )  # TODO are these valid to patch/ mock?
    @patch(f"{BUDGET_HANDLER_PATH}.create_new_budget")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_success(
        self,
        mock_get_session,
        mock_create_new_budget,
        mock_get_budget_by_budget_and_user_id,
    ):
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

    def test_missing_body_keys(self):
        with self.app.test_request_context():
            response, status = self.handler.create_budget({})
            self.assertEqual(status, 422)
            self.assertIn(
                "Missing attribute(s) to update. Valid attributes are: ",
                response["message"],
            )

    @patch(f"{BUDGET_HANDLER_PATH}.create_new_budget")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_value_error_exception(
        self,
        mock_get_session,
        mock_create_new_budget,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_create_new_budget.side_effect = ValueError("bad request")

        with self.app.test_request_context():
            response, status = self.handler.create_budget(
                BaseBudgetHandlerTest.VALID_CREATE_BUDGET_BODY
            )
            self.assertEqual(status, 422)
            self.assertIn("bad request", response["message"])

    @patch(f"{BUDGET_HANDLER_PATH}.create_new_budget")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_exception_raised(
        self,
        mock_get_session,
        mock_create_new_budget,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_create_new_budget.side_effect = Exception("service unavailable")

        with self.app.test_request_context():
            response, status = self.handler.create_budget(
                BaseBudgetHandlerTest.VALID_CREATE_BUDGET_BODY
            )
            self.assertEqual(503, status)
            self.assertIn("Unable to fetch budget.", response["message"])


class TestCreateBudgetItem(BaseBudgetHandlerTest):
    @patch(f"{BUDGET_HANDLER_PATH}.get_budget_by_budget_and_user_id")
    @patch(f"{BUDGET_HANDLER_PATH}.create_new_budget_item")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_success(
        self,
        mock_get_session,
        mock_create_new_budget_item,
        mock_get_budget_by_budget_and_user_id,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_create_new_budget_item.return_value = 1  # new_budget_item.id -> int shape
        mock_get_budget_by_budget_and_user_id.return_value = (
            BaseBudgetHandlerTest.VALID_BUDGET_OBJECT_WITH_ITEMS
        )

        with self.app.test_request_context():
            response, status = self.handler.create_budget_item(
                BaseBudgetHandlerTest.VALID_BUDGET_ITEM_BODY
            )
            print(f"TEST {response}")
            self.assertEqual(200, status)
            self.assertEqual(
                BaseBudgetHandlerTest.VALID_BUDGET_OBJECT_WITH_ITEMS,
                response["budget"],
            )  # response["budget"] == mocked object
            self.assertEqual(1, response["budget_item_id"])

    @patch(f"{BUDGET_HANDLER_PATH}.create_new_budget_item")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_value_error_exception(
        self,
        mock_get_session,
        mock_create_new_budget_item,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_create_new_budget_item.side_effect = ValueError("Bad request")

        with self.app.test_request_context():
            response, status = self.handler.create_budget_item(
                BaseBudgetHandlerTest.VALID_BUDGET_ITEM_BODY
            )
            self.assertEqual(422, status)
            self.assertIn("Bad request", response["message"])

    @patch(f"{BUDGET_HANDLER_PATH}.create_new_budget_item")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_exception_raised(
        self,
        mock_get_session,
        mock_create_new_budget_item,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_create_new_budget_item.side_effect = Exception("Service unavailable")

        with self.app.test_request_context():
            response, status = self.handler.create_budget_item(
                BaseBudgetHandlerTest.VALID_BUDGET_ITEM_BODY
            )
            self.assertEqual(503, status)
            self.assertIn("Unable to fetch budget item", response["message"])

    def test_missing_body_keys(self):
        with self.app.test_request_context():
            response, status = self.handler.create_budget_item("bad input")
            self.assertEqual(status, 422)
            self.assertIn(
                "Missing attribute(s) to update. Valid attributes are:",
                response["message"],
            )


class TestEditBudget(BaseBudgetHandlerTest):
    VALID_EDIT_BUDGET_BODY = {
        "budget_id": 1,
        "name": "new name",
        "month_duration": 12,
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

    @patch(f"{BUDGET_HANDLER_PATH}.get_budget_by_budget_and_user_id")
    @patch(f"{BUDGET_HANDLER_PATH}.edit_budget_attributes")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_success(
        self,
        mock_get_session,
        mock_edit_budget_attributes,
        mock_get_budget_by_budget_and_user_id,
    ):
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

    def test_missing_attributes_to_update(self):
        with self.app.test_request_context():
            response, status = self.handler.edit_budget({"budget_id": 1})
            self.assertEqual(422, status)
            self.assertIn(
                "Missing attribute(s) to update. Valid attributes are:",
                response["message"],
            )

    def test_missing_body_keys(self):
        with self.app.test_request_context():
            response, status = self.handler.edit_budget("bad input")
            self.assertEqual(422, status)
            self.assertEqual("Missing budget_id", response["message"])

    @patch(f"{BUDGET_HANDLER_PATH}.edit_budget_attributes")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    @patch(f"{BUDGET_HANDLER_PATH}.attributes_to_update_dict")
    def test_value_error_raised(
        self,
        mock_attributes_to_update_dict,
        mock_get_session,
        mock_edit_budget_attributes,
    ):
        mock_attributes_to_update_dict.return_value = (
            TestEditBudget.ATTRIBUTES_TO_UPDATE_BODY
        )
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_edit_budget_attributes.side_effect = ValueError("Bad request")

        with self.app.test_request_context():
            response, status = self.handler.edit_budget(
                {
                    "budget_id": 1,
                    "name": None,
                    "month_duration": 12,
                }
            )
            self.assertEqual(422, status)
            self.assertEqual("Bad request", response["message"])

    @patch(f"{BUDGET_HANDLER_PATH}.edit_budget_attributes")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    @patch(f"{BUDGET_HANDLER_PATH}.attributes_to_update_dict")
    def test_exception_raised(
        self,
        mock_attributes_to_update_dict,
        mock_get_session,
        mock_edit_budget_attributes,
    ):
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

    ATTRIBUTES_TO_UPDATE_BODY = {"name": "new name", "category": "bills", "total": 1234}
    EDITED_BUDGET_ITEM_OBJ = {
        "id": 1,
        "name": "my_budget",
        "month_duration": 12,
        "gross_income": 1000,
        "items": [
            {"id": 1, "name": "new name", "category": "bills", "total": "$1,234.00"}
        ],
    }
    EDIT_BUDGET_ITEM_BODY = {
        "item_id": 1,
        "budget_id": 1,
        "name": "new name",
        "category": "bills",
        "total": 1234,
    }

    def test_missing_body_keys(self):
        with self.app.test_request_context():
            response, status = self.handler.edit_budget_item("bad input")
            self.assertEqual(422, status)
            self.assertEqual("Missing budget_id and/or item_id", response["message"])

    def test_missing_attributes_to_update(self):
        with self.app.test_request_context():
            response, status = self.handler.edit_budget_item(
                {
                    "item_id": 1,
                    "budget_id": 1,
                }
            )
            self.assertEqual(422, status)
            self.assertIn(
                "Missing attribute(s) to update. Valid attributes are:",
                response["message"],
            )

    @patch(f"{BUDGET_HANDLER_PATH}.get_budget_by_budget_and_user_id")
    @patch(f"{BUDGET_HANDLER_PATH}.edit_budget_item_attributes")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_success(
        self,
        mock_get_session,
        mock_edit_budget_item_attributes,
        mock_get_budget_by_budget_and_user_id,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_edit_budget_item_attributes.return_value = 1  # item_id -> int shape
        mock_get_budget_by_budget_and_user_id.return_value = (
            TestEditBudgetItem.EDITED_BUDGET_ITEM_OBJ
        )
        with self.app.test_request_context():
            response, status = self.handler.edit_budget_item(
                TestEditBudgetItem.EDIT_BUDGET_ITEM_BODY
            )
            self.assertEqual(200, status)
            self.assertEqual(1, response["budget_item_id"])
            self.assertEqual(
                TestEditBudgetItem.EDITED_BUDGET_ITEM_OBJ, response["budget"]
            )

    @patch(f"{BUDGET_HANDLER_PATH}.edit_budget_item_attributes")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_value_error_raised(
        self,
        mock_get_session,
        mock_edit_budget_item_attributes,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_edit_budget_item_attributes.side_effect = ValueError("Bad request")
        with self.app.test_request_context():
            response, status = self.handler.edit_budget_item(
                {
                    "item_id": 1,
                    "budget_id": 1,
                    "name": None,
                    "category": "bills",
                    "total": 1234,
                }
            )
            self.assertEqual(422, status)
            self.assertEqual("Bad request", response["message"])

    @patch(f"{BUDGET_HANDLER_PATH}.edit_budget_item_attributes")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_exception_raised(
        self,
        mock_get_session,
        mock_edit_budget_item_attributes,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_edit_budget_item_attributes.side_effect = Exception("Service unavailable")

        with self.app.test_request_context():
            response, status = self.handler.edit_budget_item(
                TestEditBudgetItem.EDIT_BUDGET_ITEM_BODY
            )
            self.assertEqual(503, status)
            self.assertIn("Unable to update budget item", response["message"])


class TestDeleteBudget(BaseBudgetHandlerTest):
    def test_missing_request_body_keys(self):
        with self.app.test_request_context():
            response, status = self.handler.delete_budget("bad input")
            self.assertEqual(422, status)
            self.assertEqual("Missing budget_id", response["message"])

    @patch(f"{BUDGET_HANDLER_PATH}.delete_budget_by_budget_and_user_ids")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_success(
        self,
        mock_get_session,
        mock_delete_budget_by_budget_and_user_ids,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_delete_budget_by_budget_and_user_ids.return_value = "my budget name"

        with self.app.test_request_context():
            response, status = self.handler.delete_budget({"budget_id": 1})
            self.assertEqual(200, status)
            self.assertIn(
                "Budget 'my budget name' and its contents has been deleted",
                response["message"],
            )

    @patch(f"{BUDGET_HANDLER_PATH}.delete_budget_by_budget_and_user_ids")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_value_error_raised(
        self,
        mock_get_session,
        mock_delete_budget_by_budget_and_user_ids,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_delete_budget_by_budget_and_user_ids.side_effect = ValueError(
            "Bad request"
        )

        with self.app.test_request_context():
            response, status = self.handler.delete_budget({"budget_id": None})
            self.assertEqual(422, status)
            self.assertIn(
                "Bad request",
                response["message"],
            )

    @patch(f"{BUDGET_HANDLER_PATH}.delete_budget_by_budget_and_user_ids")
    @patch(f"{BUDGET_HANDLER_PATH}.get_session")
    def test_exception_raised(
        self,
        mock_get_session,
        mock_delete_budget_by_budget_and_user_ids,
    ):
        mock_get_session.return_value = BaseBudgetHandlerTest.SESSION_USER_ID_SHAPE
        mock_delete_budget_by_budget_and_user_ids.side_effect = Exception(
            "Service unavailable"
        )

        with self.app.test_request_context():
            response, status = self.handler.delete_budget({"budget_id": 1})
            self.assertEqual(503, status)
            self.assertIn(
                "Unable to delete budget",
                response["message"],
            )


class TestDeleteBudgetItem(BaseBudgetHandlerTest):

    def test_missing_request_body_keys(self):
        with self.app.test_request_context():
            response, status = self.handler.delete_budget_item("bad input")
            self.assertEqual(422, status)
            self.assertEqual("Missing item_id and/or budget_id", response["message"])

    @patch(f"{BUDGET_HANDLER_PATH}.delete_budget_item_by_item_and_budget_ids")
    def test_success(
        self,
        mock_delete_budget_item_by_item_and_budget_ids,
    ):
        mock_delete_budget_item_by_item_and_budget_ids.return_value = (
            "Category: 'bills' and with Name: 'internet'"
        )

        with self.app.test_request_context():
            response, status = self.handler.delete_budget_item(
                {"item_id": 1, "budget_id": 1}
            )
            self.assertEqual(200, status)
            self.assertEqual(
                "Budget item in Category: 'bills' and with Name: 'internet' and its contents has been deleted.",
                response["message"],
            )

    @patch(f"{BUDGET_HANDLER_PATH}.delete_budget_item_by_item_and_budget_ids")
    def test_value_error_raised(
        self,
        mock_delete_budget_item_by_item_and_budget_ids,
    ):
        mock_delete_budget_item_by_item_and_budget_ids.side_effect = ValueError(
            "Bad request"
        )

        with self.app.test_request_context():
            response, status = self.handler.delete_budget_item(
                {"item_id": 1, "budget_id": None}
            )
            self.assertEqual(422, status)
            self.assertEqual("Bad request", response["message"])

    @patch(f"{BUDGET_HANDLER_PATH}.delete_budget_item_by_item_and_budget_ids")
    def test_exception_raised(
        self,
        mock_delete_budget_item_by_item_and_budget_ids,
    ):
        mock_delete_budget_item_by_item_and_budget_ids.side_effect = Exception(
            "Service unavailable"
        )

        with self.app.test_request_context():
            response, status = self.handler.delete_budget_item(
                {"item_id": 1, "budget_id": 1}
            )
            self.assertEqual(503, status)
            self.assertIn("Unable to delete budget", response["message"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
