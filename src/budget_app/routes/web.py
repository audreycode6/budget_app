# "Frontend API" only deals with HTML
from pathlib import Path
from flask import Blueprint, send_from_directory, current_app

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
web_blueprint = Blueprint("web", __name__)


def _send_frontend(filename):
    """convert to string for send_from_directory"""
    return send_from_directory(str(FRONTEND_DIR), filename)


@web_blueprint.route(
    "/register"
)  # TODO add flash when successful and redirecting to login
def register_page():
    return _send_frontend("register.html")


@web_blueprint.route("/login")
def login_page():
    return _send_frontend("login.html")


@web_blueprint.route("/logout")  # TODO change to logged out view of demo/login page
def logout_page():
    return _send_frontend("login.html")


@web_blueprint.route("/budgets")
def budgets_page():
    return _send_frontend("budgets.html")


@web_blueprint.route("/budget/<int:budget_id>")
# TODO fix so that can only see your budget/ error display correctly
def budget_page(budget_id):
    return _send_frontend("budget.html")


@web_blueprint.route("/create_budget")
def create_budget_page():
    return _send_frontend("create_budget.html")


@web_blueprint.route("/create_budget_items")
def create_budget_items_page():
    return _send_frontend("create_budget_items.html")


@web_blueprint.route("/budget/<int:budget_id>/edit")
def edit_budget_page(budget_id):
    return _send_frontend("edit_budget.html")


@web_blueprint.route("/delete_budget")
def delete_budget_page():
    return _send_frontend("budgets.html")


# TODO index home page - demo and intro
@web_blueprint.route("/")
def index_page():
    return _send_frontend("index.html")
