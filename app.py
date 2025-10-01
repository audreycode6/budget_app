from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
    )

app = Flask(__name__)

@app.route("/")
def index():
    render_template("index.html")

@app.route("/signup")
def signup():
    render_template("signup.html")

@app.route("/login")
def login():
    render_template("login.html")


@app.route("/profile/<user>")
def profile():
    render_template("profile.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)