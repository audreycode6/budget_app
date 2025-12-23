from budget_app.services.auth.auth_service import get_session
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
from budget_app.utils import validate_request_body_keys_exist, stringify_attributes


# TODO when testing test_budget.py need to do function mocking for the funcs already tested (get_session, etc...)
class BudgetHandler:
    BUDGET_ATTRIBUTES = ["name", "gross_income", "month_duration"]
    BUDGET_ITEM_ATTRIBUTES = ["name", "category", "total"]

    def get_budget(self, body):
        if not validate_request_body_keys_exist(["budget_id"], body):
            return {"message": "No budget_id provided"}, 422

        budget_id = body.get("budget_id")
        user_id = get_session()["id"]

        try:
            budget = get_budget(budget_id, user_id)
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
        if not validate_request_body_keys_exist(BudgetHandler.BUDGET_ATTRIBUTES, body):
            return {
                "message": f"Missing attribute(s) to update. Valid attributes are: {stringify_attributes(BudgetHandler.BUDGET_ATTRIBUTES)}"
            }, 422

        name = body.get("name")
        gross_income_raw = body.get("gross_income")
        month_duration_raw = body.get("month_duration")
        user_id = get_session()["id"]

        try:
            budget_id = create_new_budget(
                user_id, name, month_duration_raw, gross_income_raw
            )
            budget = get_budget(budget_id, user_id)
            return {"budget": budget}, 200
        except ValueError as e:
            print(e)
            return {"message": str(e)}, 422
        except Exception as e:
            print(e)
            return {"message": "Failed to create budget."}, 503

    def create_budget_item(self, body):
        required_attributes = BudgetHandler.BUDGET_ITEM_ATTRIBUTES + ["budget_id"]
        if not validate_request_body_keys_exist(required_attributes, body):
            return {
                "message": f"Missing attribute(s) to update. Valid attributes are: {stringify_attributes(required_attributes)}"
            }, 422

        name = body.get("name")
        category = body.get("category")
        total = body.get("total")
        budget_id = body.get("budget_id")
        user_id = get_session()["id"]

        try:
            budget_item_id = create_new_budget_item(
                name, category, total, budget_id, user_id
            )
            budget = get_budget(budget_id, user_id)
            return {"budget": budget, "budget_item_id": budget_item_id}, 200

        except ValueError as e:
            print(e)
            return {"message": str(e)}, 422
        except Exception as e:
            print(e)
            return {"message": "Failed to create budget item."}

    def edit_budget(self, body):
        if not validate_request_body_keys_exist(["budget_id"], body):
            return {"message": "Missing budget_id"}, 422

        BudgetHandler.BUDGET_ATTRIBUTES = ["name", "gross_income", "month_duration"]

        attributes_to_update = attributes_to_update_dict(
            body, BudgetHandler.BUDGET_ATTRIBUTES
        )
        if not attributes_to_update:
            return {
                "message": f"Missing attribute(s) to update. Valid attributes are: {stringify_attributes(BudgetHandler.BUDGET_ATTRIBUTES)}"
            }, 422

        user_id = get_session()["id"]
        budget_id = body.get("budget_id")
        try:
            budget_id = edit_budget(budget_id, user_id, attributes_to_update)
            updated_budget = get_budget(budget_id, user_id)
            return {"budget_id": budget_id, "budget": updated_budget}, 200
        except ValueError as e:
            print(e)
            return {"message": str(e)}, 422
        except Exception as e:
            print(e)
            return {"message": "Failed to update budget."}, 503

    def edit_budget_item(self, body):
        if not validate_request_body_keys_exist(["budget_id", "item_id"], body):
            return {"message": "Missing budget_id and/or item_id"}, 422

        attributes_to_update = attributes_to_update_dict(
            body, BudgetHandler.BUDGET_ITEM_ATTRIBUTES
        )
        if not attributes_to_update:
            return {
                "message": f"Missing attribute(s) to update. Valid attributes are: {stringify_attributes(BudgetHandler.BUDGET_ITEM_ATTRIBUTES)}"
            }, 422

        user_id = get_session()["id"]
        budget_id = body.get("budget_id")
        item_id = body.get("item_id")

        try:
            budget_item_id = edit_budget_item(item_id, budget_id, attributes_to_update)
            updated_budget = get_budget(budget_id, user_id)
            return {"budget_item_id": budget_item_id, "budget": updated_budget}, 200
        except ValueError as e:
            print(e)
            return {"message": str(e)}, 422
        except Exception as e:
            print(e)
            return {"message": "Failed to update budget item."}, 503

    def delete_budget(self, body):
        if not validate_request_body_keys_exist(["budget_id"], body):
            return {"message": "Missing budget_id"}, 422

        budget_id = body.get("budget_id")
        user_id = get_session()["id"]

        try:
            budget_name = delete_budget(budget_id, user_id)
            return {
                "message": f"Budget '{budget_name}' and its contents has been deleted"
            }, 200

        except ValueError as e:
            print(e)
            return {"message": str(e)}, 422

        except Exception as e:
            print(e)
            return {"message": "Failed to delete budget."}, 503

    def delete_budget_item(self, body):
        if not validate_request_body_keys_exist(["item_id", "budget_id"], body):
            return {"message": "Missing item_id and/or budget_id"}, 422

        item_id = body.get("item_id")
        budget_id = body.get("budget_id")

        try:
            item_description = delete_budget_item(item_id, budget_id)
            return {
                "message": f"Budget item in {item_description} and its contents has been deleted."
            }, 200

        except ValueError as e:
            print(e)
            return {"message": str(e)}, 422

        except Exception as e:
            print(e)
            return {"message": "Failed to delete budget."}, 503
