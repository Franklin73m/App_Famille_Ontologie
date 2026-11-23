# API

Base : `http://localhost:8000/api`. Documentation interactive générée : `http://localhost:8000/docs`.
Les endpoints de consultation sont en `GET`. Les identifiants des personnes déjà présentes sont ceux de l'ontologie (ex. `Mawuli`, `Nadege`).

| Endpoint | Description |
|---|---|
| `/sante` | Vérifie l'API et le chargement de l'ontologie |
| `/personnes` | Liste de toutes les personnes (triées par nom) |
| `POST /personnes` | Crée une personne et la rattache à une personne existante |
| `/personnes/{id}/famille` | Toute la famille d'une personne, avec le lien de chacun |
| `/lien?a={id}&b={id}` | Lien entre deux personnes, dans les deux sens |
| `/graphe` | Nœuds et arêtes pour dessiner l'arbre |

## Exemples

`GET /api/sante`
```json
{"statut": "ok", "personnes": 22}
```

`GET /api/lien?a=Sena&b=Mawuli`
```json
{
  "a": {"id": "Sena", "nom": "Sena", "sexe": "M", "age": 52},
  "b": {"id": "Mawuli", "nom": "Mawuli", "sexe": "M", "age": 30},
  "a_vers_b": [{"libelle": "Oncle", "precision": "", "phrase": "Sena est l'oncle de Mawuli"}],
  "b_vers_a": [{"libelle": "Neveu", "precision": "", "phrase": "Mawuli est le neveu de Sena"}],
  "resume": "Sena est l'oncle de Mawuli"
}
```

`GET /api/personnes/Mawuli/famille` → `{"personne": {...}, "membres": [{"id": "Nadege", ..., "liens": [{"libelle": "Épouse", ...}]}, ...]}`, triés des plus proches aux plus éloignés.

`GET /api/graphe` → `{"noeuds": [{"id","label","sexe","age","niveau"}], "aretes": [{"source","cible","type"}]}` ; `type` = `parent` (source est parent de cible) ou `mariage`.

## Créer une personne

`POST /api/personnes`
```json
{
  "nom": "Élodie Martin",
  "sexe": "F",
  "age": 36,
  "personne_liee_id": "Ama",
  "relation": "parent"
}
```

`sexe` vaut `M` ou `F`; `age` est facultatif (de 0 à 130). `relation` vaut `parent` (la nouvelle personne est le parent), `enfant` (elle est l'enfant) ou `conjoint`. L'identifiant est généré depuis le nom et reçoit un suffixe en cas de doublon. La réponse `201` contient la personne créée.

Les ajouts sont écrits atomiquement dans `ontology/famille_ajouts.owl`, séparément de l'ontologie d'exemple régénérée par `tools/construire_ontologie.py`. Ils restent disponibles après redémarrage du backend.

## Erreurs
| Code | Cas |
|---|---|
| 404 | Identifiant inconnu |
| 400 | `/lien` avec deux fois la même personne |
| 422 | Paramètre manquant, nom vide, sexe ou relation invalide, âge hors limites |

Deux personnes sans lien : réponse 200, `a_vers_b` et `b_vers_a` vides, `resume` = « Aucun lien familial direct n'a été trouvé entre X et Y. »
