from ...models import Budget
from ...extensions import db
from flask import (session)

def create_budget_result(name, month_duration_raw, gross_income_raw):
    ''' return False if all good OR error message(s) '''
    error_messages = []

    # check name: not empty or unqiue to current user
    if not name:
        error_messages.append('Budget name must not be empty.')
    if Budget.query.filter_by(user_id=session['user_id'], name=name).first():
        error_messages.append('You already have a budget with that name.')

    # check month duration is either 1 or 12
    try:
        month_duration = int(month_duration_raw)
        if month_duration not in [1, 12]:
            error_messages.append('Month duration must be 1 (month) or 12 (year).')
    except ValueError:
        error_messages.append(('Month duration must be a number (1 or 12).'))
    
    # check gross_income is number >= 0
    try:
        gross_income = float(gross_income_raw)
        if not isinstance(gross_income, (int, float)) or gross_income < 0:
            error_messages.append('Gross income most be a non negative number.')
    except ValueError:
        error_messages.append('Gross income must be a valid number.')

    if error_messages:
        return error_messages
    
    # if no errors, safely convert for DB
    month_duration = int(month_duration_raw)
    gross_income = float(gross_income_raw)

    new_budget = Budget(
        name=name,
        month_duration=month_duration,
        gross_income=gross_income,
        user_id=session['user_id']
    )
    db.session.add(new_budget)
    db.session.commit()
    return new_budget.id # used to display correct budget view
# 