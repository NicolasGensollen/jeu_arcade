from pathlib import Path
import pygame
import sys

ECRAN_LARGEUR, ECRAN_HAUTEUR = 800, 600
TAILLE_TUILE = 40
FPS = 60
DOSSIER_NIVEAUX = Path("niveaux")
CARACTERES_VALIDES = set(['#', 'P', 'E', '.'])
COULEURS = {
    '#': (100, 100, 100),  # Gris pour les blocs
    'E': (0, 200, 0),      # Vert pour la sortie
    'P': (255, 0, 0),      # Rouge pour le joueur
    '.': (0, 0, 0)         # Noir pour l'arrière-plan
}

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
    for y, ligne in enumerate(lignes):
        for x, caractere in enumerate(ligne.strip()):
            rect = creer_tuile(x, y) 
            match caractere:
                case "#":
                    niveau_data['tuiles_sol'].append(rect)
                case "E":
                    niveau_data['tuile_sortie'] = rect
                case "P":
                    niveau_data['pos_joueur'] = (rect.x, rect.y)
    if niveau_data['pos_joueur'] is None:
        raise ValueError("Erreur de Parsing: Position joueur 'P' manquante.")

    return niveau_data


def charger_niveau(numero_niveau: int) -> str | None:
    """
    Charge le contenu d'un fichier de niveau spécifié.
    Affiche le contenu ou un message d'erreur si le fichier est manquant.
    """
    nom_fichier = f"niveau_{numero_niveau}.txt"
    chemin_fichier = DOSSIER_NIVEAUX / nom_fichier
    if not chemin_fichier.exists():
        print("ERREUR : Fichier introuvable. Veuillez vérifier le numéro de niveau et le chemin.")
        return None    
    try:
        contenu = chemin_fichier.read_text(encoding='utf-8')
        print("--- Contenu du Fichier ---")
        print(contenu.strip())
        print("--------------------------")
        return contenu
    except Exception as e:
        print(f"ERREUR de lecture : Une erreur inattendue s'est produite : {e}")
        return None


def main():
    pygame.init()
    ecran = pygame.display.set_mode((ECRAN_LARGEUR, ECRAN_HAUTEUR))
    pygame.display.set_caption("Jeu Arcade")
    clock = pygame.time.Clock()
    
    niveau = charger_niveau(1)
    if niveau is None:
        print("Erreur critique: Impossible de charger niveau_1.txt")
        return

    try:
        niveau_data = construire_niveau(niveau)
    except ValueError as e:
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
        
        ecran.fill(COULEURS['.']) # Fond noir
        
        for tuile in niveau_data['tuiles_sol']:
            pygame.draw.rect(ecran, COULEURS['#'], tuile)    
        if niveau_data['tuile_sortie']:
            pygame.draw.rect(ecran, COULEURS['E'], niveau_data['tuile_sortie'])
        pygame.draw.rect(ecran, COULEURS['P'], rect_joueur)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()