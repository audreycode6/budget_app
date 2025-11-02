from budget_app.services.budget.transform import raw_budget_to_budget
from ...models import Budget, BudgetItem
from ...extensions import db
from ..auth.auth_service import get_session
from ...utils import format_float_to_usd

VALID_BUDGET_ITEM_CATEGORY = ["deductions", "bills", "savings"]


def create_new_budget(user_id, name, month_duration_raw, gross_income_raw):
    """return budget_id if valid input OR raise exceptions"""

    # check name: not empty or unqiue to current user
    if not name:
        raise ValueError("Budget name must not be empty.")
    if Budget.query.filter_by(user_id=get_session()["id"], name=name).first():
        raise ValueError("You already have a budget with that name.")
    # TODO test non unique is caught

    # check month duration is either 1 or 12
    try:
        month_duration = int(month_duration_raw)
    except ValueError:
        raise ValueError("Month duration must be a number (1 or 12).")  # TODO check
    if month_duration not in [1, 12]:
        raise ValueError("Month duration must be 1 (month) or 12 (year).")

    # check gross_income is number >= 0
    try:
        gross_income = float(gross_income_raw)
    except ValueError:
        raise ValueError("Gross income must be a valid number.")
    if not isinstance(gross_income, (int, float)) or gross_income < 0:
        raise ValueError("Gross income most be a non negative number.")

    # if no errors, safely convert for DB
    month_duration = int(month_duration_raw)
    gross_income = float(gross_income_raw)

    new_budget = Budget(
        name=name,
        month_duration=month_duration,
        gross_income=gross_income,
        user_id=user_id,
    )
    db.session.add(new_budget)
    db.session.commit()
    return new_budget.id  # used to display correct budget view


def create_new_budget_item(name, category, total, budget_id):
    # TODO validate user inputs: name and cost, raise error if invalid
    # else insert items into budget_item and TODO what to return
    if not name:
        raise ValueError("Budget item name must not be empty.")
    # TODO budget_item.name should be unique to the current budget
    #   (other budgets user has can have same budget name but not same budget)

    # TODO testing to ensure category is working but can remove after
    if category not in VALID_BUDGET_ITEM_CATEGORY:
        raise ValueError(f"internal error, category {category} is not valid")

    try:
        float(total)
    except ValueError:
        raise "Total must be a number"
    if not isinstance(total, (int, float)) or total < 0:
        raise ValueError("Total most be a non negative number.")

    # if no errors, safely convert for DB
    # TODO left off here
    new_budget_item = BudgetItem(
        name=name,
        category=category,
        total=total,
        budget_id=budget_id,
    )


def get_user_budget_by_id(budget_id, user_id):
    raw_budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
    print(raw_budget)

    if raw_budget is None:
        print(f"Could not find budget with id: {budget_id} and user_id: {user_id}")
        return {}

    return raw_budget_to_budget(raw_budget)


def get_user_budgets(user_id):
    raw_budgets = Budget.query.filter_by(user_id=user_id).all()

    if not raw_budgets:
        print(f"Could not find budgets for user_id: {user_id}")
        return []

    return [raw_budget_to_budget(budget) for budget in raw_budgets]
