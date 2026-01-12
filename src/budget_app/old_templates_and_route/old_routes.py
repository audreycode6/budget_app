from flask import Blueprint, flash, redirect, render_template, request, url_for
from ..services.auth import login_required
from ..services.auth.auth_service import (
    create_user,
    remove_user_from_session,
    authenticate_user,
    get_session,
)
from ..services.budget.budget_service import (
    create_new_budget,
    create_new_budget_item,
    get_budget_by_budget_and_user_id,
)

# OLD

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html", user=get_session())


@bp.route("/foo", methods=["GET"])
def foo():
    return {"foo": "bar", "baz": 1}, 200


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
        return render_template("/budget/create_budget.html", user=get_session())
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
                "/budget/create_budget.html",
                name=name,
                month_duration=month_duration_raw,
                gross_income=gross_income_raw,
                user=get_session(),
            )

        flash(f'"{name}" Budget created!', "success")
        return redirect(url_for("main.create_budget_items", budget_id=budget_id))


@bp.route("/budget/<budget_id>/items", methods=["GET", "POST"])
@login_required
def create_budget_items(budget_id):
    incomplete = True
    if request.method == "GET":
        return render_template(
            "budget_items.html",
            user=get_session(),
            budget_id=budget_id,
            budget_info=get_budget_by_budget_and_user_id(
                get_session()["id"], budget_id
            ),
        )
    if request.method == "POST":
        id = request.form["id"]
        name = request.form["name"].strip()
        category = request.form["category"]
        total = request.form["total"]  # TODO confirm data

        while incomplete:
            # TODO does this run in while loop until the complete button is submit
            try:
                create_new_budget_item(name, category, total, budget_id)
            except ValueError as e:
                flash(e, "error")
                return render_template(
                    "budget_items.html",
                    user=get_session(),
                    budget_id=budget_id,
                    budget_info=get_budget_by_budget_and_user_id(
                        get_session()["id"], budget_id
                    ),
                    name=name,
                    total=total,
                )  # TODO will i know where name and total goes since 3 forms of this ...?
            flash("New budget item added!", "success")
            return redirect(url_for("main.create_budget_item", budget_id=budget_id))

        flash("Budget complete!", "success")
        return render_template(
            "view_budget.html",
            user=get_session(),
            budget_id=budget_id,
            budget_info=get_budget_by_budget_and_user_id(
                get_session()["id"], budget_id
            ),
        )


@bp.route("/view_budget/<budget_id>", methods=["GET", "POST"])
@login_required
def view_budget(budget_id):
    if request.method == "GET":
        return render_template(
            "view_budget.html",
            budget_id=budget_id,
            budget_info=get_budget_by_budget_and_user_id(
                get_session()["id"], budget_id
            ),
        )
    # TODO get budget data
    if request.method == "POST":
        # TODO
        pass


@bp.route("/profile")
@login_required
def profile():

    # TODO need dict of budget_id and budget_name of all budgets belonging to user
    return render_template("profile.html")
    # TODO make template
