import csv
import urllib.request

from flask import redirect, render_template, request, session
from functools import wraps
from passlib.apps import custom_app_context as pwd_context
from cs50 import SQL
from passlib.context import CryptContext


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


# bundles indivual recipes by categoty for display
def voorvertoning(categorie):
    verzameling = db.execute(
        "SELECT id, image, label, popularity FROM cachen WHERE uri IN (SELECT uri FROM dietLabels WHERE dietLabel = :dietLabel) ORDER BY popularity DESC",
        dietLabel=categorie)
    return verzameling


# bundles favourite recipes for display
def fav_recipes(u_id):

    # get recipes from favourites
    recepten = db.execute("SELECT recipe_id FROM favorites WHERE user_id = :user_id", user_id=u_id)

    # bundle them
    verzameling = []
    for i in range(len(recepten)):
        rec_id = recepten[i]['recipe_id']
        info = db.execute("SELECT * FROM cachen WHERE id = :id", id=rec_id)
        verzameling.append(info[0])
    return verzameling


def userInfo():
    # select all the user-ids who had this recipe in their favorites
    gebruikersDict = db.execute("SELECT user_id FROM favorites WHERE recipe_id = :recipe_id", recipe_id=request.args.get('id'))
    gebruikersID = []
    for gebruiker in range(len(gebruikersDict)):
        gebruikersID.append(gebruikersDict[gebruiker]['user_id'])

    # make list of dicts with user_id and username
    gebruikers = []
    if len(gebruikersID) > 0:
        for gebruiker in gebruikersID:
            gegevens = db.execute("SELECT id, username FROM users WHERE id = :id", id=gebruiker)
            gebruikers.append(gegevens[0])
    return gebruikers


def favRecipes():
    # select all the recipes that the user has in favorites
    receptenDict = db.execute("SELECT recipe_id FROM favorites WHERE user_id = :user_id", user_id=session["user_id"])
    recepten = []
    for recept in range(len(receptenDict)):
        recepten.append(receptenDict[recept]['recipe_id'])
    return recepten


def addOrDelete(recepten):
    if len(recepten) > 0:
        # if recipe not in favorites, add
        if int(request.form.get("recipeID")) not in recepten:
            db.execute("INSERT INTO favorites (user_id, recipe_id) VALUES(:user_id, :recipe_id)",
                       user_id=session["user_id"], recipe_id=int(request.form.get("recipeID")))
            # update number of likes if recipe added to favorites
            db.execute("UPDATE cachen SET popularity = popularity + :price WHERE id = :id",
                       id=int(request.form.get("recipeID")), price=1)
        else:
            # remove like if recipe removed from favorites
            db.execute("DELETE FROM favorites WHERE recipe_id = :recipe_id", recipe_id=int(request.form.get("recipeID")))
            db.execute("UPDATE cachen SET popularity = popularity - :like WHERE id = :id",
                       id=int(request.form.get("recipeID")), like=1)
    # if there are no recipes in favorites, add to favorites
    else:
        db.execute("INSERT INTO favorites (user_id, recipe_id) VALUES(:user_id, :recipe_id)",
                   user_id=session["user_id"], recipe_id=int(request.form.get("recipeID")))
        db.execute("UPDATE cachen SET popularity = popularity + :price WHERE id = :id",
                   id=int(request.form.get("recipeID")), price=1)


def registerUser():
    # encrypt password
    myctx = CryptContext(schemes=["sha256_crypt"],
                         sha256_crypt__default_rounds=80000)
    hash = pwd_context.hash(request.form.get("password"))

    # insert user into users
    db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
               username=request.form.get("username"), hash=hash)
    rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
    return rows