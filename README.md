# TP Jeu Arcade

### Objectifs

- Utiliser la gestion de fichiers avec `pathlib`.
- Implémenter une gestion des erreurs robuste, notamment pour le chargement des données.
- Développer les mécaniques d'un jeu de plateforme basique (gravité, collisions, déplacement) avec Pygame.

### Introduction

Dans ce TP nous allons réaliser un jeu de type "arcade" où le joueur déplace un personnage dans différents niveaux. A chaque niveau, le but est d'atteindre la sortie sans tomber en se déplaçant sur des plateformes.

On concevra les cartes des niveaux dans des fichiers textes qui seront stockés dans un dossier spécifique. Chaque fois que le joueur passe au niveau suivant, le programme va chercher la carte correspondante et l'affiche à l'écran. Pour gagner le jeu, il faut finir tout les niveaux.
### Les cartes de niveaux

Chaque niveau sera un fichier texte simple où chaque ligne représente une rangée de la grille du niveau.

| Caractère | Signification                                         |
| --------- | ----------------------------------------------------- |
| **#**     | Bloc Sol/Plateforme (où le joueur peut marcher)       |
| **P**     | Position de départ du Joueur (doit être unique)       |
| **E**     | Zone d' entrée/sortie (pour passer au niveau suivant) |
| **.**     | Espace Vide (où le joueur tombe)                      |

Voici la carte du 1er niveau de notre jeu:

```
....................
....................
.............#......
.......#....#..#....
P..................E
###..###############

```

Et voici la carte du 2nd niveau:

```
....................
....................
....................
P#...............#E.
##..###.###.########

```

N'hésitez pas à prendre quelques minutes pour concevoir quelques cartes supplémentaires pour d'éventuels niveaux suivants.

---
### Partie 1 : Mise en Place et Gestion des Fichiers de Niveaux

L'objectif initial est de s'assurer que le programme peut localiser et lire correctement les fichiers de niveau en utilisant le module `pathlib` que nous avons vu en cours.

Créez une structure de dossiers comme suit : 
```
/
├── jeu_plateforme.py (Le code principal du jeu)
└── niveaux/
    ├── niveau_1.txt
    ├── niveau_2.txt
    └── ...
```

Copier collez les niveaux 1 et 2 de notre jeu dans les fichiers correspondants.

Dans votre code Python,  déclarez une variable `DOSSIER_NIVEAUX` pointant vers le répertoire `niveaux` en utilisant `pathlib`.

Écrivez une fonction 
```python
def charger_niveau(numero_niveau: int) -> str | None:
    ...
```
qui prend un numéro de niveau en paramètre et qui affiche le contenu de la carte du niveau correspondant. La fonction retourne aussi ce contenu.
On utilisera la méthode `read_text()` du chemin pour lire l'intégralité du contenu du fichier dans une chaîne de caractères.

Pensez à gérer les erreurs potentielles:
- Le fichier de niveau n'existe pas
- La lecture du fichier échoue pour une raison quelconque
Pour le moment, on se contentera d'afficher le message d'erreur avec un `print()`.

---
### Partie 2 : Affichage d'un niveau

Il s'agit maintenant d'intégrer Pygame et de transformer les données textuelles du niveau en objets (des "tuiles") exploitables par le moteur de jeu.

Dans une fonction `main()`, initialisez `Pygame`, créez la fenêtre (800x600) et la boucle de jeu de base qui doit gérer l'événement `QUIT` et remplir l'écran de la couleur du fond (Noir par exemple).

Définissez la taille des tuiles (ex : `TAILLE_TUILE = 40`).

Créez une fonction 
```python
def creer_tuile(x_grille: int, y_grille: int) -> pygame.Rect:
    ...
```
qui prend un des coordonnées de grille `(x,y)` et retourne un objet représentant la tuile correspondante (un rectangle Pygame `pygame.Rect`).

Écrivez une fonction 
```python
def construire_niveau(donnees_texte: str) -> dict:
    ...
```
qui prend la chaîne de caractères lue à partir du fichier de niveau et qui retourne un dictionnaire de ce type:
```python
niveau_data = {
	"tuiles_sol": [],     # Contient les tuiles du sol
	"tuile_sortie": None, # Contient la tuile de sortie
	"pos_joueur": None,   # Contient un tuple (x, y) pour la pos du joueur   
}
```
Cette fonction doit parcourir ligne par ligne et caractère par caractère ces données.
Pour chaque caractère, appelez `creer_tuile(...)` pour construire la liste de tous les blocs du niveau et stockez les tuiles dans le dictionnaire `niveau_data`.

Si la position initiale du joueur est manquante, on lèvera une `ValueError`.

Dans la fonction `main()`, chargez le niveau 1 en texte (`charger_niveau()`), puis en tuiles (`construire_niveau()`). Gérez les cas où ces fonctions retournent `None` ou lèvent une erreur.

Dans la boucle de jeu, construire un `pygame.Rect` pour le joueur, et affichez les blocs du niveau (par exemple, les blocs `'#'` en gris, le joueur `'P'` en rouge, et la sortie en vert). 

---
### Partie 3 : Gestion des Erreurs et Robustesse

Cette partie est cruciale pour valider les objectifs sur la gestion des erreurs et des exceptions.
#### Gestion des niveaux manquants

Créez une exception personnalisée de type `NiveauErreur` pour gérer toutes les erreurs liées aux niveaux.

Créez une seconde exception personnalisée de type `NiveauIntrouvableErreur` qui hérite de `NiveauErreur` et qu'on utilisera lorsque le fichier de niveau demandé n'existe pas. 

Modifier la fonction `__init__` pour afficher un message d'erreur personnalisé (par exemple "ERREUR FATALE : Le fichier XXX est introuvable.").

Modifiez ensuite la fonction `charger_niveau()` pour lever cette erreur si une exception `FileNotFoundError` est levée lors de la lecture du fichier. La fonction `charger_niveau()` ne renvoie donc plus `None` mais lève une erreur dans ce cas.

Capturez ensuite cette exception dans la fonction `main()` pour terminer le jeu proprement.

#### Gestion des caractères non valides dans les cartes de niveaux

Créez une nouvelle variable `CARACTERES_VALIDES` qui contient les caractères autorisés dans les cartes de niveaux.

Créez une nouvelle exception personnalisée de type `CaractereInvalideErreur` qui hérite de `NiveauErreur` et qui affiche un message personnalisé lorsqu'un caractère non valide est rencontré dans une carte de niveau (par exemple "ERREUR DE SYNTAXE : Caractère interdit '{caractere}' trouvé à la ligne {ligne+1}, colonne {colonne+1}.")

Dans la fonction `construire_niveau`, lorsque vous parcourez les caractères, utilisez un bloc `try...except` autour du traitement de chaque caractère. Si le caractère lu n'est pas un des caractères valides, levez une exception personnalisée de type `CaractereInvalideErreur`.

Si cette exception est levée, le programme doit afficher un message d'erreur précis (ex : "Erreur dans niveau_1.txt : caractère 'Z' non reconnu à la ligne 5, colonne 12.") puis interrompre le chargement du niveau et arrêter le jeu.

#### Gestion du cas où il n'y a pas exactement un joueur

Créez une nouvelle exception personnalisée de type `PositionJoueurErreur` qui hérite de `NiveauErreur` et qui affiche un message personnalisé lorsqu'il n'y a aucun ou plusieurs caractères "Joueur" dans une carte de niveaux (par exemple: "ERREUR DE LOGIQUE : Le niveau contient {compte} départ(s) de joueur (1 seul requis).").

Modifiez la fonction `construire_niveau` pour vérifier qu'il y a exactement un caractère `'P'`. S'il n'y en a aucun ou s'il y en a plus d'un, levez une exception personnalisée ``PositionJoueurErreur``.

Capturez cette exception et affichez un message d'erreur clair.

#### Gestion du cas où il n'y a pas exactement une sortie

Faites la même chose que pour le joueur, mais en implémentant une nouvelle exception personnalisée de type `TuileSortieErreur`.

---

### Partie 4 : Mécaniques de Jeu et Transition de Niveaux

#### Modéliser le Joueur (Vitesse et État)

Pour l'instant, nous avons seulement la position de départ du joueur. Pour qu'il bouge, nous devons gérer sa vitesse.

Créez un dictionnaire (variable globale) `joueur` contenant :
- `rect`: Le `pygame.Rect` du joueur.
- `vitesse_x`: La vitesse horizontale actuelle (initialisée à 0).
- `vitesse_y`: La vitesse verticale actuelle (initialisée à 0).
- `au_sol`: Un booléen (`True`/`False`) pour savoir si le joueur peut sauter.

Ecrire une fonction
```python
def initialiser_joueur(x: int, y: int):
    ...
```
qui utilise ce dictionnaire global et initialise les valeurs (on commence sans vitesse et au sol).

Ecrire ensuite une fonction
```python
def sauter():
    ...
```
qui utilise ce dictionnaire global. Si le joueur est au sol, on modifie sa `vitesse_y` à une constante appelée `VITESSE_SAUT` et on modifie le booléen `au_sol`.

On a maintenant besoin de gérer les déplacements de notre joueur.
Définissez les constantes `VITESSE_MAX_X` et `VITESSE_MAX_Y` qui devront limiter la vitesse possible du joueur dans ces directions.

Ecrire ensuite une fonction
```python
def mettre_a_jour_vitesses(touches: dict):
	...
```
qui doit mettre à jour les vitesses du dictionnaire global `joueur` en fonction des touches pressées:
- `K_LEFT`: pour aller à gauche
- `K_RIGHT`: pour aller à droite
- `K_SPACE`: pour sauter

Si le joueur n'est pas au sol, il faut augmenter sa vitesse verticale d'une constante `GRAVITE`.
Limitez les vitesses maximales avec  `VITESSE_MAX_X` et `VITESSE_MAX_Y`.
#### Gérer les collisions

Ecrire une fonction
```python
def gerer_collisions_horizontales(niveau: dict):
    ...
```
qui doit s'occuper de gérer les collisions sur l'axe des X uniquement.
Il faut parcourir les tuiles du sol et vérifier si le rectangle du joueur est en intersection avec la tuile en question (vous pouvez utiliser [colliderec()](https://www.pygame.org/docs/ref/rect.html#pygame.Rect.colliderect) et les attributs `top`, `left`, `bottom` et `right`).
Il faudra distinguer le cas où le joueur entre en collision par la droite (`vitesse_x > 0`) du cas où il entre en collision par la gauche (`vitesse_x < 0`).

Ecrire maintenant une fonction
```python
def gerer_collisions_verticales(niveau: dict):
    ...
```
qui doit s'occuper de gérer les collisions sur l'axe des Y uniquement. La logique est similaire à celle de `gerer_collisions_horizontales()` sauf qu'il faut gérer le booléen `au_sol` en plus.

Passons maintenant à la fonction clé qui gère le mouvement du joueur:
```python
def appliquer_physique(niveau: dict, touches: dict):
    ...
```
Cette fonction doit:
- mettre à jour les vitesses
- mettre à jour la position suivant l'axe des X
- vérifier les collisions horizontales
- mettre à jour la position suivant l'axe des Y
- vérifier les collisions verticales

Vous pouvez ensuite appeler cette fonction dans la boucle de jeu principale. Votre joueur devrait normalement être contrôlable et tomber dans les trous.

#### Gérer les fins de niveaux

Il nous reste deux événements à prendre en compte:
- La détection de sortie de niveau (victoire du niveau)
- La détection de chute (Game Over)

Il nous faut d'abord réorganiser un peu notre fonction `main()`. Avant la boucle infinie, initialisez `niveau_data` à `None` et `niveau_actuel` à 1:
```python
jeu_en_cours = True
niveau_data = None
niveau_actuel = 1
while jeu_en_cours:
	if niveau_data is None:
		# On va mettre le code de chargement de niveau ici
```
Le code de chargement de niveau doit être constitué des appels aux fonctions `construire_niveau()`, `charger_niveau()`, et `initialiser_joueur()`. Les erreurs que ces fonctions peuvent lever (`NiveauIntrouvableErreur` et `NiveauErreur`) doivent être gérées de façon appropriée (message et fin du jeu).

Regardons maintenant la détection de sortie (après l'appel à `appliquer_physique()` et avant les dessins). Vérifiez si le `rect` du joueur touche le `rect` de la sortie. Si c'est le cas, incrémentez le numéro du niveau, mettez `niveau_data` à `None` et affichez un message de passage de niveau. 

Passons à la détection de chute (après la détection de sortie dans le `main()`). Si le joueur sors de l'écran par le bas, affichez un message et mettez `niveau_data` à `None`.

A ce stade, vous devriez pouvoir jouer au jeu en passant de niveau en niveau ou en recommençant le même niveau si vous perdez.

---

### Partie 5 : Améliorer les graphismes

Pour le moment, tout les éléments sont visuellement assez pauvres... Nous allons utiliser des images pour donner plus fière allure à notre jeu.

Créez un dossier `assets` dans lequel vous placerez les images pour les éléments suivants:
- le joueur (par exemple mario)
- les blocs (par exemple un cube de briques)
- les sorties (par exemple le tunnel vert de mario)
- le fond (un paysage de votre choix)

Utilisez `pathlib` pour pointer vers le dossier des images.

Créez une fonction 
```python
def charger_image(
	nom_fichier: str,
	largeur: int | None = None,
	hauteur: int | None = None,
	alpha: bool = True,
) -> pygame.Surface:
	...
```
qui tente de charger une image et qui retourne l'image `pygame` ou None si un échec a eu lieu.
Cette fonction gère également le redimensionnement automatique si besoin.

Créez ensuite une fonction 
```python
def initialiser_images() -> dict[str, pygame.Surface]:
	...
```
qui doit charger toutes les images du jeu dans un dictionnaire.

On appellera cette fonction dans la fonction `main()`, avant la boucle de jeu.

Dans la boucle de jeu, nous devons mettre à jour l'affichage. On tentera de _blit_ l'image correspondant à l'élément actuel si l'image existe, sinon on utilisera les anciens graphiques par défaut.

**Question bonus :** Faîtes en sorte que le personnage représentant le joueur soit tourné dans la direction de déplacement pour plus de réalisme. (Aide: regardez la fonction [pygame.transform.flip()](https://www.pygame.org/docs/ref/transform.html#pygame.transform.flip))

---
### Aller plus loin

#### Afficher des messages au joueur

On voudrait afficher les messages de la console aussi sur l'écran de jeu, de façon à ce que le joueur sache son niveau par exemple. Implémentez une fonction:
```python
def afficher_message(
	ecran: pygame.Rect,
	message: str,
	couleur_texte: Couleur = NOIR,
	couleur_fond: Couleur = ROUGE,
) -> None:
	...
```
qui affiche le message passé au centre de l'écran. On ajoutera une petite pause grâce à [pygame.time.wait()](https://www.pygame.org/docs/ref/time.html#pygame.time.wait).

#### Calcul des scores et classement des meilleurs joueurs

Ajoutez un calcul des scores du joueur (en fonction du niveau atteint, du nombre d'essais, du temps de jeu...). Une fois la partie finie, enregistrer le score, le pseudo du joueur et la date dans un fichiers `scores.txt`.

A la fin d'une partie, le jeu doit nous afficher le top 10 des meilleurs joueurs de tous les temps ainsi que notre classement pour la partie que nous venons de jouer.


