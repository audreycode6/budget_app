from budget_app.utils import format_float_to_usd


def raw_budget_to_budget(raw_budget):
    return {
        "id": raw_budget.id,
        "name": raw_budget.name,
        "month_duration": raw_budget.month_duration,
        "gross_income": format_float_to_usd(float(raw_budget.gross_income)),
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "total": item.total,
            }
            for item in raw_budget.items
        ],
    }
