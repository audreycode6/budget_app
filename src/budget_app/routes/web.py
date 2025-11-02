# "Frontend API" only deals with HTML
from flask import Blueprint, render_template, request

from budget_app.routes.api import budgets as api_budgets

web_blueprint = Blueprint("web", __name__)


@web_blueprint.route("/")
def index():
    return render_template("index.html")


@web_blueprint.route("/budgets")
def render_budgets():
    budgets = api_budgets()
    return render_template("budgets.html", budgets=budgets)
