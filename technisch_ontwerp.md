# Technisch Ontwerp

### Routes

- Login
  - Scherm, GET, POST
- Lopgout
  - Geen eigen scherm, wordt vervolgens doorgestuurd naar homepage, GET
- Register
  - Scherm, GET, POST
- Homepage
  - Scherm met de drie categorieën, GET
- Categorie 1
  - Scherm met recepten en filteroptie, GET
- Categorie 2
  - Scherm met recepten en filteroptie, GET
- Categorie 3
  - Scherm met recepten en filteroptie, GET
- Filter
  - Geen eigen scherm, op scherm van de betreffende categorie, GET, POST
- PersoonlijkProfiel
  -  Scherm met gegevens en favoriete recepten en mogelijkheid om deze te bewerken, GET, POST
- Profiel
  - Scherm met favoriete recepten van de gebruiker die is aangeklikt, GET, POST
- Favoriet
  - Geen eigen scherm, voegt een recept toe aan favoriete recepten op persoonlijk profiel, blijf op pagina
- Gebruikers
  - Scherm met alle gebruikers die betreffend recept hebben geliked, GET, POST

### Views

[Schetsen](https://docs.google.com/presentation/d/1vd6hnFBhVhjwufJE3FLvwI_Mhs6Ra2_f7SeBGiFoqi8/edit?usp=sharing)


### Helpers
- apology()
  - Foutmelding
- lookup()
  - Return de tags van een recept
- login_required()
  - Redirect gebruiker naar login scherm.


### Plugins
- [Bootsrtap](https://getbootstrap.com/)


