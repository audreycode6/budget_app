"""TODO: helper funcs to validate input that is reused (creating/editting budget/budget_items)"""


def validate_month_duration(month_duration_raw):
    try:
        month_duration = int(month_duration_raw)
        if month_duration not in [1, 12]:
            return "Month duration must be 1 (month) or 12 (year)."
        return False
    except ValueError:
        return "Month duration must be a number (1 or 12)."


def validate_positive_float(num_input):
    try:
        number = float(num_input)
        if not isinstance(number, (int, float)) or number < 0:
            return "must be a non negative number."
        return False
    except ValueError:
        return "must be a valid number."
