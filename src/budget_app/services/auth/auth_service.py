from ...extensions import db
from flask import session
from ...models import User


def create_user(username, password):
    # Check username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return False

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return True


def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session["user_id"] = {
            "id": user.id,
            "username": user.username,
        }  # store user_id in session to access session info
        return True
    else:
        return False


def get_session():
    return session.get("user_id", None)


def remove_user_from_session():
    session.clear()
