from pathlib import Path
import pygame
import sys
from enum import Enum

NOM_DU_JEU = "The Arcade Game"
ECRAN_LARGEUR, ECRAN_HAUTEUR = 800, 600
TAILLE_TUILE = 40
FPS = 60
DOSSIER_NIVEAUX = Path("niveaux")

class ElementDecor(Enum):
    MUR = "#"
    JOUEUR = "P"
    SORTIE = "E"
    VIDE = "."

Couleur = tuple[int, int, int]
GRIS: Couleur = (100, 100, 100)
VERT: Couleur = (0, 200, 0)
ROUGE: Couleur = (255, 0, 0)
NOIR: Couleur = (0, 0, 0)
COULEURS = {
    ElementDecor.MUR: GRIS,
    ElementDecor.SORTIE: VERT,
    ElementDecor.JOUEUR: ROUGE,
    ElementDecor.VIDE: NOIR,
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
        'tuiles_sol': [],     
        'tuile_sortie': None, 
        'pos_joueur': None     
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


def main():
    pygame.init()
    ecran = pygame.display.set_mode((ECRAN_LARGEUR, ECRAN_HAUTEUR))
    pygame.display.set_caption(NOM_DU_JEU)
    clock = pygame.time.Clock()
    
    try:
        niveau = charger_niveau(1)
    except NiveauIntrouvableErreur as e:
        print(f"-> ÉCHEC GÉRÉ : {e}\n")
        return
    try:
        niveau_data = construire_niveau(niveau)
    except (
        CaractereInvalideErreur,
        PositionJoueurErreur,
        TuileSortieErreur
    ) as e:
        print(f"Erreur de construction : {e}")
        return

    rect_joueur = pygame.Rect(
        niveau_data['pos_joueur'][0],
        niveau_data['pos_joueur'][1],
        TAILLE_TUILE,
        TAILLE_TUILE
    )
    
    jeu_en_cours = True
    while jeu_en_cours:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jeu_en_cours = False
        
        ecran.fill(COULEURS[ElementDecor.VIDE]) # Fond noir
        
        for tuile in niveau_data['tuiles_sol']:
            pygame.draw.rect(ecran, COULEURS[ElementDecor.MUR], tuile)    
        if niveau_data['tuile_sortie']:
            pygame.draw.rect(
                ecran,
                COULEURS[ElementDecor.SORTIE],
                niveau_data['tuile_sortie'],
            )
        pygame.draw.rect(ecran, COULEURS[ElementDecor.JOUEUR], rect_joueur)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()