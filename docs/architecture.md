# Architecture

```
┌────────────┐   HTTP/JSON    ┌─────────────────────┐
│  Angular   │ ─────────────► │  FastAPI (Python)   │
│ (frontend) │ ◄───────────── │  /api/...           │
└────────────┘  localhost:4200│  localhost:8000     │
                              └──────────┬──────────┘
                                         │ lit et complète
                              ┌────────────────────────────┐
                              │ ontology/famille.owl       │
                              │ ontology/famille_ajouts.owl│
                              └────────────────────────────┘
```

## Backend (`backend/app/`)

| Fichier | Rôle |
|---|---|
| `main.py` | Crée l'application, active le CORS, branche les routes sous `/api` |
| `config.py` | Chemins des ontologies, origines autorisées (CORS) |
| `routers/api.py` | Les endpoints ; convertit les résultats en modèles Pydantic |
| `schemas/modeles.py` | Forme des entrées et sorties Pydantic |
| `services/ontologie.py` | Lit l'OWL/XML de base et ses ajouts, construit le graphe familial (`Famille`) |
| `services/ecriture_ontologie.py` | Écrit atomiquement les nouvelles personnes dans l'OWL complémentaire |
| `services/relations.py` | Déduit les liens (« a est ___ de b ») et les phrases en français |

Flux lecture : requête → `routers/api.py` → `obtenir_famille()` (fichiers OWL combinés et mis en cache) → `relations.liens()` → JSON. Après une création, le cache est invalidé.

## Choix techniques

- **Pas de raisonneur dans l'application** : voir `docs/ontologie.md` §4. Le calcul en Python est déterministe, rapide et testable.
- **Lecture OWL sans bibliothèque externe** : moins de dépendances, moins de risques d'installation.
- **Ontologie lue une seule fois** : redémarrer le serveur après modification de `famille.owl` (`--reload` ne surveille que le code).
- **Ajouts persistants** : les créations sont stockées dans `ontology/famille_ajouts.owl`; le générateur de l'ontologie d'exemple ne les efface pas.
- **Versions figées** dans `requirements.txt`.
- **Liens dans les deux sens** : « a est ___ de b » est calculé séparément pour (a,b) et (b,a), d'où des libellés corrects (père/fils, oncle/neveu).

## Frontend (`frontend/`)

Angular 19, composants autonomes. Structure détaillée dans `frontend/README.md`.

- `AppComponent` charge la liste des personnes et gère les 3 onglets PrimeNG; `CreationPersonneComponent` pilote le formulaire de création.
- Un seul service HTTP (`services/api.service.ts`) ; il consulte les données et crée les personnes via l'API.
- La logique sans Angular (textes, couleurs, conversion du graphe, messages d'erreur) est dans `utils/` : fonctions pures, testables avec Node.
- Le graphe utilise `vis-network/standalone` en disposition hiérarchique : le niveau (génération) de chaque nœud est calculé par le backend (`Famille.niveau()`).
- Les réponses périmées sont ignorées (si l'utilisateur change de choix pendant un appel).
- CORS : le backend accepte `localhost` / `127.0.0.1` sur n'importe quel port (`config.py`).
