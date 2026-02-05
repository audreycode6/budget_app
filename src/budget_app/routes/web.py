# "Frontend API" only deals with HTML
from pathlib import Path
from flask import Blueprint, send_from_directory, current_app
from budget_app.routes.handlers.http.budget import BudgetHandler

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
web_blueprint = Blueprint("web", __name__)

budget_handler = BudgetHandler()


def _send_frontend(filename):
    """convert to string for send_from_directory"""
    return send_from_directory(str(FRONTEND_DIR), filename)


def _validate_budget_access(budget_id):
    """
    Validates that the user is logged in and budget exists and user has access.
    Returns True if valid or user isn't logged in, False otherwise.
    """
    result, status_code = budget_handler.get_budget({"budget_id": budget_id})

    if result.get("message") == "User not authenticated":
        return True
    return status_code == 200


# Wildcard catch-all route
@web_blueprint.route("/<path:catch_call>")
def all_routes(catch_call):
    return _send_frontend("unavailable_page.html")


@web_blueprint.route("/register")
def register_page():
    return _send_frontend("register.html")


@web_blueprint.route("/login")
def login_page():
    return _send_frontend("login.html")


@web_blueprint.route("/logout")
def logout_page():
    return _send_frontend("login.html")


@web_blueprint.route("/budgets")
def budgets_page():
    return _send_frontend("budgets.html")


@web_blueprint.route("/budget/<int:budget_id>")
def budget_page(budget_id):
    if not _validate_budget_access(budget_id):
        return _send_frontend("unavailable_page.html"), 404

    return _send_frontend("budget.html")


@web_blueprint.route("/create_budget")
def create_budget_page():
    return _send_frontend("create_budget.html")


@web_blueprint.route("/create_budget_items")
def create_budget_items_page():
    return _send_frontend("create_budget_items.html")


@web_blueprint.route("/budget/<int:budget_id>/edit")
def edit_budget_page(budget_id):
    if not _validate_budget_access(budget_id):
        return _send_frontend("unavailable_page.html"), 404

    return _send_frontend("edit_budget.html")


@web_blueprint.route("/delete_budget")
def delete_budget_page():
    return _send_frontend("budgets.html")


@web_blueprint.route("/")
def index_page():
    return _send_frontend("index.html")
