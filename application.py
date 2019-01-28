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
        # check if username and password are matching
        rows = loginCheck()

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
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
        # check if username is availible and passwords are matching
        registerCheck()

        # register the users information
        rows = registerUser()

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
    # likes(verzameling)
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
    # if returned recipe id is empty after POST, use returned id
    # if request.args.get('id') is None:
    #     recipe_id = recipeID
    # else:
    #     recipe_id = request.args.get('id')

    if request.method == "GET":
        info = db.execute("SELECT * FROM cachen WHERE id = :id", id=request.args.get('id'))
        ingredienten = db.execute("SELECT * FROM ingredients WHERE uri = :uri", uri=info[0]['uri'])

        if session.get("user_id"):
            # select al recipes the user has in favorites
            recepten = favRecipes()

            # make button red if current recipe is in favorites
            isFavorite=False
            if len(recepten)>0:
                if int(request.args.get('id')) in recepten:
                    isFavorite=True

            # select all the user-ids, usernames who had the selected recipe in their favorites
            gebruikers = userInfo()

            # amount of users who added recipe to favorites
            amount = len(gebruikers)

            return render_template("recept.html", info=info[0], ingredienten=ingredienten, isFavorite=isFavorite, gebruikers=gebruikers[:5], amount=amount)
        return render_template("recept.html", info=info[0], ingredienten=ingredienten)

    # if clicked on favorite button
    else:
        # select al recipes the user has in favorites
        recepten = favRecipes()

        # delete if recipe already in favorites, otherwise add to favorites
        addOrDelete(recepten)
        return redirect(url_for("index"))


@app.route("/personal_profile")
def personal_profile():
    rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session['user_id'])
    uname = rows[0]['username']
    count = len(db.execute("SELECT * FROM favorites WHERE user_id = :user_id", user_id=session['user_id']))
    verzameling = fav_recipes(session['user_id'])
    return render_template("personal_profile.html", username = uname, ammount = count, verzameling = verzameling)


@app.route("/other_profile", methods=["GET","POST"])
def other_profile():
    other_id = request.args.get('id')
    rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=other_id)
    uname = rows[0]['username']
    count = len(db.execute("SELECT * FROM favorites WHERE user_id = :user_id", user_id=other_id))
    verzameling = fav_recipes(other_id)
    return render_template("other_profile.html", username = uname, ammount = count, verzameling = verzameling)


@app.route("/settings", methods=["GET", "POST"])
def settings():

    if request.method == "POST":

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


