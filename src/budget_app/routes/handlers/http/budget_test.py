"""TODO start tests for budget.py,

test all funcs in budgetHandler class"""

import unittest
from unittest.mock import patch

# TODO do we need session ..?
from budget_app import create_app
from budget_app.routes.handlers.http.budget import BudgetHandler


# TODO work with chat about structure and next steps


class BaseAuthHandlerTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.handler = BudgetHandler()


class TestGetBudget(BaseAuthHandlerTest):
    pass


class TestGetBudgets(BaseAuthHandlerTest):
    pass


class TestCreateBudget(BaseAuthHandlerTest):
    pass


class TestCreateBudgetItem(BaseAuthHandlerTest):
    pass


class TestEditBudget(BaseAuthHandlerTest):
    pass


class TestEditBudgetItem(BaseAuthHandlerTest):
    pass


class TestDeleteBudget(BaseAuthHandlerTest):
    pass


class TestDeleteBudgetItem(BaseAuthHandlerTest):
    pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
