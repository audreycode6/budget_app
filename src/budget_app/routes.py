from flask import Blueprint, flash, redirect, render_template, request, url_for
from .services.auth.middleware import login_required
from .services.auth.auth_service import (
    create_user,
    remove_user_from_session,
    authenticate_user,
    get_session,
)
from .services.budget.budget_service import create_new_budget, get_budget

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html", user=get_session())


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        try:
            create_user(username, password)
        except ValueError as e:
            flash(e, "error")
            return render_template("signup.html"), 422

        flash("Account created! Please log in.")
        return redirect(url_for("main.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            authenticate_user(username, password)

        except ValueError as e:
            flash(e, "error")
            return render_template("login.html", username=username), 422

        return redirect(url_for("main.index"))  # TODO maybe switch to profile page


@bp.route("/logout")
def logout():
    remove_user_from_session()
    flash("Logged out successfully.", "success")
    return redirect(url_for("main.index"))


@bp.route("/create_budget", methods=["GET", "POST"])
@login_required
def create_budget():
    if request.method == "GET":
        return render_template("create_budget.html", user=get_session())
    if request.method == "POST":
        name = request.form["name"].strip()
        month_duration_raw = request.form["month_duration"]
        gross_income_raw = request.form["gross_income"]

        try:
            budget_id = create_new_budget(
                name, month_duration_raw, gross_income_raw
            )  # TODO  try catch

        except ValueError as e:
            flash(e, "error")
            return render_template(
                "create_budget.html",
                name=name,
                month_duration=month_duration_raw,
                gross_income=gross_income_raw,
                user=get_session(),
            )

        flash(f'"{name}" Budget created! TODO redirect to add budget_items', "success")
        return redirect(url_for("main.view_budget", budget_id=budget_id))


@bp.route("/view_budget/<budget_id>", methods=["GET", "POST"])
@login_required
def view_budget(budget_id):
    if request.method == "GET":
        return render_template(
            "view_budget.html",
            user=get_session(),
            budget_id=budget_id,
            budget_info=get_budget(budget_id),
        )
    # TODO get budget data
    if request.method == "POST":
        # TODO
        pass


@bp.route("/profile/<user>")
@login_required
def profile(user):
    return render_template("profile.html", user=user)
    # TODO make template
