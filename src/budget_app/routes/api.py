# "Backend API" Only deals with JSON

"""
- /api/health | basic health endpoint

# AUTH
- /api/auth/signup | registers a new user account
- /api/auth/login | authenticates a user
- /api/auth/logout | delete user session

# BUDGET
- /api/budget/create | create new budget
- /api/budget/item/create | create budget items for existing budget
- /api/budget/edit | edit budget properties
- /api/budget/item/edit | edit budget item properties
- /api/budget/delete | delete budget
- /api/budget/item/delete | delete budget item properties
- GET /api/budgets | get all budgets
- POST /api/budget | get one budget

"""

from flask import Blueprint, request

from budget_app.routes.handlers.http.auth import AuthHandler
from budget_app.routes.handlers.http.budget import BudgetHandler

auth_handler = AuthHandler()
budget_handler = BudgetHandler()

api_blueprint = Blueprint("api", __name__)

"""
AUTH ROUTES
"""


@api_blueprint.route("/api/auth/authenticated")
@auth_handler.login_required
def authenticate_user():
    return {}, 200


@api_blueprint.route("/api/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


@api_blueprint.route("/api/auth/login", methods=["POST"])
def auth_login():
    body = request.get_json()
    return auth_handler.authenticate(body)


@api_blueprint.route("/api/auth/register", methods=["POST"])
def auth_register():
    body = request.get_json()
    return auth_handler.register(body)


@api_blueprint.route("/api/auth/logout", methods=["GET"])
@auth_handler.login_required
def auth_logout():
    return auth_handler.logout_user()


"""
BUDGET ROUTES
"""


@api_blueprint.route("/api/budget/<int:budget_id>", methods=["GET"])
def get_budget_by_id(budget_id):
    return budget_handler.get_budget({"budget_id": budget_id})


@api_blueprint.route("/api/budgets", methods=["GET"])
@auth_handler.login_required
def budgets():
    return budget_handler.get_budgets()


@api_blueprint.route("/api/budget/create", methods=["POST"])
@auth_handler.login_required
def budget_create():
    body = request.get_json()
    return budget_handler.create_budget(body)


@api_blueprint.route("/api/budget/item/create", methods=["POST"])
@auth_handler.login_required
def budget_item_create():
    body = request.get_json()
    return budget_handler.create_budget_item(body)


@api_blueprint.route("/api/budget/item/categories", methods=["GET"])
def get_budget_item_categories():
    categories = budget_handler.get_item_categories_list()
    return {"categories": categories}, 200


@api_blueprint.route("/api/budget/edit", methods=["POST"])
@auth_handler.login_required
def budget_edit():
    body = request.get_json()
    return budget_handler.edit_budget(body)


@api_blueprint.route("/api/budget/item/edit", methods=["POST"])
@auth_handler.login_required
def budget_item_edit():
    body = request.get_json()
    return budget_handler.edit_budget_item(body)


@api_blueprint.route("/api/budget/delete", methods=["POST"])
@auth_handler.login_required
def budget_delete():
    body = request.get_json()
    return budget_handler.delete_budget(body)


@api_blueprint.route("/api/budget/item/delete", methods=["POST"])
@auth_handler.login_required
def budget_item_delete():
    body = request.get_json()
    return budget_handler.delete_budget_item(body)
