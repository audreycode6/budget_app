from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    )
from .services.auth.middleware import login_required
from .services.auth.auth_service import (
    create_user,
    remove_user_from_session,
    valid_login)
from .services.budget.budget_service import (
    create_budget_result)

bp = Blueprint('main', __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        signup_result = create_user(username, password)

        if signup_result == 'empty user or pw':
            flash('Username or password must be filled out.', 'error')
            return render_template('signup.html'), 422
        
        if signup_result == 'existing user':
            flash('Username already taken.', 'error')
            return render_template('signup.html'), 422

        flash('Account created! Please log in.')
        return redirect(url_for('main.login'))
    
    return render_template("signup.html")

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if valid_login(username, password):
            flash('Login successful!', 'success')
            return redirect(url_for('main.index')) # TODO maybe switch to profile page 
    
        flash('Invalid username or password.', 'error')
        return render_template("login.html", username=username), 422

    return render_template("login.html")

@bp.route('/logout')
def logout():
    remove_user_from_session()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('main.index'))

@bp.route('/create_budget', methods=['GET', 'POST'])
@login_required
def create_budget():
    if request.method == "POST":
        name = request.form['name'].strip()
        month_duration_raw = request.form['month_duration']
        gross_income_raw = request.form['gross_income']

        result = create_budget_result(name, month_duration_raw, gross_income_raw)
        if isinstance(result, list): # TODO doesnt feel so descriptive but it does the job (?)
            for error in result:
                flash(error, 'error')
            return render_template('create_budget.html', 
                                   name=name, 
                                   month_duration=month_duration_raw, 
                                   gross_income=gross_income_raw)

        flash(f'"{name}" Budget created! TODO redirect to add budget_items', 'success')
        return redirect(url_for('main.view_budget', budget_id=result))
    
    return render_template("create_budget.html")

@bp.route('/view_budget/<budget_id>', methods=['GET', 'POST'])
@login_required
def view_budget(budget_id):
    # TODO
    return render_template("view_budget.html")

@bp.route("/profile/<user>")
@login_required
def profile(user):
    return render_template("profile.html", user=user)
    # TODO make template
