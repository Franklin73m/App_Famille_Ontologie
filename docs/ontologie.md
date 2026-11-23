# Ontologie

Fichier : `ontology/famille.owl` (OWL/XML). IRI de base : `http://www.semanticweb.org/agognonulrich/ontologies/2026/9/untitled-ontology-2`.
Original conservé : `ontology/versions/famille_v0_original.owl`. Le fichier corrigé est **généré** par `tools/construire_ontologie.py` à partir de l'original : ne pas le modifier à la main sans reporter le changement dans le script.

## 1. Contenu

**Classes** : Personne, Sexe (Masculin, Feminin), Parent, Pere, Mere, Enfant, Fils, Fille, GrandParent, GrandPere, GrandeMere, PetitEnfant, PetitFils, PetiteFille, Frere, Soeur, DemiFrere, DemiSoeur, Oncle, Tante, Neveu, Niece, Cousin, Cousine, BeauParent, BeauPere, BelleMere, BeauFils, BelleFille, Homme, Femme, Garcon, Fillette.

**Propriétés d'objet** : `parentDe` (inverse `enfantDe`), `marierA` (symétrique), `grandParentDe` (déduite : parentDe ∘ parentDe), `frereDe`, `soeurDe`.
**Propriété de données** : `age` (entier).

## 2. Faits de base (ce que l'application lit)

| Fait | Représentation dans l'OWL |
|---|---|
| Sexe | `ClassAssertion(Masculin ou Feminin, individu)` |
| Âge | `DataPropertyAssertion(age, individu, entier)` |
| Nom affiché | `AnnotationAssertion(rdfs:label, individu, texte)` |
| Parenté | `ObjectPropertyAssertion(parentDe, parent, enfant)` (jamais `enfantDe` : l'inverse est implicite) |
| Mariage | `ObjectPropertyAssertion(marierA, a, b)` (une seule direction suffit) |

## 3. Corrections apportées à l'original

| # | Défaut dans l'original | Correction |
|---|---|---|
| C1 | `Parent` ≡ a un `Enfant`, `Enfant` ≡ a un `Parent` : circulaire, jamais déduit | Les deux utilisent maintenant `Personne` comme filler |
| C2 | `grandParentDe` sous-propriété de `parentDe` (un grand-parent devenait parent) | Sous-propriété supprimée, remplacée par la chaîne `parentDe ∘ parentDe ⊑ grandParentDe` |
| C3 | `grandParentDe` inverse-fonctionnelle (un seul grand-parent par personne) | Caractéristique supprimée |
| C4 | `frereDe`, `soeurDe` transitives | Caractéristique supprimée |
| C5 | Masculin / Feminin non disjoints | `DisjointClasses(Masculin, Feminin)` ajouté |
| C6 | `Neuveu ⊑ Fils`, `Niece ⊑ Fille` | Axiomes supprimés |
| C7 | `Homme`, `Femme`, `Garcon`, `Fillette` : cardinalités de `age` mal formées | Seuil réel : adulte = âge ≥ 18, mineur = âge < 18 |
| C8 | 10 propriétés numérotées (`parentDe1-3`, `enfantDe1-3`, `marierA1-4`) avec domaines/ranges bloquants | Supprimées avec tous leurs axiomes |
| C9 | `DemiFrere`, `DemiSoeur` : définitions mal formées | Gardées comme sous-classes de Frere/Soeur ; la distinction est faite par le backend |
| C10 | Faute `Neuveu` | Renommé `Neveu` |
| + | Caractéristiques manquantes | `marierA` symétrique et irréflexive, `parentDe` asymétrique, domaine/range `Personne` |

Conservé tel quel : toutes les autres définitions de classes (Oncle, Tante, Cousin, Cousine, Pere, Mere, GrandPere, BeauPere, etc.).

## 4. Limite assumée de l'OWL

OWL ne sait pas exprimer « mêmes parents » ni « partage un seul parent ». Un raisonneur (HermiT) ne peut donc pas déduire à lui seul Frere, Oncle, Cousin... à partir de `parentDe`. Le backend Python calcule ces liens (`backend/app/services/relations.py`) en suivant les définitions des classes. Protégé reste utile pour visualiser l'ontologie et vérifier sa **cohérence**.

## 5. Individus (famille d'exemple, 22 personnes)

```
Dossou (M,84) ⚭ Adjoa (F,80)
├── Koffi (M,58) ⚭ Ayaba (F,56)
│   ├── Mawuli (M,30) ⚭ Nadège (F,29)
│   │   └── Selom (M,4)
│   └── Edem (F,27)
├── Afi (F,55) ⚭ Roland (M,57)
│   ├── Yawa (F,29) ⚭ Prosper (M,31)
│   │   └── Ama (F,2)
│   └── Kossi (M,25)
│   Roland a aussi, avec Ablavi (F,60) :
│   └── Fabrice (M,34) ⚭ Carine (F,33)
│       └── Daniel (M,8)          → Fabrice est le demi-frère de Yawa et Kossi
└── Sena (M,52) ⚭ Esther (F,50)
    ├── Gilles (M,22)
    └── Amavi (F,19)
```

Cas couverts : parents, enfants, époux, grands-parents, arrière-grands-parents, fratrie, demi-fratrie, oncles/tantes (y compris par alliance), neveux/nièces, cousins, belle-mère (remariage), beau-parent, gendre/belle-fille, beaux-frères/belles-sœurs.

Pour utiliser une vraie famille : modifier `PERSONNES`, `PARENTE`, `MARIAGES` en haut de `tools/construire_ontologie.py`, puis `python tools/construire_ontologie.py`. Mettre ensuite à jour les valeurs attendues dans `backend/tests/`.

## 6. Vérification dans Protégé (à faire)

1. Ouvrir `ontology/famille.owl` dans Protégé.
2. Menu *Reasoner* → *HermiT* → *Start reasoner*. Résultat attendu : ontologie **cohérente**, aucune classe en rouge.
3. Test de la disjonction : dans l'onglet *Individuals*, ajouter temporairement le type `Feminin` à `Koffi`, relancer HermiT : il doit signaler une incohérence. Annuler ensuite la modification (ne pas enregistrer).
4. Contrôle des seuils : après `Synchronize reasoner`, `Selom` (4 ans) doit apparaître dans `Garcon`, `Dossou` dans `Homme`.
5. `Dossou` doit avoir `grandParentDe` vers Mawuli, Edem, Yawa, Kossi, Gilles, Amavi.
