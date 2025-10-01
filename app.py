from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
    )
# TO RUN LOCALLY: poetry run python app.py
app = Flask(__name__)

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