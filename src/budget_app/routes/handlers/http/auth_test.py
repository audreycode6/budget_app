import unittest
from unittest.mock import patch

from flask import session

from budget_app import create_app
from budget_app.routes.handlers.http.auth import AuthHandler

"""Test the auth.py handler: use function mocking for the 
helper funcs that have been tested in other unittests

handler tests answer questions like:
Given X input, does this handler call the right services
 and return the correct HTTP response?
 
- Handler imports create local references
- patch() must target that local reference
- You do not change test imports
- You do not mock the service module directly
- The patch string = handler module path + function name
"""


class BaseAuthHandlerTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.handler = AuthHandler()


class TestAuthenticate(BaseAuthHandlerTest):

    @patch("budget_app.routes.handlers.http.auth.authenticate_user")
    @patch("budget_app.routes.handlers.http.auth.validate_request_body_keys_exist")
    def test_success(
        self, mock_validate_request_body_keys_exist, mock_authenticate_user
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_authenticate_user.return_value = {"id": 1, "username": "foo"}

        with self.app.test_request_context():
            response, status = self.handler.authenticate(
                {"username": "foo", "password": "bar"}
            )

            self.assertEqual(status, 200)
            self.assertEqual(response["message"], "Successfully authenticated.")
            self.assertEqual(session["user_id"]["id"], 1)

    @patch("budget_app.routes.handlers.http.auth.validate_request_body_keys_exist")
    def test_missing_body_keys(self, mock_validate_request_body_keys_exist):
        mock_validate_request_body_keys_exist.return_value = False

        with self.app.test_request_context():
            response, status = self.handler.authenticate({})

            self.assertEqual(status, 422)
            self.assertIn(
                "Username and/or password must be provided.", response["message"]
            )

    @patch("budget_app.routes.handlers.http.auth.authenticate_user")
    @patch("budget_app.routes.handlers.http.auth.validate_request_body_keys_exist")
    def test_invalid_credentials(
        self, mock_validate_request_body_keys_exist, mock_authenticate_user
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_authenticate_user.return_value = None

        with self.app.test_request_context():
            response, status = self.handler.authenticate(
                {"username": "foo", "password": "wrong"}
            )

            self.assertEqual(status, 401)
            self.assertIn("Invalid username or password.", response["message"])
            self.assertNotIn("user_id", session)

    @patch("budget_app.routes.handlers.http.auth.authenticate_user")
    @patch("budget_app.routes.handlers.http.auth.validate_request_body_keys_exist")
    def test_service_exception(
        self, mock_validate_request_body_keys_exist, mock_authenticate_user
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_authenticate_user.side_effect = Exception("service unavailable")

        with self.app.test_request_context():
            response, status = self.handler.authenticate(
                {"username": "foo", "password": "bar"}
            )

            self.assertEqual(status, 503)
            self.assertIn("Failed to authenticate user.", response["message"])


class TestRegister(BaseAuthHandlerTest):

    @patch("budget_app.routes.handlers.http.auth.create_user")
    @patch("budget_app.routes.handlers.http.auth.validate_request_body_keys_exist")
    def test_success(self, mock_validate_request_body_keys_exist, mock_create_user):
        mock_validate_request_body_keys_exist.return_value = True
        mock_create_user.return_value = True

        with self.app.test_request_context():
            response, status = self.handler.register(
                {"username": "foo", "password": "bar"}
            )

            self.assertEqual(status, 200)
            self.assertIn("User successfully registered.", response["message"])

    @patch("budget_app.routes.handlers.http.auth.create_user")
    @patch("budget_app.routes.handlers.http.auth.validate_request_body_keys_exist")
    def test_username_already_exists(
        self, mock_validate_request_body_keys_exist, mock_create_user
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_create_user.return_value = False

        with self.app.test_request_context():
            response, status = self.handler.register(
                {"username": "foo", "password": "bar"}
            )
            self.assertEqual(status, 422)
            self.assertIn("Username already exists.", response["message"])

    @patch("budget_app.routes.handlers.http.auth.validate_request_body_keys_exist")
    def test_missing_body_username_key(self, mock_validate_request_body_keys_exist):
        mock_validate_request_body_keys_exist.return_value = False

        with self.app.test_request_context():
            response, status = self.handler.register(
                {"username": "", "password": "bar"}
            )
            self.assertEqual(status, 422)
            self.assertIn(
                "Username and/or password must be provided.", response["message"]
            )

    @patch("budget_app.routes.handlers.http.auth.validate_request_body_keys_exist")
    def test_missing_body_pw_key(self, mock_validate_request_body_keys_exist):
        mock_validate_request_body_keys_exist.return_value = False

        with self.app.test_request_context():
            response, status = self.handler.register(
                {"username": "foo", "password": ""}
            )
            self.assertEqual(status, 422)
            self.assertIn(
                "Username and/or password must be provided.", response["message"]
            )

    @patch("budget_app.routes.handlers.http.auth.validate_request_body_keys_exist")
    def test_missing_body_keys(self, mock_validate_request_body_keys_exist):
        mock_validate_request_body_keys_exist.return_value = False

        with self.app.test_request_context():
            response, status = self.handler.register({})
            self.assertEqual(status, 422)
            self.assertIn(
                "Username and/or password must be provided.", response["message"]
            )

    @patch("budget_app.routes.handlers.http.auth.create_user")
    @patch("budget_app.routes.handlers.http.auth.validate_request_body_keys_exist")
    def test_service_exception(
        self, mock_validate_request_body_keys_exist, mock_create_user
    ):
        mock_validate_request_body_keys_exist.return_value = True
        mock_create_user.side_effect = Exception("service unavailable")

        with self.app.test_request_context():
            response, status = self.handler.register(
                {"username": "foo", "password": "bar"}
            )

            self.assertEqual(status, 503)
            self.assertIn("Failed to register user.", response["message"])


class TestLogoutUser(BaseAuthHandlerTest):

    @patch("budget_app.routes.handlers.http.auth.remove_user_from_session")
    def test_success(self, mock_remove_user_from_session):
        with self.app.test_request_context():
            response, status = self.handler.logout_user()

            mock_remove_user_from_session.assert_called_once()
            self.assertEqual(status, 200)
            self.assertIn("Deleted user from session", response["message"])


class TestLoginRequired(BaseAuthHandlerTest):

    def test_allows_authorized_user(self):
        def protected_func():
            return {"message": "ok"}, 200

        decorated_func = self.handler.login_required(protected_func)

        with self.app.test_request_context():
            session["user_id"] = {"id": 1, "username": "foo"}
            response, status = decorated_func()

            self.assertEqual(200, status)
            self.assertIn("ok", response["message"])

    def test_block_unauthorized(self):
        def protected_func():
            return {"message": "ok"}, 200

        decorated_func = self.handler.login_required(protected_func)

        with self.app.test_request_context():
            response, status = decorated_func()

            self.assertEqual(status, 401)
            self.assertIn(
                "You must be authenticated to use this route.", response["message"]
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
