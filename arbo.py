import os

# Dossiers à exclure
DOSSIERS_EXCLUS = {
    'venv', 'env', '__pycache__', '.git', '.idea',
    'node_modules', 'migrations', '.vscode', '.pytest_cache',
}

# Extensions de fichiers à exclure
EXTENSIONS_EXCLUES = {'.pyc', '.log', '.tmp'}

# Nom du fichier de sortie
FICHIER_SORTIE = "arborescence.txt"

# Profondeur maximale (None = illimité)
PROFONDEUR_MAX = 3

def est_exclu(nom, chemin):
    if nom.startswith(".") and os.path.isdir(chemin):  # Dossier caché
        return True
    if nom in DOSSIERS_EXCLUS:
        return True
    if os.path.isfile(chemin):
        _, ext = os.path.splitext(nom)
        if ext in EXTENSIONS_EXCLUES:
            return True
    return False

def afficher_arborescence(racine, fichier, niveau=0):
    if PROFONDEUR_MAX is not None and niveau > PROFONDEUR_MAX:
        return

    try:
        elements = sorted(os.listdir(racine))
    except PermissionError:
        return

    for nom in elements:
        chemin = os.path.join(racine, nom)
        if est_exclu(nom, chemin):
            continue
        indent = "│   " * niveau
        if os.path.isdir(chemin):
            fichier.write(f"{indent}├── {nom}/\n")
            afficher_arborescence(chemin, fichier, niveau + 1)
        elif os.path.isfile(chemin):
            fichier.write(f"{indent}├── {nom}\n")

def main():
    dossier_racine = "."  # Répertoire courant
    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        f.write("📁 Arborescence du projet (principale) :\n")
        f.write("├── .\n")
        afficher_arborescence(dossier_racine, f, 1)

    print(f"\n✅ Fichier '{FICHIER_SORTIE}' généré avec succès.")

if __name__ == "__main__":
    main()
