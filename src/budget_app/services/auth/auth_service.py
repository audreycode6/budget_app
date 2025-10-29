from ...extensions import db
from flask import (session)
from ...models import User

def create_user(username, password):
    if not username or not password:
        return 'empty user or pw'
    
    # Check username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return 'existing user'
    
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()


def valid_login(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user_id'] = user.id # store user_id in session to allow signed in view
        return True
    else:
        return False

def remove_user_from_session():
    session.pop('user_id', None)