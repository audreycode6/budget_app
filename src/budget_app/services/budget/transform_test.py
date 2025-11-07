import unittest
from .transform import raw_budget_to_budget
from ...models import Budget, BudgetItem


class RawBudgetToBudget(unittest.TestCase):

    def setUp(self):
        self.raw_budget = Budget(
            id=1, user_id=10, name="mock_name", month_duration=1, gross_income=3500
        )

        self.raw_budget.items = [
            BudgetItem(id=1, budget_id=1, name="Rent", category="bills", total=1200),
            BudgetItem(id=2, budget_id=1, name="Groceries", category="food", total=400),
        ]

    def test_success(self):
        response = raw_budget_to_budget(self.raw_budget)
        formatted_budget = {
            "id": 1,
            "name": "mock_name",
            "month_duration": 1,
            "gross_income": "$3,500.00",
            "items": [
                {
                    "id": 1,
                    "name": "Rent",
                    "category": "bills",
                    "total": "$1,200.00",
                },
                {
                    "id": 2,
                    "name": "Groceries",
                    "category": "food",
                    "total": "$400.00",
                },
            ],
        }
        self.assertEqual(response, formatted_budget)


if __name__ == "__main__":
    unittest.main()
