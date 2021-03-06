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
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return render_template("login_fail.html")

        else:
            session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return render_template("index.html")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/login_fail", methods=["GET", "POST"])
def login_fail():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return render_template("login_fail.html")

        # stay loged in
        else:
            session["user_id"] = rows[0]["id"]

        # redirect to index
        return render_template("index.html")

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login_fail.html")


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

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        # ensure username doesn't already exist
        if len(rows) == 1:
            return render_template("register_fail.html", error="Username already taken")

        # check that password and confirmation matches
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("register_fail.html", error="Password and confirmation do not match")

        # register the users information
        rows = registerUser()

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        check = len(db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username")))
        return render_template("register.html")


@app.route("/register_fail", methods=["GET", "POST"])
def register_fail():
    """Register user."""
    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        # ensure username doesn't already exist
        if len(rows) == 1:
            return render_template("register_fail.html", error="Username already taken")
        # check that password and confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("register_fail.html", error="Password and confirmation do not match")

        # register the users information
        rows = registerUser()

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        check = len(db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username")))
        return render_template("register.html")


# display balanced recipes
@app.route("/balanced")
def balanced():
    verzameling = voorvertoning("Balanced")
    return render_template("balanced.html", verzameling=verzameling)

# display low carb recipes
@app.route("/lowCarb")
def lowCarb():
    verzameling = voorvertoning("Low-Carb")
    return render_template("lowCarb.html", verzameling=verzameling)

# display low fat recipes
@app.route("/lowFat")
def lowFat():
    verzameling = voorvertoning("Low-Fat")
    return render_template("lowFat.html", verzameling=verzameling)

# display high protein recipes
@app.route("/highProtein")
def highProtein():
    verzameling = voorvertoning("High-Protein")
    return render_template("highProtein.html", verzameling=verzameling)


@app.route("/recept", methods=["GET", "POST"])
def recept():
    if request.method == "GET":
        info = db.execute("SELECT * FROM cachen WHERE id = :id", id=request.args.get('id'))
        ingredienten = db.execute("SELECT * FROM ingredients WHERE uri = :uri", uri=info[0]['uri'])

        if session.get("user_id"):
            # select al recipes the user has in favorites
            recepten = favRecipes()

            # make button red if current recipe is in favorites
            isFavorite = False
            if len(recepten) > 0:
                if int(request.args.get('id')) in recepten:
                    isFavorite = True

            # select all the user-ids, usernames who had the selected recipe in their favorites
            gebruikers = userInfo()

            return render_template("recept.html", info=info[0], ingredienten=ingredienten, isFavorite=isFavorite, gebruikers=gebruikers[:5])
        return render_template("recept.html", info=info[0], ingredienten=ingredienten)

    # if clicked on favorite button
    else:
        # select al recipes the user has in favorites
        recepten = favRecipes()

        # delete if recipe already in favorites, otherwise add to favorites
        addOrDelete(recepten)
        return redirect(url_for("personal_profile"))


@app.route("/personal_profile", methods=["GET", "POST"])
def personal_profile():
    if request.method == "GET":
        # get user information
        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session['user_id'])
        uname = rows[0]['username']

        # get favourite recipes
        count = len(db.execute("SELECT * FROM favorites WHERE user_id = :user_id", user_id=session['user_id']))
        verzameling = fav_recipes(session['user_id'])
        return render_template("personal_profile.html", username=uname, ammount=count, verzameling=verzameling)
    else:
        # select al recipes the user has in favorites
        recepten = favRecipes()

        # delete recipe from favorites
        addOrDelete(recepten)
        return redirect(url_for("personal_profile"))


@app.route("/other_profile")
def other_profile():

    # get user information
    other_id = request.args.get('id')
    rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=other_id)
    uname = rows[0]['username']

    # get personal favourites
    count = len(db.execute("SELECT * FROM favorites WHERE user_id = :user_id", user_id=other_id))
    verzameling = fav_recipes(other_id)
    return render_template("other_profile.html", username=uname, ammount=count, verzameling=verzameling)


@app.route("/settings", methods=["GET", "POST"])
def settings():

    if request.method == "POST":
        # check that passowrd and confirmation match
        if request.form.get("new_password") != request.form.get("confirmation"):
            return render_template("settings_fail.html", error="Passowrd and confirmation do not match")

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=request.form.get("user_id"))

        # check if old password is correct
        if not pwd_context.verify(request.form.get('old_password'), rows[0]['hash']):
            return render_template("settings_fail.html", error="Incorrect old password")

        # encrypt new password
        hash = pwd_context.hash(request.form.get("new_password"))

        # update password
        db.execute("UPDATE users SET hash=:hash", hash=hash)

        return redirect(url_for("personal_profile"))
    else:
        user_id = session['user_id']
        return render_template("settings.html", user_id=user_id)


@app.route("/settings_fail", methods=["GET", "POST"])
def settings_fail():

    if request.method == "POST":

        # check that password and confirmation match
        if request.form.get("new_password") != request.form.get("confirmation"):
            return render_template("settings_fail.html", error="Passowrd and confirmation do not match")

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session['user_id'])

        # check if old password is correct
        if not pwd_context.verify(request.form.get('old_password'), rows[0]['hash']):
            return render_template("settings_fail.html", error="Incorrect old password")

        # encrypt new password
        hash = pwd_context.hash(request.form.get("new_password"))

        # update password
        db.execute("UPDATE users SET hash=:hash", hash=hash)

        return redirect(url_for("personal_profile"))
    else:
        return render_template("settings.html")

