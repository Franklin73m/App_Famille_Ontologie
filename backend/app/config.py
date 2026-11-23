"""Configuration du backend : chemins et paramètres."""
from pathlib import Path

# backend/app/config.py -> racine du projet = 2 niveaux au-dessus de backend/
RACINE_PROJET = Path(__file__).resolve().parents[2]

# Ontologie utilisée par l'application (générée par tools/construire_ontologie.py)
CHEMIN_ONTOLOGIE = RACINE_PROJET / "ontology" / "famille.owl"

# Les ajouts faits depuis l'application restent séparés de l'ontologie d'exemple générée.
CHEMIN_AJOUTS_ONTOLOGIE = RACINE_PROJET / "ontology" / "famille_ajouts.owl"

# Le frontend Angular (en développement) peut appeler l'API depuis localhost / 127.0.0.1, sur n'importe quel port
ORIGINES_AUTORISEES_REGEX = r"^http://(localhost|127\.0\.0\.1)(:\d+)?$"
