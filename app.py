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
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


# TO RUN LOCALLY: poetry run python app.py
app = Flask(__name__)

load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

print("Using DB:", os.getenv('DATABASE_URL')) # TODO remove in production, this is for checking db is being read

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signin.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/profile/<user>")
def profile(user):
    return render_template("profile.html", user=user)

if __name__ == "__main__":
    app.run(debug=True, port=5003)