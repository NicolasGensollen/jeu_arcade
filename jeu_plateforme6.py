from pathlib import Path
import pygame
import sys
from enum import Enum

NOM_DU_JEU = "The Arcade Game"
ECRAN_LARGEUR, ECRAN_HAUTEUR = 800, 600
TAILLE_TUILE = 40
FPS = 60

DOSSIER_NIVEAUX = Path("niveaux_monstres")
DOSSIER_ASSETS = Path("assets")

# Fichiers Images
IMG_JOUEUR = "joueur.png"
IMG_BLOC = "bloc.png"
IMG_SORTIE = "sortie.png"
IMG_FOND = "fond.jpg"
IMG_MONSTRE = "monstre.png"

# Ajout du 'M' pour Monstre
class ElementDecor(Enum):
    MUR = "#"
    JOUEUR = "P"
    SORTIE = "E"
    VIDE = "."
    MONSTRE = "M"

Couleur = tuple[int, int, int]
GRIS: Couleur = (100, 100, 100)
VERT: Couleur = (0, 200, 0)
ROUGE: Couleur = (255, 0, 0)
NOIR: Couleur = (0, 0, 0)
VIOLET: Couleur = (148, 0, 211)
COULEURS = {
    ElementDecor.MUR: GRIS,
    ElementDecor.SORTIE: VERT,
    ElementDecor.JOUEUR: ROUGE,
    ElementDecor.VIDE: NOIR,
    ElementDecor.MONSTRE: VIOLET,
}


class NiveauErreur(Exception):
    """Classe mère pour toutes les erreurs liées aux niveaux."""
    pass

class NiveauIntrouvableErreur(NiveauErreur):
    """Levée quand le fichier n'existe pas."""
    def __init__(self, chemin: str | Path):
        super().__init__(
            f"ERREUR FATALE : Le fichier '{chemin}' est introuvable."
        )

class CaractereInvalideErreur(NiveauErreur):
    """Levée quand un caractère inconnu est lu."""
    def __init__(self, caractere: str, ligne: int, colonne: int):
        super().__init__(
            f"ERREUR DE SYNTAXE : Caractère interdit '{caractere}' "
            f"trouvé à la ligne {ligne+1}, colonne {colonne+1}."
        )

class PositionJoueurErreur(NiveauErreur):
    """Levée quand le nombre de joueurs 'P' est incorrect."""
    def __init__(self, compte: int):
        super().__init__(
            f"ERREUR DE LOGIQUE : Le niveau contient {compte} "
            f"départ(s) de joueur (1 seul requis)."
        )

class TuileSortieErreur(NiveauErreur):
    """Levée quand le nombre de tuiles de sortie est incorrect."""
    def __init__(self, compte: int):
        super().__init__(
            f"ERREUR DE LOGIQUE : Le niveau contient {compte} "
            f"sorties (1 seule requise)."
        )


joueur = {
    'rect': None,
    'vitesse_x': 0,
    'vitesse_y': 0,
    'au_sol': False,
    'direction': 'droite',
    'mort': False,
}

GRAVITE = 1
VITESSE_SAUT = 15
VITESSE_MAX_X = 5
VITESSE_MAX_Y = 15


def charger_image(
    nom_fichier: str,
    largeur: int | None = None,
    hauteur: int | None = None,
    alpha: bool = True,
) -> pygame.Surface:
    """
    Tente de charger une image. Retourne l'image pygame ou None si échec.
    Gère le redimensionnement automatique.
    """
    chemin = DOSSIER_ASSETS / nom_fichier
    try:
        if not chemin.exists():
            print(
                f"AVERTISSEMENT : Image introuvable '{chemin}'. "
                f"Utilisation de la couleur par défaut."
            )
            return None
        img = pygame.image.load(str(chemin))
        # Optimisation de l'image (convert vs convert_alpha)
        img = img.convert_alpha() if alpha else img.convert()
        # Redimensionnement si demandé
        if largeur and hauteur:
            img = pygame.transform.scale(img, (largeur, hauteur))
        return img
    except pygame.error as e:
        print(f"ERREUR PYGAME : Impossible de lire '{chemin}' ({e}).")
        return None

def initialiser_images() -> dict[ElementDecor, pygame.Surface]:
    """Charge toutes les images du jeu dans un dictionnaire."""
    images = {}
    DOSSIER_ASSETS.mkdir(exist_ok=True)
    print("--- CHARGEMENT DES IMAGES ---")
    images[ElementDecor.JOUEUR] = charger_image(
        IMG_JOUEUR, TAILLE_TUILE, TAILLE_TUILE
    )
    images[ElementDecor.MUR] = charger_image(
        IMG_BLOC, TAILLE_TUILE, TAILLE_TUILE
    )
    images[ElementDecor.SORTIE] = charger_image(
        IMG_SORTIE, TAILLE_TUILE, TAILLE_TUILE
    )
    images[ElementDecor.VIDE] = charger_image(
        IMG_FOND, ECRAN_LARGEUR, ECRAN_HAUTEUR, alpha=False
    )
    images[ElementDecor.MONSTRE] = charger_image(
        IMG_MONSTRE, TAILLE_TUILE, TAILLE_TUILE,
    )
    print("-----------------------------")
    return images


def initialiser_joueur(x: int, y: int):
    """Initialise la structure du joueur."""
    joueur['rect'] = pygame.Rect(x, y, TAILLE_TUILE, TAILLE_TUILE)
    joueur['vitesse_x'] = 0
    joueur['vitesse_y'] = 0
    joueur['au_sol'] = False
    joueur["direction"] = "droite"
    joueur["mort"] = False


def mettre_a_jour_vitesses(touches: dict):
    """Met à jour les vitesses du joueur selon les touches pressées."""
    joueur['vitesse_x'] = 0
    if touches[pygame.K_LEFT]:
        joueur['vitesse_x'] = -VITESSE_MAX_X
        joueur["direction"] = "gauche"
    if touches[pygame.K_RIGHT]:
        joueur['vitesse_x'] = VITESSE_MAX_X
        joueur["direction"] = "droite"
    if not joueur['au_sol']:
        joueur['vitesse_y'] += GRAVITE
    if touches[pygame.K_SPACE] and joueur['au_sol']:
        sauter()
    # Limiter la vitesse verticale pour 
    # ne pas traverser les blocs trop vite
    if joueur['vitesse_y'] > VITESSE_MAX_Y:
        joueur['vitesse_y'] = VITESSE_MAX_Y

def sauter():
    """Applique un saut si le joueur est au sol."""
    if joueur['au_sol']:
        joueur['vitesse_y'] = -VITESSE_SAUT
        joueur['au_sol'] = False


def gerer_collisions_horizontales(niveau: dict):
    """Gère les collisions horizontales avec les tuiles solides du niveau."""
    for tuile in niveau['tuiles_sol']:
        if joueur["rect"].colliderect(tuile):
            if joueur["vitesse_x"] > 0: # Collision à droite
                joueur["rect"].right = tuile.left
            elif joueur["vitesse_x"] < 0: # Collision à gauche
                joueur["rect"].left = tuile.right


def gerer_collisions_verticales(niveau: dict):
    """Gère les collisions verticales avec les tuiles solides du niveau."""
    for tuile in niveau['tuiles_sol']:
        if joueur["rect"].colliderect(tuile):
            if joueur["vitesse_y"] > 0: # Collision par le haut (atterrissage)
                joueur["rect"].bottom = tuile.top
                joueur["vitesse_y"] = 0
                joueur["au_sol"] = True
            elif joueur["vitesse_y"] < 0: # Collision par le bas (tête)
                joueur["rect"].top = tuile.bottom
                joueur["vitesse_y"] = 0


def appliquer_physique(niveau: dict, touches: dict):
    """Gère le mouvement et les collisions en séparant les axes."""
    mettre_a_jour_vitesses(touches)
    joueur["rect"].x += joueur["vitesse_x"]
    gerer_collisions_horizontales(niveau)
    joueur["rect"].y += joueur["vitesse_y"]
    joueur["au_sol"] = False # On présume qu'on tombe jusqu'à preuve du contraire
    gerer_collisions_verticales(niveau)
    verifier_collisions_danger(niveau)


def verifier_collisions_danger(niveau: dict):
    """Vérifie si le joueur touche un monstre."""
    for monstre in niveau['tuiles_monstres']:
        # On réduit légèrement la zone de collision 
        # du monstre pour être "gentil" (hitbox)
        hitbox_monstre = monstre.inflate(-10, -10) 
        if joueur['rect'].colliderect(hitbox_monstre):
            print("GAME OVER : Touché par un monstre !")
            joueur['mort'] = True


def creer_tuile(x_grille: int, y_grille: int) -> pygame.Rect:
    """Crée et retourne un objet pygame.Rect pour une tuile."""
    return pygame.Rect(
        x_grille * TAILLE_TUILE,
        y_grille * TAILLE_TUILE,
        TAILLE_TUILE, TAILLE_TUILE
    )


def construire_niveau(donnees_texte: str) -> dict:
    """Transforme les données textuelles du niveau en objets Pygame."""
    lignes = donnees_texte.strip().split('\n')
    niveau_data = {
        "tuiles_sol": [],     
        "tuile_sortie": None, 
        "pos_joueur": None,
        "tuiles_monstres": [],     
    }
    compte_joueur = 0
    compte_sortie = 0
    for y, ligne in enumerate(lignes):
        for x, caractere in enumerate(ligne.strip()):
            rect = creer_tuile(x, y)
            try:
                caractere = ElementDecor(caractere)
            except ValueError:
                raise CaractereInvalideErreur(caractere, y, x)
            match caractere:
                case ElementDecor.MUR:
                    niveau_data['tuiles_sol'].append(rect)
                case ElementDecor.SORTIE:
                    niveau_data['tuile_sortie'] = rect
                    compte_sortie += 1
                case ElementDecor.JOUEUR:
                    niveau_data['pos_joueur'] = (rect.x, rect.y)
                    compte_joueur += 1
                case ElementDecor.MONSTRE:
                    niveau_data["tuiles_monstres"].append(rect)
    if compte_joueur != 1:
        raise PositionJoueurErreur(compte_joueur)
    if compte_sortie != 1:
        raise TuileSortieErreur(compte_sortie)
    return niveau_data


def charger_niveau(numero_niveau: int) -> str:
    """
    Charge le contenu d'un fichier de niveau spécifié.
    Affiche le contenu ou un message d'erreur si le fichier est manquant.
    """
    nom_fichier = f"niveau_{numero_niveau}.txt"
    chemin_fichier = DOSSIER_NIVEAUX / nom_fichier
    try:
        contenu = chemin_fichier.read_text(encoding='utf-8')
    except FileNotFoundError:
        raise NiveauIntrouvableErreur(chemin_fichier)
    return contenu


def afficher_message(
    ecran: pygame.Rect,
    message: str,
    couleur_texte: Couleur = NOIR,
    couleur_fond: Couleur = ROUGE,
) -> None:
    """Affiche un message à l'écran."""
    font = pygame.font.Font(None, 30)
    texte = font.render(message, True, couleur_texte)
    rect = texte.get_rect(center=(ECRAN_LARGEUR // 2, ECRAN_HAUTEUR // 2))
    ecran.fill(couleur_fond)
    ecran.blit(texte, rect)
    pygame.display.flip()
    pygame.time.wait(1000)


def main():
    pygame.init()
    ecran = pygame.display.set_mode((ECRAN_LARGEUR, ECRAN_HAUTEUR))
    pygame.display.set_caption(NOM_DU_JEU)
    clock = pygame.time.Clock()
    images = initialiser_images()
    niveau_actuel = 1
    jeu_en_cours = True
    niveau_data = None
    while jeu_en_cours:
        if niveau_data is None:
            print(f"\nTentative de chargement du niveau {niveau_actuel}...")
            try:
                niveau_data = construire_niveau(charger_niveau(niveau_actuel))
                initialiser_joueur(
                    niveau_data['pos_joueur'][0],
                    niveau_data['pos_joueur'][1],
                )
                print(f"Niveau {niveau_actuel} chargé avec succès.")
                afficher_message(
                    ecran, f"NIVEAU {niveau_actuel} !", NOIR, VERT
                )
            except NiveauIntrouvableErreur as e:
                message = (
                    f"FIN DU JEU : Niveau {niveau_actuel} introuvable. "
                    "Tous les niveaux terminés !"
                )
                print(f"FATAL: {message}")
                afficher_message(ecran, message, NOIR, VERT)
                jeu_en_cours = False
                break
            except NiveauErreur as e:
                message = (
                    f"ERREUR de configuration au Niveau {niveau_actuel}: {e}"
                )
                print(f"FATAL: {message}")
                afficher_message(ecran, message)
                jeu_en_cours = False
                break

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jeu_en_cours = False
        touches = pygame.key.get_pressed()
        appliquer_physique(niveau_data, touches)

        # Vérification de la sortie
        if joueur["rect"].colliderect(niveau_data["tuile_sortie"]):
            niveau_actuel += 1
            niveau_data = None
            print(f"Passage au niveau {niveau_actuel}...")
            continue

        # Vérification de la chute
        if joueur["mort"] or joueur["rect"].top > ECRAN_HAUTEUR:
            message = (
                "GAME OVER : Touché par un monstre !"
                if joueur['mort'] else "GAME OVER : Chute !"
            )
            print(message)
            afficher_message(ecran, message)
            niveau_data = None
            continue  

        if images[ElementDecor.VIDE]:
            ecran.blit(images[ElementDecor.VIDE], (0, 0))
        else:
            ecran.fill(COULEURS[ElementDecor.VIDE]) # Fond noir
        
        for tuile in niveau_data['tuiles_sol']:
            if images[ElementDecor.MUR]:
                ecran.blit(images[ElementDecor.MUR], tuile)
            else:
                pygame.draw.rect(ecran, COULEURS[ElementDecor.MUR], tuile)   
 
        for monstre in niveau_data['tuiles_monstres']:
            if images[ElementDecor.MONSTRE]:
                ecran.blit(images[ElementDecor.MONSTRE], monstre)
            else:
                pygame.draw.rect(
                    ecran, COULEURS[ElementDecor.MONSTRE], monstre
                )
        
        if niveau_data['tuile_sortie']:
            if images[ElementDecor.SORTIE]:
                ecran.blit(
                    images[ElementDecor.SORTIE],
                    niveau_data["tuile_sortie"],
                )
            else:
                pygame.draw.rect(
                    ecran,
                    COULEURS[ElementDecor.SORTIE],
                    niveau_data['tuile_sortie'],
                )
        if joueur['rect']:
            if images[ElementDecor.JOUEUR]:
                img_joueur = images[ElementDecor.JOUEUR]
                if joueur["direction"] == "gauche":
                    img_joueur = pygame.transform.flip(
                        images[ElementDecor.JOUEUR], True, False
                    )
                ecran.blit(img_joueur, joueur["rect"])
            else:
                pygame.draw.rect(
                    ecran, COULEURS[ElementDecor.JOUEUR], joueur['rect']
                )
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()