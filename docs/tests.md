# Tests

Lancer depuis `backend/` : `python -m unittest discover -s tests -v` (ou `pytest` si installé).

| Fichier | Contenu | Nombre |
|---|---|---|
| `backend/tests/test_relations.py` | Lecture de l'ontologie, moteur de relations, niveaux de génération | 30 |
| `backend/tests/test_api.py` | Endpoints (ignorés si FastAPI n'est pas installé) | 8 |
| `frontend/src/app/utils/*.test.mjs` | Fonctions utilitaires du frontend (`npm test`) | 7 |

## Résultats attendus (extraits)

| a | b | Résultat « a est ___ de b » |
|---|---|---|
| Koffi | Mawuli | Père |
| Edem | Mawuli | Sœur |
| Fabrice | Yawa | Demi-frère |
| Sena | Mawuli | Oncle |
| Esther | Mawuli | Tante (par alliance) |
| Mawuli | Gilles | Cousin |
| Gilles | Ayaba | Neveu (par alliance) |
| Dossou | Selom | Arrière-grand-père |
| Afi | Fabrice | Belle-mère (remariage d'un parent) |
| Koffi | Nadège | Beau-père (parent du conjoint) |
| Nadège | Koffi | Belle-fille (conjoint(e) de l'enfant) |
| Roland | Sena | Beau-frère |
| Ablavi | Yawa | aucun lien |

## État de vérification (21/11/2026, environnement de création sans accès réseau)

| Élément | Statut |
|---|---|
| 30 tests du moteur (backend) | ✅ exécutés, tous passent |
| 7 tests utilitaires du frontend | ✅ exécutés, tous passent |
| Fonctions des routes API | ✅ exécutées avec de faux modules `fastapi`/`pydantic` : réponses, codes 400/404, graphe corrects |
| TypeScript du frontend | ✅ vérifié avec de faux typings Angular (aucune erreur de type) |
| 8 tests d'API avec le vrai FastAPI | ⏳ non exécutés (FastAPI non installable ici) |
| `ng build` / `ng serve`, templates HTML Angular | ⏳ non exécutés (Angular non installable ici) |
| Ontologie dans Protégé + HermiT | ⏳ à faire (`docs/ontologie.md` §6) |

Un test de symétrie vérifie sur les 22×22 paires que si a a un lien avec b, b en a un avec a.

## Test manuel de bout en bout (à faire sur le PC)
1. Backend et frontend lancés (`docs/guide-installation.md` §4).
2. Onglet Famille, choisir **Mawuli** : 15 personnes, la première est Nadège (« Nadège est l'épouse de Mawuli »). Ablavi n'apparaît pas.
3. Onglet Lien : **Sena** et **Mawuli** → « Sena est l'oncle de Mawuli », puis « Mawuli est le neveu de Sena ». Le bouton ⇄ inverse l'ordre.
4. Onglet Lien : **Ablavi** et **Yawa** → « Aucun lien familial direct n'a été trouvé… ».
5. Onglet Lien : deux fois la même personne → message « Choisissez deux personnes différentes ».
6. Onglet Arbre : 4 lignes de générations ; Dossou et Adjoa en haut, Selom, Ama et Daniel en bas ; Roland et Ablavi sur la même ligne qu'Afi.
7. Arrêter le backend, recharger la page : message « Impossible de joindre l'API » avec le bouton Réessayer.
