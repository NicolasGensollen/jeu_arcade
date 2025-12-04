from pathlib import Path
import pygame
import sys
from enum import Enum

NOM_DU_JEU = "The Arcade Game"
ECRAN_LARGEUR, ECRAN_HAUTEUR = 800, 600
TAILLE_TUILE = 40
FPS = 60

# Chemins
DOSSIER_NIVEAUX = Path("niveaux_monstres_mobiles")
DOSSIER_ASSETS = Path("assets")

# Fichiers Images
IMG_JOUEUR = "joueur.png"
IMG_BLOC = "bloc.png"
IMG_SORTIE = "sortie.png"
IMG_FOND = "fond.jpg"
IMG_MONSTRE = "monstre.png"
IMG_MONSTRE_MOBILE = "monstre_mobiles.png"

class ElementDecor(Enum):
    MUR = "#"
    JOUEUR = "P"
    SORTIE = "E"
    VIDE = "."
    MONSTRE = "M"
    MONSTRE_MOBILE = "X"

Couleur = tuple[int, int, int]
GRIS: Couleur = (100, 100, 100)
VERT: Couleur = (0, 200, 0)
ROUGE: Couleur = (255, 0, 0)
NOIR: Couleur = (0, 0, 0)
VIOLET: Couleur = (148, 0, 211)
ORANGE: Couleur = (255, 140, 0)

COULEURS = {
    ElementDecor.MUR: GRIS,
    ElementDecor.SORTIE: VERT,
    ElementDecor.JOUEUR: ROUGE,
    ElementDecor.VIDE: NOIR,
    ElementDecor.MONSTRE: VIOLET,
    ElementDecor.MONSTRE_MOBILE: ORANGE,
}

COULEUR_TEXTE = NOIR
COULEUR_HUD_BG = (0, 0, 0, 150) # Fond semi-transparent pour le texte

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
    'mort': False
}

GRAVITE = 1
VITESSE_SAUT = 15
VITESSE_MAX_X = 5
VITESSE_MAX_Y = 15
VITESSE_MONSTRE = 2

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
    images[ElementDecor.MONSTRE_MOBILE] = charger_image(
        IMG_MONSTRE_MOBILE, TAILLE_TUILE, TAILLE_TUILE,
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


def gerer_physique_monstres(niveau: dict):
    monstres_a_supprimer = []
    for monstre in niveau['tuiles_monstres_mobiles']:
        rect = monstre['rect']
        monstre['vitesse_y'] += GRAVITE
        if monstre['vitesse_y'] > VITESSE_MAX_Y:
            monstre['vitesse_y'] = VITESSE_MAX_Y
        rect.x += monstre['vitesse_x']
        if rect.left <= 0:
            monstre['vitesse_x'] = abs(monstre['vitesse_x'])
        elif rect.right >= ECRAN_LARGEUR:
            monstre['vitesse_x'] = -abs(monstre['vitesse_x'])
        for mur in niveau['tuiles_sol']:
            if rect.colliderect(mur):
                if monstre['vitesse_x'] > 0:
                    rect.right = mur.left
                    monstre['vitesse_x'] *= -1
                elif monstre['vitesse_x'] < 0:
                    rect.left = mur.right
                    monstre['vitesse_x'] *= -1
        rect.y += monstre['vitesse_y']
        for mur in niveau['tuiles_sol']:
            if rect.colliderect(mur):
                if monstre['vitesse_y'] > 0:
                    rect.bottom = mur.top
                    monstre['vitesse_y'] = 0
        if rect.top > ECRAN_HAUTEUR:
            monstres_a_supprimer.append(monstre)
    for m in monstres_a_supprimer:
        if m in niveau['tuiles_monstres_mobiles']:
            niveau['tuiles_monstres_mobiles'].remove(m)


def verifier_collisions_danger(niveau: dict):
    """Vérifie si le joueur touche un monstre."""
    for monstre in niveau['tuiles_monstres_fixes']:
        # On réduit légèrement la zone de collision 
        # du monstre pour être "gentil" (hitbox)
        hitbox_monstre = monstre.inflate(-10, -10) 
        if joueur['rect'].colliderect(hitbox_monstre):
            joueur['mort'] = True
    for monstre in niveau['tuiles_monstres_mobiles']:
        hitbox_monstre = monstre["rect"].inflate(-10, -10)
        if joueur['rect'].colliderect(hitbox_monstre):
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
        "tuiles_monstres_fixes": [],
        "tuiles_monstres_mobiles": [],     
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
                    niveau_data["tuiles_monstres_fixes"].append(rect)
                case ElementDecor.MONSTRE_MOBILE:
                    niveau_data["tuiles_monstres_mobiles"].append(
                        {
                            "rect": rect,
                            "vitesse_x": VITESSE_MONSTRE,
                            "vitesse_y": 0,
                        }
                    )
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
    ecran,
    texte,
    sous_texte="",
    couleur=(255, 255, 255),
):
    """Affiche un message à l'écran."""
    font_titre = pygame.font.Font(None, 50)
    font_sous = pygame.font.Font(None, 30)
    surf_titre = font_titre.render(texte, True, couleur)
    rect_titre = surf_titre.get_rect(
        center=(ECRAN_LARGEUR // 2, ECRAN_HAUTEUR // 2 - 20)
    )
    fond = pygame.Surface((ECRAN_LARGEUR, 200))
    fond.set_alpha(200)
    fond.fill((0, 0, 0))
    rect_fond = fond.get_rect(
        center=(ECRAN_LARGEUR // 2, ECRAN_HAUTEUR // 2)
    )
    ecran.blit(fond, rect_fond)
    ecran.blit(surf_titre, rect_titre)
    if sous_texte:
        surf_sous = font_sous.render(sous_texte, True, (200, 200, 200))
        rect_sous = surf_sous.get_rect(
            center=(ECRAN_LARGEUR // 2, ECRAN_HAUTEUR // 2 + 30)
        )
        ecran.blit(surf_sous, rect_sous)
    pygame.display.flip()
    pygame.time.wait(3000)


def afficher_hud(
    ecran: pygame.Rect,
    temps_ecoule,
    niveau: int,
    essais: int,
):
    """Affiche le timer et le niveau en haut de l'écran."""
    font = pygame.font.Font(None, 30)
    texte = f"Niveau: {niveau} | Essai: {essais} | Temps: {temps_ecoule:.1f}s"
    surface = font.render(texte, True, COULEUR_TEXTE)
    rect = surface.get_rect(topleft=(10, 10))
    bg_surface = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
    bg_surface.fill(COULEUR_HUD_BG)
    ecran.blit(bg_surface, (5, 5))
    ecran.blit(surface, rect)


def afficher_ecran_fin(
    ecran: pygame.Rect,
    stats_globales: list,
):
    """Affiche le tableau récapitulatif à la fin du jeu."""
    ecran.fill((20, 20, 40)) # Fond bleu très sombre
    font_titre = pygame.font.Font(None, 60)
    font_texte = pygame.font.Font(None, 36)
    titre = font_titre.render("RÉSULTATS FINAUX", True, (255, 215, 0))
    ecran.blit(titre, (ECRAN_LARGEUR//2 - titre.get_width()//2, 50))
    y = 150
    headers = ["Niveau", "Temps", "Essais"]
    x_positions = [200, 400, 600]
    for i, h in enumerate(headers):
        text = font_texte.render(h, True, (100, 200, 255))
        ecran.blit(text, (x_positions[i] - text.get_width()//2, y))
    pygame.draw.line(ecran, (255, 255, 255), (100, y + 30), (700, y + 30), 2)
    y += 50
    total_temps = 0
    total_essais = 0
    for stat in stats_globales:
        t_str = f"{stat['temps']:.1f}s"
        e_str = str(stat['essais'])
        total_temps += stat['temps']
        total_essais += stat['essais']
        l1 = font_texte.render(str(stat['niveau']), True, (255, 255, 255))
        l2 = font_texte.render(t_str, True, (255, 255, 255))
        l3 = font_texte.render(e_str, True, (255, 255, 255))
        ecran.blit(l1, (x_positions[0] - l1.get_width()//2, y))
        ecran.blit(l2, (x_positions[1] - l2.get_width()//2, y))
        ecran.blit(l3, (x_positions[2] - l3.get_width()//2, y))
        y += 40
    pygame.draw.line(ecran, (255, 255, 255), (100, y + 10), (700, y + 10), 2)
    y += 30
    somme_t = font_texte.render(f"TOTAL: {total_temps:.1f}s", True, (0, 255, 0))
    somme_e = font_texte.render(f"TOTAL: {total_essais} essais", True, (0, 255, 0))
    ecran.blit(somme_t, (x_positions[1] - somme_t.get_width()//2, y))
    ecran.blit(somme_e, (x_positions[2] - somme_e.get_width()//2, y))
    # Instructions Quitter
    y += 80
    quit_msg = font_texte.render("Appuyez sur ÉCHAP pour quitter", True, (150, 150, 150))
    ecran.blit(quit_msg, (ECRAN_LARGEUR//2 - quit_msg.get_width()//2, y))
    pygame.display.flip()
    # Boucle d'attente fin
    attente = True
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                attente = False
                pygame.quit()
                sys.exit()


def main():
    pygame.init()
    ecran = pygame.display.set_mode((ECRAN_LARGEUR, ECRAN_HAUTEUR))
    pygame.display.set_caption("Jeu Plateforme - Stats & Timer")
    clock = pygame.time.Clock()
    images = initialiser_images()
    niveau_actuel = 1
    niveau_data = None
    jeu_en_cours = True
    
    # Variables de statistiques
    stats_globales = []
    temps_debut_niveau = 0
    essais_niveau = 1
    niveau_precedent = 0 # Pour détecter si c'est un nouveau niveau ou un retry

    while jeu_en_cours:
        # 1. LOAD / RESTART
        if niveau_data is None:
            try:
                niveau_data = construire_niveau(charger_niveau(niveau_actuel))
                initialiser_joueur(
                    niveau_data['pos_joueur'][0],
                    niveau_data['pos_joueur'][1],
                )
                print(f"Niveau {niveau_actuel} chargé avec succès.")
                # Gestion du Timer et des Essais
                if niveau_actuel != niveau_precedent:
                    # C'est un tout nouveau niveau
                    temps_debut_niveau = pygame.time.get_ticks()
                    essais_niveau = 1
                    niveau_precedent = niveau_actuel
                else:
                    # C'est un ré-essai
                    essais_niveau += 1    
                afficher_message(
                    ecran, f"Début niveau {niveau_actuel} (Essai {essais_niveau})"
                )            
            except NiveauErreur as e:
                # FIN DU JEU (Plus de niveaux)
                if niveau_actuel > 1:
                    afficher_ecran_fin(ecran, stats_globales)
                else:
                    print(f"Erreur critique: {e}")
                jeu_en_cours = False
                continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT: jeu_en_cours = False
        touches = pygame.key.get_pressed()
        gerer_physique_monstres(niveau_data)
        appliquer_physique(niveau_data, touches)
        
        temps_actuel = (pygame.time.get_ticks() - temps_debut_niveau) / 1000.0

        if joueur['mort'] or joueur['rect'].top > ECRAN_HAUTEUR:
            msg = "Touché !" if joueur['mort'] else "Chute !"
            afficher_message(ecran, "ÉCHEC", f"{msg} Essai {essais_niveau} raté.", (255, 50, 50))
            niveau_data = None # Force reload (même niveau)
            continue

        if (
            niveau_data['tuile_sortie'] and
            joueur['rect'].colliderect(niveau_data['tuile_sortie'])
        ):
            # Enregistrement des stats
            temps_final = temps_actuel
            stats_globales.append({
                'niveau': niveau_actuel,
                'temps': temps_final,
                'essais': essais_niveau
            })
            afficher_message(
                ecran, 
                "NIVEAU TERMINÉ !", 
                f"Temps: {temps_final:.1f}s | Essais: {essais_niveau}", 
                (50, 255, 50)
            )
            niveau_actuel += 1
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
 
        for monstre in niveau_data['tuiles_monstres_fixes']:
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

        for m in niveau_data['tuiles_monstres_mobiles']:
            img = images.get(
                ElementDecor.MONSTRE_MOBILE,
                images.get(ElementDecor.MONSTRE)
            )
            if img:
                if m['vitesse_x'] > 0:
                    img_flip = pygame.transform.flip(img, True, False)
                else:
                    img_flip = img
                ecran.blit(img_flip, m['rect'])
            else: pygame.draw.rect(
                ecran, COULEURS[ElementDecor.MONSTRE_MOBILE], m['rect']
            )
        afficher_hud(ecran, temps_actuel, niveau_actuel, essais_niveau)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()