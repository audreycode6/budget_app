from functools import wraps

from flask import session
from budget_app.services.auth.auth_service import (
    authenticate_user,
    create_user,
    remove_user_from_session,
)
from budget_app.utils import validate_request_body_keys_exist


class AuthHandler:
    """
    Auth handler middleware
    """

    def login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return {"message": "You must be authenticated to use this route."}, 401
            return f(*args, **kwargs)

        return decorated_function

    """
    Auth handlers
    """

    def authenticate(self, body):
        if not validate_request_body_keys_exist(["username", "password"], body):
            return {"message": "Username and/or password must be provided."}, 422

        try:
            user_data = authenticate_user(body["username"], body["password"])

            if user_data:
                session["user_id"] = user_data
                return {"message": "Successfully authenticated."}, 200
            else:
                return {"message": "Invalid username or password."}, 401

        except Exception as e:
            print(e)
            return {"message": "Failed to authenticate user."}, 503

    def register(self, body):
        if not validate_request_body_keys_exist(["username", "password"], body):
            return {"message": "Username and/or password must be provided."}, 422

        try:
            username = body["username"]
            password = body["password"]

            if create_user(username, password):
                return {"message": "User successfully registed."}, 200
            else:
                return {"message": "Username already exists."}, 422

        except Exception as e:
            print(e)
            return {"message": "Failed to register user."}, 503

    def logout_user(self):
        remove_user_from_session()
        return {"message": "Deleted user from session"}, 200
