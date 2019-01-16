import requests
from cs50 import SQL

# configure CS50 Library to use SQLite database
# db = SQL("sqlite:///finance.db")

def balancedRecepten():
    # haal alle balanced recepten op
    balanced = requests.get("https://api.edamam.com/search?q=&app_id=e4a4f431&app_key=19473fe38dd2a93f7d82dd69663bd844&diet=balanced&to=1000")
    content = balanced.json()
    recepten = content['hits']

    # benoem alle waardes
    for i in range(len(recepten)):
        uri = recepten[i]['recipe']['uri']
        label = recepten[i]['recipe']['label']
        image = recepten[i]['recipe']['image']
        dietLabels = recepten[i]['recipe']['dietLabels']
        healthLabels = recepten[i]['recipe']['healthLabels']
        ingredients = recepten[i]['recipe']['ingredients']
        cautions = recepten[i]['recipe']['cautions']
        calories = recepten[i]['recipe']['calories']
        totalTime = recepten[i]['recipe']['totalTime']

        # ubdate tabel cashen
        db.execute("INSERT INTO cashenBalanced (uri, label, image, dietLabels, healthLabels, cautions, ingredients, calories, totalTime) VALUES(:uri, :label, :image, :dietLabels, :healthLabels, :cautions, :ingredients, :calories, :totalTime)",
                    uri=uri, label=label, image=image, dietLabels=dietLabels, healthLabels=healthLabels, cautions=cautions, ingredients=ingredients, calories=calories, totalTime=totalTime)

        # benoem de waardes voor ingredienten tabel
        for ingredient in range(len(ingredients):
            text = ingredients[ingredient]['text']
            weight = ingredients[ingredient]['weight']

            # ubdate tabel ingredients
            db.execute("INSERT INTO ingredients (uri, text, weight) VALUES(:uri, :text, :weight)",
                        uri=uri, text=text, weight=weight)

        # benoem waardes voor cautions tabel
        for j in range(len(cautions)):
            caution = cautions[j]

            # ubdate tabel cautions
            db.execute("INSERT INTO cautions (uri, caution) VALUES(:uri, :caution", uri=uri, caution=caution)

        # benoem waardes voor tabel dietLabels
        for k in dietLabels:
            dietLabel = dietLabels[k]

            # ubdate tabel dietLabels
            db.execute("INSERT INTO dietLabels (uri, dietLabel) VALUES(:uri, :dietLabel)", uri=uri, dietLabel=dietLabel)

        # benoem waardes voor tabel healthLabels
        for l in healthLabels:
            healthLabel = healthLabels[l]

            # ubdate tabel healtLabels
            db.execute("INSERT INTO healthLabels (uri, healthLabel), VALUES(:uri, :healthLabel", uri=uri, dietLabel=dietLabel)


def proteinRecepten():
    # haal alle high-protein recepten op
    balanced = requests.get("https://api.edamam.com/search?q=&app_id=e4a4f431&app_key=19473fe38dd2a93f7d82dd69663bd844&diet=high-protein&to=1000")
    content = balanced.json()
    recepten = content['hits']

    for i in range(len(recepten)):
        label = recepten[i]['recipe']['label']
        image = recepten[i]['recipe']['image']
        dietLabels = recepten[i]['recipe']['dietLabels']
        healthLabels = recepten[i]['recipe']['healthLabels']
        cautions = recepten[i]['recipe']['cautions']
        ingredients = recepten[i]['recipe']['ingredients']
        calories = recepten[i]['recipe']['calories']
        totalTime = recepten[i]['recipe']['totalTime']


def fatRecepten():
    # haal alle low-fat recepten op
    balanced = requests.get("https://api.edamam.com/search?q=&app_id=e4a4f431&app_key=19473fe38dd2a93f7d82dd69663bd844&diet=low-fat&to=1000")
    content = balanced.json()
    recepten = content['hits']

    for i in range(len(recepten)):
        label = recepten[i]['recipe']['label']
        image = recepten[i]['recipe']['image']
        dietLabels = recepten[i]['recipe']['dietLabels']
        healthLabels = recepten[i]['recipe']['healthLabels']
        cautions = recepten[i]['recipe']['cautions']
        ingredients = recepten[i]['recipe']['ingredients']
        calories = recepten[i]['recipe']['calories']
        totalTime = recepten[i]['recipe']['totalTime']


def carbRecepten():
    # haal alle low-carb recepten op
    balanced = requests.get("https://api.edamam.com/search?q=&app_id=e4a4f431&app_key=19473fe38dd2a93f7d82dd69663bd844&diet=low-carb&to=1000")
    content = balanced.json()
    recepten = content['hits']

    for i in range(len(recepten)):
        label = recepten[i]['recipe']['label']
        image = recepten[i]['recipe']['image']
        dietLabels = recepten[i]['recipe']['dietLabels']
        healthLabels = recepten[i]['recipe']['healthLabels']
        cautions = recepten[i]['recipe']['cautions']
        ingredients = recepten[i]['recipe']['ingredients']
        calories = recepten[i]['recipe']['calories']
        totalTime = recepten[i]['recipe']['totalTime']

balancedRecepten()