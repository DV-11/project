import requests
	from cs50 import SQL

	# configure CS50 Library to use SQLite database
	db = SQL("sqlite:///finance.db")

	def balancedRecepten():
	    # haal alle balanced recepten op
	    balanced = requests.get("https://api.edamam.com/search?q=&app_id=e4a4f431&app_key=19473fe38dd2a93f7d82dd69663bd844&diet=high-protein&to=1000")
	    content = balanced.json()
	    recepten = content['hits']

	    # benoem alle waardes
	    for i in range(len(recepten)):
	        uri = recepten[i]['recipe']['uri']
	        url = recepten[i]['recipe']['url']
	        label = recepten[i]['recipe']['label']
	        image = recepten[i]['recipe']['image']
	        dietLabels = recepten[i]['recipe']['dietLabels']
	        healthLabels = recepten[i]['recipe']['healthLabels']
	        ingredients = recepten[i]['recipe']['ingredients']
	        cautions = recepten[i]['recipe']['cautions']
	        calories = recepten[i]['recipe']['calories']

	        # ubdate tabel cashen
	        db.execute("INSERT INTO cachen (uri, url, label, image, calories) VALUES(:uri, :url, :label, :image, :calories)",
	                    uri=uri, url=url, label=label, image=image, calories=calories)

	        # benoem de waardes voor ingredients tabel
	        for ingredient in range(len(ingredients)):
	            tekst = ingredients[ingredient]['text']
	            weight = ingredients[ingredient]['weight']

	            # ubdate tabel ingredients
	            db.execute("INSERT INTO ingredients (uri, tekst, weight) VALUES(:uri, :tekst, :weight)",
	                        uri=uri, tekst=tekst, weight=weight)

	        # benoem waardes voor tabel dietLabels
	        for k in range(len(dietLabels)):
	            dietLabel = dietLabels[k]

	            # ubdate tabel dietLabels
	            db.execute("INSERT INTO dietLabels (uri, dietLabel) VALUES(:uri, :dietLabel)", uri=uri, dietLabel=dietLabel)

	        # # benoem waardes voor cautions tabel
	        # for j in range(len(cautions)):
	        #     caution = cautions[j]

	        #     # ubdate tabel cautions
	        #     db.execute("INSERT INTO cautions (uri, caution) VALUES(:uri, :caution", uri=uri, caution=caution)

	        # # benoem waardes voor tabel healthLabels
	        # for l in healthLabels:
	        #     healthLabel = healthLabels[l]

	        #     # ubdate tabel healtLabels
	        #     db.execute("INSERT INTO healthLabels (uri, healthLabel), VALUES(:uri, :healthLabel", uri=uri, dietLabel=dietLabel)

	balancedRecepten()