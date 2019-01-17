from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from passlib.context import CryptContext
import pprint

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username and password was submitted
        if not request.form.get("username") or not request.form.get("password"):
            return apology("must provide username/password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        # return redirect(url_for("index"))
        return render_template("index.html")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("homepage"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username and password was submitted
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("email"):
            return apology("must provide username/password/email")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username doesn't already exist
        if len(rows) == 1:
            return apology("username already exists")

        # query databasse for email
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))

        # ensure email doesn't already exist
        if len(rows) == 1:
            return apology("There is already an account with this email")

        # ensure password is the same as passwordcheck
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords are not matching")

        # encrypt password
        myctx = CryptContext(schemes=["sha256_crypt"],
                             sha256_crypt__default_rounds=80000)
        hash = pwd_context.hash(request.form.get("password"))

        # insert user into users
        db.execute("INSERT INTO users (username, email, hash) VALUES(:username, :email, :hash)",
                    username=request.form.get("username"), email=request.form.get("email"), hash=hash)
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/balanced")
def balanced():
    uris = db.execute("SELECT uri FROM dietLabels WHERE dietLabel = :dietLabel", dietLabel="Balanced")
    verzameling = []
    for uri in uris:
        info = db.execute("SELECT image, label FROM cachen WHERE uri = :uri", uri=uri['uri'])
        # als er geen image of label aanwezig is
        if len(info) > 0:
            verzameling.append(info[0])

    return render_template("balanced.html", verzameling=verzameling)

@app.route("/lowCarb")
def lowCarb():
    return apology("TODO")

@app.route("/lowFat")
def lowFat():
    return apology("TODO")

@app.route("/highProtein")
def highProtein():
    return apology("TODO")

@app.route("/recept")
def recept():
    return render_template("recept.html")
