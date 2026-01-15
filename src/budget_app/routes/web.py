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
    # TODO add link to individual budget
    return _send_frontend("budgets.html")


@web_blueprint.route("/budget")
# TODO view single budget by budget.id and user.id
# TODO fix so id is in path ... ? if thats good practice ..?
def budget_page():
    return _send_frontend("budget.html")


# TODO index home page - demo and intro


@web_blueprint.route("/create_budget")
# TODO take in budget name, month duration, gross income
def create_budget_page():  # TODO budget or budget_items
    return _send_frontend("create_budget.html")


@web_blueprint.route("/create_budget_items")
def create_budget_items_page():
    # TODO take in item id, item name, item category, item total
    """while loop of create_new_budget_item until they click done/submit"""
    return _send_frontend("create_budget_items.html")


# @web_blueprint.route("/edit_budget")
# # TODO take in budget.id, user.id and attributes to update dict (name, month_dration, gross_incmoe)
# def edit_budget_page():  # TODO
#     return _send_frontend("edit_budget.html")


# @web_blueprint.route("/edit_budget_item")
# # TODO take in budget id and item.id + attributes to update dict (name, total, category, )
# def edit_budget_item_page():  # TODO
#     return _send_frontend("edit_budget_item.html")


# @web_blueprint.route("/delete_budget")

# # TODO redirect to index/profile page of all users budgets
# def delete_budget_page():  # TODO
#     return _send_frontend("budgets.html")


# @web_blueprint.route("/delete_item")
# # TODO redirect to budget with its update (item gone)
# def create_budget_page():  # TODO
#     return _send_frontend("budget.html")
