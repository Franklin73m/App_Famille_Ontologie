# Changelog

## [Non publié] - 2026-11-22
### Ajouté
- Interface PrimeNG 19 (thème Aura), formulaire de création d'une personne et rattachement comme parent, enfant ou conjoint.
- `POST /api/personnes` : validation, identifiant unique et écriture atomique dans `ontology/famille_ajouts.owl`, séparée de l'ontologie générée.
- Palette d'interface marine (`#14213D`), crème (`#F4EDE0`) et corail (`#FF6B5B`), appliquée aussi à l'arbre vis-network.
- Choix explicites par boutons radio pour le lien familial dans la fenêtre de création.
- Transition de panneau façon changement de page; les onglets actifs ont des bords droits et l'animation respecte `prefers-reduced-motion`.

### Corrigé
- Versions Angular runtime/compilateur alignées en 19.2.25 après l'erreur `ɵɵgetReplaceMetadataURL is not a function` qui empêchait l'affichage.
- Choix du lien « Enfant de la personne choisie » rendu visible et direct; le lien enfant est aussi couvert par les tests API.
- `frontend/tsconfig.json` définit maintenant `rootDir: "./src"` pour éliminer le diagnostic TypeScript sur le dossier source commun.

### Décisions
- Conserver les nouvelles personnes dans une ontologie OWL complémentaire afin qu'une régénération de `famille.owl` n'écrase pas les ajouts faits depuis l'application.
- Utiliser des boutons radio visibles pour les trois relations plutôt qu'une liste déroulante, afin de rendre le choix du lien enfant explicite.
- Personnaliser Aura et les styles de l'application avec les trois couleurs demandées, sans ajouter une autre bibliothèque d'interface.
- Utiliser une animation CSS légère de rotation/transfert pour les panneaux; désactivation en mode réduction des mouvements.
- Fixer explicitement `rootDir` à `src` pour conserver une disposition stable des sorties TypeScript.

### Vérifications
- `npm.cmd run build` réussi; `npm.cmd test` : 7 tests réussis.
- Tests backend : 42 réussis lors de la dernière exécution; aucune modification backend depuis.
- Le panneau VS Code **Problems** ne signalait plus d'erreur après l'ajout de `rootDir`.
- Vérification navigateur : lien enfant sélectionnable, formulaire activé, onglet entier corail sans arrondi, animation présente et aucun débordement à 390 px. Le formulaire n'a pas été envoyé pendant cette vérification.

## [0.2.0] - 2026-11-21
### Ajouté
- Frontend Angular 19 : onglets « Famille d'une personne », « Lien entre deux personnes », « Arbre familial » (vis-network).
- 7 tests des fonctions utilitaires du frontend (`npm test`).
- 5 tests sur les niveaux de génération (backend).
- Procédure de test manuel de bout en bout (`docs/tests.md`).

### Corrigé
- Backend : calcul des générations pour l'arbre (une personne sans parents connus et sans conjoint, comme Ablavi, était placée trop haut ; les demi-frères étaient sur des lignes différentes).
- `requirements.txt` : versions exactes remplacées par des bornes, pour éviter les échecs d'installation avec un Python récent.
- CORS : localhost / 127.0.0.1 acceptés sur tout port (au lieu de 4200 seulement).

## [0.1.0] - 2026-11-21
### Ajouté
- `ontology/famille.owl` : ontologie corrigée + 22 individus (4 générations, 26 liens de parenté, 7 mariages).
- `tools/construire_ontologie.py` : génération reproductible de l'ontologie.
- Backend FastAPI : `/api/sante`, `/api/personnes`, `/api/personnes/{id}/famille`, `/api/lien`, `/api/graphe`.
- Moteur de relations (parenté directe, fratrie complète/demi, oncles/tantes, neveux/nièces, cousins, belle-famille, alliance).
- 25 tests unitaires du moteur + 8 tests d API.
- Documentation complète.

### Corrigé (ontologie d'origine, détails dans `docs/ontologie.md`)
- Définition circulaire Parent/Enfant ; `grandParentDe` ; transitivité de `frereDe`/`soeurDe` ; disjonction Masculin/Feminin ; Neveu/Nièce ; seuils d'âge ; propriétés numérotées supprimées ; DemiFrere/DemiSoeur ; faute `Neuveu`.

### Décision
- Java/Maven remplacé par Python/FastAPI ; HermiT non utilisé dans l'application (conservé dans Protégé pour vérifier la cohérence).
