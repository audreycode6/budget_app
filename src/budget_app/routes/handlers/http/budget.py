from budget_app.services.auth.auth_service import get_session
from budget_app.services.budget.budget_service import (
    create_new_budget,
    get_user_budget_by_id,
    get_user_budgets,
)
from budget_app.utils import validate_request_body_keys_exist


class BudgetHandler:
    def get_budget(self, body):
        if not validate_request_body_keys_exist(["budget_id"], body):
            return {"message": "No budget_id provided"}, 422

        budget_id = body.get("budget_id")
        user_id = get_session()["id"]

        try:
            budget = get_user_budget_by_id(budget_id, user_id)
            return {"budget": budget}, 200
        except Exception as e:
            print(e)
            return {"message": "Failed to retreive budget."}, 503

    def get_budgets(self):
        user_id = get_session()["id"]

        try:
            budgets = get_user_budgets(user_id)
            return {"budgets": budgets}, 200
        except Exception as e:
            print(e)
            return {"message": "Failed to retreive budget."}, 503

    def create_budget(self, body):
        if not validate_request_body_keys_exist(
            ["name", "gross_income", "month_duration"], body
        ):
            return {"message": "Missing name, gross_income, and/or month_duration"}, 422

        name = body.get("name")
        gross_income_raw = body.get("gross_income")
        month_duration_raw = body.get("month_duration")
        user_id = get_session()["id"]

        try:
            budget_id = create_new_budget(
                user_id, name, month_duration_raw, gross_income_raw
            )
            budget = get_user_budget_by_id(budget_id, user_id)
            return {"budget": budget}, 200
        except ValueError as e:
            print(e)
            return {"message": str(e)}, 422
        except Exception as e:
            print(e)
            return {"message": "Failed to create budget."}, 503
