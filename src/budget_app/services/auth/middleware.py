from flask import (
    flash,
    redirect,
    session,
    url_for,
    )

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to access this page', 'error')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function