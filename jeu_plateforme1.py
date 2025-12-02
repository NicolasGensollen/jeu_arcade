from pathlib import Path

DOSSIER_NIVEAUX = Path("niveaux")

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
    
if __name__ == "__main__":
    niveau1 = charger_niveau(1)
    niveau2 = charger_niveau(2)