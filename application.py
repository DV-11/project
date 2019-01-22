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
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username and password was submitted
        if not request.form.get("username") or not request.form.get("password"):
            return apology("must provide username/password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username doesn't already exist
        if len(rows) == 1:
            return apology("username already exists")

        # ensure password is the same as passwordcheck
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords are not matching")

        # encrypt password
        myctx = CryptContext(schemes=["sha256_crypt"],
                             sha256_crypt__default_rounds=80000)
        hash = pwd_context.hash(request.form.get("password"))

        # insert user into users
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                    username=request.form.get("username"), hash=hash)
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
    verzameling = voorvertoning("Balanced")
    return render_template("balanced.html", verzameling=verzameling)

@app.route("/lowCarb")
def lowCarb():
    verzameling = voorvertoning("Low-Carb")
    return render_template("lowCarb.html", verzameling=verzameling)

@app.route("/lowFat")
def lowFat():
    verzameling = voorvertoning("Low-Fat")
    return render_template("lowFat.html", verzameling=verzameling)

@app.route("/highProtein")
def highProtein():
    verzameling = voorvertoning("High-Protein")
    return render_template("highProtein.html", verzameling=verzameling)

@app.route("/recept", methods=["GET", "POST"])
def recept():
    if request.method == "GET":
        info = db.execute("SELECT * FROM cachen WHERE id = :id", id=request.args.get('id'))
        ingredienten = db.execute("SELECT * FROM ingredients WHERE uri = :uri", uri=info[0]['uri'])

        if session["user_id"]:
            recepten = db.execute("SELECT recipe_id FROM favorites WHERE user_id = :user_id", user_id=session["user_id"])
            # make button red if in favorite
            if len(recepten)>0:
                if int(request.args.get('id')) in recepten[0].values():
                    isFavorite=True
                else:
                    isFavorite=False

                return render_template("recept.html", info=info[0], ingredienten=ingredienten, isFavorite=isFavorite)
        return render_template("recept.html", info=info[0], ingredienten=ingredienten)

    else:
        recepten = db.execute("SELECT recipe_id FROM favorites WHERE user_id = :user_id", user_id=session["user_id"])
        # delete if recipe already in favorites
        if int(request.form.get('id')) not in recepten[0].values():
            db.execute("INSERT INTO favorites (user_id, recipe_id) VALUES(:user_id, :recipe_id)",
                        user_id=session["user_id"], recipe_id=int(request.form.get("recipeID")))
        else:
            db.execute("DELETE FROM favorites WHERE recipe_id = :recipe_id", recipe_id=int(request.form.get("recipeID")))
        return redirect(url_for("index"))

@app.route("/personal_profile")
def personal_profile():
    rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session['user_id'])
    uname = rows[0]['username']
    return render_template("personal_profile.html", username = uname)

@app.route("/settings", methods=["GET", "POST"])
def settings():

    if request.method == "POST":

        if not request.form.get("old_password") or not request.form.get("new_password") or not request.form.get("confirmation"):
            return apology("must fill in all fields")

        if request.form.get("new_password") != request.form.get("confirmation"):
            return apology("confirmation does not match")

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session['user_id'])

        if not pwd_context.verify(request.form.get('old_password'), rows[0]['hash']):
            return apology("incorrect old password")

        hash = pwd_context.hash(request.form.get("new_password"))

        db.execute("UPDATE users SET hash=:hash", hash=hash)

        return render_template("personal_profile.html")

    else:
        return render_template("settings.html")

