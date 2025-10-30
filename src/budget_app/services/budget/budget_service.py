from ...models import Budget
from ...extensions import db
from flask import (session)
from ..auth.auth_service import get_session

def create_new_budget(name, month_duration_raw, gross_income_raw):
    ''' return budget_id if valid input OR raise exceptions '''

    # check name: not empty or unqiue to current user
    if not name:
        raise ValueError('Budget name must not be empty.')
    if Budget.query.filter_by(user_id=get_session()['id'], name=name).first():
        raise ValueError('You already have a budget with that name.')

    # check month duration is either 1 or 12
    try:
        month_duration = int(month_duration_raw)
    except ValueError:
        raise ValueError('Month duration must be a number (1 or 12).') # TODO check
    if month_duration not in [1, 12]:
        raise ValueError('Month duration must be 1 (month) or 12 (year).')
    
    # check gross_income is number >= 0
    try:
        gross_income = float(gross_income_raw)
    except ValueError:
        raise ValueError('Gross income must be a valid number.')
    if not isinstance(gross_income, (int, float)) or gross_income < 0:
        raise ValueError('Gross income most be a non negative number.')
    
    # if no errors, safely convert for DB
    month_duration = int(month_duration_raw)
    gross_income = float(gross_income_raw)
    
    new_budget = Budget(
        name=name,
        month_duration=month_duration,
        gross_income=gross_income,
        user_id=get_session()['id']
    )
    db.session.add(new_budget)
    db.session.commit()
    return new_budget.id # used to display correct budget view

def get_budget(budget_id):
    # TODO fix to grab data from budget db 
    budget_info = Budget.query.filter_by(id=budget_id).first() # ends up getting the __repr__
    # budget_info = Budget.query.filter_by(user_id=get_session()['id'], id=budget_id).all()
    return budget_info
