# Guide d'installation (Windows ; Mac/Linux : équivalents indiqués)

## 1. Backend

1. **Python 3.11 ou plus** : https://www.python.org/downloads/ . Sous Windows, cocher *Add Python to PATH* pendant l'installation.
2. **VS Code** : https://code.visualstudio.com/ ; ouvrir le dossier `famille-ontologie`.
3. Dans le terminal de VS Code (*Terminal → New Terminal*) :
   ```
   python --version
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   Mac/Linux : `python3` à la place de `python`, et `source .venv/bin/activate`. L'invite doit afficher `(.venv)`.
   Si PowerShell refuse l'activation : `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, ou utiliser `cmd`.
4. Tests : `python -m unittest discover -s tests -v` → attendu : `OK` (38 tests, aucun ignoré une fois FastAPI installé).
5. Lancer : `uvicorn app.main:app --reload`, puis ouvrir http://localhost:8000/docs et essayer `/api/personnes`.

## 2. Régénérer l'ontologie (si besoin)
Depuis la racine du projet : `python tools/construire_ontologie.py`. Redémarrer ensuite le serveur.

## 3. Frontend

1. Installer **Node.js version LTS** : https://nodejs.org (accepter les options par défaut). Fermer puis rouvrir VS Code.
2. Vérifier : `node --version` (v20.11 ou plus ; v22 ou plus recommandé) et `npm --version`.
3. Dans un **nouveau terminal** (le backend doit continuer à tourner dans le premier) :
   ```
   cd frontend
   npm install
   npm start
   ```
   `npm install` dure 1 à 3 minutes ; les messages « deprecated » sont normaux. Ne pas lancer `npm audit fix --force`.
4. Ouvrir http://localhost:4200. Attendu : trois onglets, la liste de 22 personnes, et l'arbre familial en 4 lignes (générations).
5. Facultatif : `npm test` → 7 tests (nécessite Node 22.18 ou plus).
6. Pas besoin d'installer Angular CLI globalement.

## 4. Lancer l'application complète (résumé)

| Terminal | Commandes | Résultat |
|---|---|---|
| 1 : backend | `cd backend`, activer `.venv`, `uvicorn app.main:app --reload` | http://localhost:8000/docs |
| 2 : frontend | `cd frontend`, `npm start` | http://localhost:4200 |

## Problèmes fréquents
| Message | Solution |
|---|---|
| `'python' n'est pas reconnu` | Réinstaller Python en cochant *Add to PATH*, ou essayer `py` |
| `No module named 'fastapi'` | Environnement non activé : relancer `.venv\Scripts\activate` |
| `Address already in use` | Port 8000 occupé : `uvicorn app.main:app --reload --port 8001` |
| 404 sur une personne | Identifiant sensible à la casse et sans accent (`Nadege`, pas `Nadège`) |
| `pip install` échoue avec une erreur de compilation (Rust, `pydantic-core`) | Python trop récent ou trop ancien pour les versions demandées : utiliser Python 3.11, 3.12 ou 3.13 |
| Page Angular : « Impossible de joindre l'API » | Backend arrêté : relancer `uvicorn app.main:app --reload` dans `backend/` |
| Console du navigateur : erreur CORS | Ouvrir le site par `http://localhost:4200` (le backend accepte localhost et 127.0.0.1, sur tout port) |
| `npm` / `node` non reconnu | Fermer et rouvrir le terminal après l'installation de Node.js |
| `npm install` : erreur réseau ou `ERESOLVE` | Relancer ; vérifier la connexion ; ne jamais utiliser `--force` sans me demander |
| Port 4200 occupé | `npm start -- --port 4300` |
| Arbre vide ou mal placé | Recharger la page (F5) ; vérifier http://localhost:8000/api/graphe |
