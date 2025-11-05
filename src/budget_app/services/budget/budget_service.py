from budget_app.services.budget.transform import raw_budget_to_budget
from budget_app.services.budget.validate_input import (
    validate_month_duration,
    validate_positive_float,
)
from ...models import Budget, BudgetItem
from ...extensions import db

VALID_BUDGET_ITEM_CATEGORY = ["deductions", "bills", "savings"]


def get_formatted_budget(budget_id, user_id):
    raw_budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()

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


def create_new_budget(user_id, name, month_duration_raw, gross_income_raw):
    """
    return budget_id if valid input OR raise exceptions
    """

    # check name: not empty or unqiue to current user
    if not name:
        raise ValueError("Budget name must not be empty.")
    if Budget.query.filter_by(user_id=user_id, name=name).first():
        raise ValueError("You already have a budget with that name.")

    # check month duration is either 1 or 12
    invalid_month_duration_message = validate_month_duration(month_duration_raw)
    if invalid_month_duration_message:
        raise ValueError(invalid_month_duration_message)

    # check gross_income is number >= 0
    invalid_gross_income_message = validate_positive_float(gross_income_raw)
    if invalid_gross_income_message:
        raise ValueError(f"Gross income {invalid_gross_income_message}")

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


def create_new_budget_item(name, category, total, budget_id, user_id):
    """
    Validate user inputs: name and cost, raise error if invalid
    else insert items into budget_item and return new budget item id
    """
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
    if not budget:
        print(f"Budget_id: {budget_id}, doesn't belong to user with user_id {user_id}")
        raise ValueError("Invalid budget.")
    if not name:
        raise ValueError("Budget item name must not be empty.")

    if category not in VALID_BUDGET_ITEM_CATEGORY:
        raise ValueError(f"Category: '{category}' is not valid")

    invalid_total_message = validate_positive_float(total)
    if invalid_total_message:
        raise ValueError(f"Total {invalid_total_message}")

    new_budget_item = BudgetItem(
        name=name,
        category=category,
        total=total,
        budget_id=budget_id,
    )
    db.session.add(new_budget_item)
    db.session.commit()

    return new_budget_item.id


def edit_budget(budget_id, user_id, attributes_to_edit):
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
    if not budget:
        print(f"Budget_id: {budget_id}, doesn't belong to user with user_id {user_id}")
        raise ValueError(
            "Invalid budget."
        )  # TODO thoughts on this error message (?) MAKE a custom exception class

    for attribute, new_value in attributes_to_edit.items():
        # Validate new_value
        if attribute == "name":
            if not new_value:
                raise ValueError("New name must not be empty.")
            if (
                Budget.query.filter_by(user_id=user_id, name=new_value).first()
                and budget.name != new_value
            ):  # error if name different than current budget.name value and
                # exists in users other budgets
                raise ValueError("You already have a budget with that name.")

        if attribute == "gross_income":
            error_message = validate_positive_float(new_value)
            if error_message:
                raise ValueError(f"{attribute} {error_message}")

        if attribute == "month_duration":
            error_message = validate_month_duration(new_value)
            if error_message:
                raise ValueError(error_message)

        # Update new_value
        setattr(budget, attribute, new_value)

    db.session.commit()

    return budget.id


def edit_budget_item(item_id, budget_id, attributes_to_edit):
    budget_item = BudgetItem.query.filter_by(id=item_id, budget_id=budget_id).first()
    if not budget_item:
        print(
            f"Budget item_id: {item_id}, doesn't belong to user with budget_id {budget_id}"
        )
        raise ValueError("Invalid budget item.")

    # Validate new_value
    for attribute, new_value in attributes_to_edit.items():
        # Validate new_value
        if attribute == "name":
            if not new_value:
                raise ValueError("New name must not be empty.")

        if attribute == "category":
            if new_value not in VALID_BUDGET_ITEM_CATEGORY:
                raise ValueError(f"Category: '{new_value}' is not valid")

        if attribute == "total":
            invalid_total_message = validate_positive_float(new_value)
            if invalid_total_message:
                raise ValueError(f"Total {invalid_total_message}")

        # Update new_value
        setattr(budget_item, attribute, new_value)

    db.session.commit()

    return item_id  # TODO what should be returned


def attributes_to_update_dict(body, list_of_attributes):
    attributes_to_update = {}
    for attribute in list_of_attributes:
        new_value = body.get(attribute)
        if new_value is not None:
            attributes_to_update[attribute] = new_value

    return attributes_to_update


def delete_budget(budget_id, user_id):
    # Retrieve the budget to delete
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
    if not budget:
        print(f"Budget_id: {budget_id}, doesn't belong to user with user_id {user_id}")
        raise ValueError("Invalid budget.")

    budget_name = budget.name

    # Delete the object
    db.session.delete(budget)
    db.session.commit()
    return budget_name


def delete_budget_item(item_id, budget_id):
    # Retrieve the budget to delete
    budget_item = BudgetItem.query.filter_by(id=item_id, budget_id=budget_id).first()
    if not budget_item:
        print(
            f"Budget item_id: {item_id}, doesn't belong to user with budget_id {budget_id}"
        )
        raise ValueError("Invalid budget item.")

    item_description = (
        f"Category: '{budget_item.category}' and with Name:'{budget_item.name}'"
    )

    # Delete the object
    db.session.delete(budget_item)
    db.session.commit()
    return item_description
