from dotenv import load_dotenv
from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
    )
from functools import wraps
import os

# Load environment variables first
load_dotenv()

from .extensions import db, migrate

app = Flask(__name__) 

# Configuration
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)

from budget_app import models
from budget_app.models import User, Budget, BudgetItem

def is_signed_in():
    return session.get('username') 

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        if not username or not password:
            flash('Username or password must be filled out.', 'danger')
            return render_template('signup.html'), 422
        
        # Check username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken.', 'danger')
            return render_template('signup.html'), 422
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index')) # TODO maybe switch to profile page 
        else:
            flash('Invalid username or password.', 'danger')
            return render_template("login.html", username=username), 422

    return render_template("login.html")

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully. 1', 'info')
    return redirect(url_for('index'))

@app.route("/profile/<user>")
@login_required
def profile(user):
    return render_template("profile.html", user=user)
    # TODO make template

if __name__ == "__main__":
    app.run(debug=True, port=5003)