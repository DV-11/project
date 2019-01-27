import csv
import urllib.request

from flask import redirect, render_template, request, session
from functools import wraps
from passlib.apps import custom_app_context as pwd_context
from cs50 import SQL
from passlib.context import CryptContext



def apology(message, code=400):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


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


def lookup(symbol):
    """Look up quote for symbol."""

    # reject symbol if it starts with caret
    if symbol.startswith("^"):
        return None

    # reject symbol if it contains comma
    if "," in symbol:
        return None

    # query Yahoo for quote
    # http://stackoverflow.com/a/21351911
    try:

        # GET CSV
        url = f"http://download.finance.yahoo.com/d/quotes.csv?f=snl1&s={symbol}"
        webpage = urllib.request.urlopen(url)

        # read CSV
        datareader = csv.reader(webpage.read().decode("utf-8").splitlines())

        # parse first row
        row = next(datareader)

        # ensure stock exists
        try:
            price = float(row[2])
        except:
            return None

        # return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
        return {
            "name": row[1],
            "price": price,
            "symbol": row[0].upper()
        }

    except:
        pass

    # query Alpha Vantage for quote instead
    # https://www.alphavantage.co/documentation/
    try:

        # GET CSV
        url = f"https://www.alphavantage.co/query?apikey=NAJXWIA8D6VN6A3K&datatype=csv&function=TIME_SERIES_INTRADAY&interval=1min&symbol={symbol}"
        webpage = urllib.request.urlopen(url)

        # parse CSV
        datareader = csv.reader(webpage.read().decode("utf-8").splitlines())

        # ignore first row
        next(datareader)

        # parse second row
        row = next(datareader)

        # ensure stock exists
        try:
            price = float(row[4])
        except:
            return None

        # return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
        return {
            "name": symbol.upper(),  # for backward compatibility with Yahoo
            "price": price,
            "symbol": symbol.upper()
        }

    except:
        return None


def usd(value):
    """Formats value as USD."""
    return f"${value:,.2f}"

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

def voorvertoning(categorie):
    uris = db.execute("SELECT uri FROM dietLabels WHERE dietLabel = :dietLabel", dietLabel=categorie)
    verzameling = []
    for uri in uris:
        info = db.execute("SELECT id, image, label, popularity FROM cachen WHERE uri = :uri", uri=uri['uri'])
        # als er geen image of label aanwezig is
        if len(info) > 0:
            verzameling.append(info[0])
    return verzameling


def likes(verzameling):
    aantalLikes = dict()
    for element in verzameling[0]:
        print(element)



def fav_recipes(u_id):
    recepten = db.execute("SELECT recipe_id FROM favorites WHERE user_id = :user_id", user_id= u_id)
    verzameling=[]
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
    recepten =[]
    for recept in range(len(receptenDict)):
        recepten.append(receptenDict[recept]['recipe_id'])
    return recepten

def addOrDelete(recepten):
    if len(recepten)>0:
        # if recipe not in favorites, add
        if int(request.form.get("recipeID")) not in recepten:
            db.execute("INSERT INTO favorites (user_id, recipe_id) VALUES(:user_id, :recipe_id)",
                        user_id=session["user_id"], recipe_id=int(request.form.get("recipeID")))
            # update number of likes if recipe added to favorites
            db.execute("UPDATE cachen SET popularity = popularity + :price WHERE id = :id", id=int(request.form.get("recipeID")), price=1)
        else:
            db.execute("DELETE FROM favorites WHERE recipe_id = :recipe_id", recipe_id=int(request.form.get("recipeID")))
            db.execute("UPDATE cachen SET popularity = popularity - :like WHERE id = :id", id=int(request.form.get("recipeID")), like=1)
    # if there are no recipes in favorites, add to favorites
    else:
        db.execute("INSERT INTO favorites (user_id, recipe_id) VALUES(:user_id, :recipe_id)",
                    user_id=session["user_id"], recipe_id=int(request.form.get("recipeID")))
        db.execute("UPDATE cachen SET popularity = popularity + :price WHERE id = :id", id=int(request.form.get("recipeID")), price=1)


def loginCheck():
    # query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

    # ensure username exists and password is correct
    if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
        return apology("invalid username and/or password")
    return rows


def registerCheck():
        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username doesn't already exist
        if len(rows) == 1:
            return apology("username already exists")

        # ensure password is the same as passwordcheck
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords are not matching")


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