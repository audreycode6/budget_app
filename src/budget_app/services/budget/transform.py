from budget_app.utils import format_float_to_usd


def raw_budget_to_budget(raw_budget):
    """
    Transform a Budget SQLAlchemy model instance into a serializable dict.

    Arg: raw_budget (Budget): A valid Budget instance with related BudgetItems loaded.

    NOTE:
    - *_raw fields are numeric and meant for calculations / forms
    - formatted fields are for display only
    """
    return {
        "id": raw_budget.id,
        "name": raw_budget.name,
        "month_duration": raw_budget.month_duration,
        "gross_income": float(raw_budget.gross_income),
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "total": item.total,
                # "total_raw": float(item.total),
            }
            for item in raw_budget.items
        ],
    }
