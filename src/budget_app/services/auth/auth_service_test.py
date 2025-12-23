import unittest
from flask import session

from budget_app.services.auth.auth_service import (
    authenticate_user,
    create_user,
    get_session,
    remove_user_from_session,
)
from ...models import User
from budget_app import create_app
from ...extensions import db


class BaseTestCase(unittest.TestCase):
    """
    Creates an application context object,
    activates that context, telling Flask “everything that runs now belongs to this app.”
    Creates all database tables inside that context.
    """

    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            }
        )
        self.client = self.app.test_client()

        self.context = self.app.app_context()  # creates an application context object
        self.context.push()  # activates that context
        db.create_all()

    def tearDown(self):
        """
        Clear the current database session,
        drops all tables (each test starts fresh with a clean in-memory DB).
        Deactivates the app context,so Flask doesn’t think your test app is
        still active after the test ends.
        """
        db.session.remove()  # clears current database session
        db.drop_all()  # drops all tables
        self.context.pop()  # deactivates the app context


class CreateUser(BaseTestCase):
    def test_sucess(self):
        user_exists = User.query.filter_by(username="foo").first()
        self.assertFalse(user_exists)

        response = create_user(username="foo", password="bar")
        self.assertTrue(response)

    def test_user_exists(self):
        create_user(username="foo", password="bar")

        user_exists = User.query.filter_by(username="foo").first()
        self.assertTrue(user_exists)

        response = create_user(username="foo", password="bar")
        self.assertFalse(response)


class UserDataFixture(BaseTestCase):
    def setUp(self):
        super().setUp()

        # create user in db
        create_user(username="foo", password="bar")


class AuthenticateUser(UserDataFixture):
    def setUp(self):
        super().setUp()

    def test_success(self):
        response = authenticate_user(username="foo", password="bar")
        self.assertEqual({"id": 1, "username": "foo"}, response)

    def test_invalid_username(self):
        response = authenticate_user(username="notuser", password="bar")
        self.assertIsNone(response)

    def test_invalid_passwrd(self):
        response = authenticate_user(username="foo", password="notpassword")
        self.assertIsNone(response)

    def test_all_invalid_args(self):
        response = authenticate_user(username="notuser", password="notpassword")
        self.assertIsNone(response)


class GetSession(BaseTestCase):
    def test_success(self):
        with (
            self.app.test_request_context()
        ):  # create and simulate user login in session
            session["user_id"] = {"id": 1, "username": "foo"}

            response = get_session()
            self.assertEqual(response["id"], 1)
            self.assertEqual(response["username"], "foo")

    def test_no_user_in_session(self):
        with self.app.test_request_context():
            with self.assertRaisesRegex(PermissionError, "User not authenticated."):
                get_session()


class RemoveUserFromSession(BaseTestCase):
    def test_success(self):
        with (
            self.app.test_request_context()
        ):  # create and simulate user login in session
            session["user_id"] = {"id": 1, "username": "foo"}

            remove_user_from_session()
            self.assertNotIn("user_id", session)


if __name__ == "__main__":
    unittest.main(verbosity=2)
