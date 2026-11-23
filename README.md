# Famille-Ontologie

Application web qui identifie les liens familiaux à partir d'une ontologie OWL (Protégé).

- **Une personne** choisie → toute sa famille, avec le lien de chacun (père, oncle, cousine, demi-frère, belle-mère...).
- **Deux personnes** choisies → le lien qui les unit, dans les deux sens.

| Couche | Technologie | Dossier | État |
|---|---|---|---|
| Ontologie | OWL (Protégé) | `ontology/` | ✅ terminée |
| Backend | Python + FastAPI | `backend/` | ✅ écrit, moteur testé |
| Frontend | Angular 19 | `frontend/` | ✅ écrit, à valider sur PC (voir PROJECT_STATE) |

> **Reprise après une pause** : donner `PROJECT_STATE.md` (et ce README) à Claude.

## Démarrage rapide

Prérequis : Python 3.11 à 3.13 et Node.js LTS. Détails et dépannage dans `docs/guide-installation.md`.

**Terminal 1 : backend**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows   (Mac/Linux : source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload     # http://localhost:8000/docs
```

**Terminal 2 : frontend**
```bash
cd frontend
npm install
npm start                         # http://localhost:4200
```

## Tests

```bash
cd backend  && python -m unittest discover -s tests -v    # moteur + API
cd frontend && npm test                                   # fonctions utilitaires
```

## Documentation

| Fichier | Contenu |
|---|---|
| `PROJECT_STATE.md` | État du projet, décisions, reste à faire |
| `CHANGELOG.md` | Journal des modifications |
| `docs/ontologie.md` | Classes, propriétés, corrections, individus |
| `docs/architecture.md` | Schéma et choix techniques |
| `frontend/README.md` | Structure du frontend Angular |
| `docs/api.md` | Endpoints et exemples |
| `docs/tests.md` | Cas de test |
| `docs/guide-installation.md` | Installation pas à pas |
