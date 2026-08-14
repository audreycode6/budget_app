"""Test-only helpers. Not imported by application code."""

import unittest
from budget_app import create_app, db

TEST_CONFIG = {
    "TESTING": True,
    "SECRET_KEY": "test",
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
}


def make_test_app(**overrides):
    """Flask app configured for tests, independent of the ambient .env"""
    return create_app({**TEST_CONFIG, **overrides})


class DatabaseTestCase(unittest.TestCase):
    """Test app + a fresh in-memory schema per test.

    Creates an application context object,
    activates that context, telling Flask
    “everything that runs now belongs to this app.”
    Creates all database tables inside that context.
    Without an application context object, Flask wouldn’t
    know which app you’re referring to when you interact
    with things like the database or configuration
    """

    def setUp(self):
        self.app = make_test_app()
        self.client = self.app.test_client()

        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()
