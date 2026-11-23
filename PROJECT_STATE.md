# PROJECT_STATE : état de reprise

*Dernière mise à jour : 22/11/2026.*

## 1. Objectif
Application web utilisant une ontologie OWL familiale : consulter la famille d'une personne, trouver le lien entre deux personnes et explorer l'arbre. L'application permet aussi d'ajouter une personne en la rattachant comme parent, enfant ou conjoint.

## 2. Stack et décisions
| Sujet | Décision | Raison |
|---|---|---|
| Backend | Python / FastAPI | Java + Maven écartés pour éviter les conflits de dépendances |
| Dépendances Python | Bornes de versions (`>=x,<y`) | Compatibilité avec les versions récentes de Python |
| Frontend | Angular 19, composants autonomes; versions runtime/compilateur alignées sur 19.2.25 | La version d'Angular est fixée; l'ancien désalignement provoquait un écran blanc |
| Interface | PrimeNG 19.1.4, `@primeng/themes` 19.1.4, PrimeIcons 8.0.2, thème Aura | Une seule bibliothèque d'interface, version compatible avec Angular 19 |
| Palette | Marine `#14213D`, crème `#F4EDE0`, corail `#FF6B5B` | Palette choisie par l'utilisateur et appliquée à l'interface et au graphe |
| Création OWL | `ontology/famille_ajouts.owl`, séparé de `famille.owl` généré | Préserver les ajouts applicatifs lors de la régénération de l'ontologie d'exemple |
| Lien de création | Relation parent/enfant/conjoint explicitement choisie | Ajouter une personne au bon endroit sans devoir saisir les autres liens déduits |
| Graphe | `vis-network/standalone`, disposition hiérarchique | Arbre interactif; déclaration de types minimale dans `frontend/src/vis-network.d.ts` |
| Raisonnement | Calculé en Python, pas par HermiT à l'exécution | HermiT dépend de Java; plusieurs règles de parenté sont calculées par le moteur applicatif |
| Lecture et format OWL | Bibliothèque standard `xml.etree`, format OWL/XML | Pas de dépendance de lecture supplémentaire; format compatible Protégé |
| Tests | `pytest`/`unittest` backend, `node --test` frontend | Outils déjà utilisés par le projet |
| TypeScript | `rootDir: "./src"` dans `frontend/tsconfig.json` | Évite le diagnostic sur le dossier source commun et stabilise le layout de compilation |

Faits OWL utilisés : classes `Masculin`/`Feminin`, propriétés `age`, `parentDe`, `marierA` et annotation `rdfs:label`. Les autres relations sont déduites par `backend/app/services/relations.py`.

## 3. Terminé
- Ontologie d'exemple corrigée et reproductible par `tools/construire_ontologie.py`; documentation des corrections dans `docs/ontologie.md`.
- Backend : lecture/fusion de l'ontologie de base et de son complément, moteur de relations, niveaux de génération, endpoints REST et CORS.
- `POST /api/personnes` : validation, identifiant unique, relation parent/enfant/conjoint, écriture OWL atomique et invalidation du cache.
- Frontend : vues famille, lien et arbre; formulaire PrimeNG avec choix radio explicite de la relation; erreurs, chargement, adaptation mobile.
- Thème Aura personnalisé, couleurs harmonisées, onglet actif à bords droits et animation CSS de changement de page. L'animation respecte `prefers-reduced-motion`.
- Alignement Angular après l'erreur `ɵɵgetReplaceMetadataURL is not a function`.
- Diagnostic VS Code **Problems** sur `rootDir` corrigé; la dernière lecture du panneau n'a relevé aucune erreur.
- Documentation API, architecture, changelog et état de reprise.

## 4. Vérifications effectuées
| Vérification | Résultat | Portée / limite |
|---|---|---|
| `npm.cmd run build` | Réussi le 22/11/2026 | Dernière vérification après le changement de `rootDir` |
| `npm.cmd test` | 7/7 réussis | Tests des fonctions utilitaires et du graphe |
| `backend\\.venv\\Scripts\\python.exe -m pytest` | 42/42 réussis lors de la dernière exécution | Backend inchangé depuis |
| VS Code **Problems** | Aucune erreur après le correctif `rootDir` | Diagnostic contrôlé dans l'espace de travail |
| Navigateur | Choix « enfant », onglet actif, transition et largeur 390 px vérifiés | Le formulaire n'a pas été envoyé, pour éviter d'écrire une donnée de test |

La base de l'ontologie contient 22 personnes. Une vérification navigateur ultérieure a affiché 23 personnes et le fichier optionnel `ontology/famille_ajouts.owl` existe maintenant. Son contenu et l'origine du nouvel ajout n'ont pas été inspectés dans cette reprise.

## 5. Non vérifié / à valider
- Le flux complet de création depuis le navigateur (POST réel, puis consultation après redémarrage) n'a pas été rejoué après le passage des relations aux boutons radio. Les tests backend couvrent la relation enfant et les tests navigateur vérifient la sélection et l'activation du bouton, sans envoyer le formulaire.
- Le contenu de `ontology/famille_ajouts.owl`, son identité ajoutée et sa cohérence dans Protégé/HermiT restent à vérifier par le propriétaire si nécessaire. Ne pas supprimer ce fichier pour tester.
- L'ontologie complète n'a pas été rouverte dans Protégé/HermiT depuis les derniers changements.
- Les trois vues ont été vérifiées dans le navigateur, mais le dernier contrôle de débordement a été fait à 390 px; faire un contrôle sur les appareils cibles avant déploiement.

## 6. Prochaines étapes possibles
1. Sauvegarder `ontology/famille_ajouts.owl` avant toute opération sur les données.
2. Si un test réel de création est nécessaire, utiliser une copie temporaire de l'ontologie ou un chemin d'ajouts temporaire.
3. Vérifier l'ontologie dans Protégé/HermiT et exécuter la procédure `docs/tests.md` avant livraison.
4. Les captures d'écran et le déploiement restent optionnels.

## 7. Pièges connus
- **Ne pas supprimer ni remplacer `ontology/famille_ajouts.owl`** : il existe et peut contenir des données utilisateur. Le générateur `tools/construire_ontologie.py` régénère `famille.owl`, pas le fichier d'ajouts.
- Le backend met l'ontologie en cache; le POST invalide ce cache. Après une modification manuelle ou une régénération externe, redémarrer le backend.
- `relation="enfant"` signifie que la personne sélectionnée est le parent : l'assertion écrite est `parentDe(personne sélectionnée, nouvelle personne)`.
- Les identifiants générés sont des slugs sans accents/espaces et reçoivent un suffixe en cas de doublon; les noms affichés gardent leurs accents.
- Pour les frères/sœurs, le moteur compare les parents connus; avec un seul parent renseigné, des enfants de ce parent peuvent être considérés frères/sœurs complets.
- « Beau-père / belle-mère » et « beau-fils / belle-fille » ont plusieurs sens en français; l'API fournit une précision.
- Deux personnes sans ancêtre commun ni mariage entre leurs familles peuvent ne partager aucun lien connu.
- `npm test` peut émettre l'avertissement Node `MODULE_TYPELESS_PACKAGE_JSON`; les 7 tests passent néanmoins. Utiliser Node 22.18 ou plus.
- Dans PowerShell, utiliser `npm.cmd` si la politique bloque `npm.ps1`.
- Les erreurs WebSocket `ERR_CONNECTION_REFUSED` sur le port 4200 surviennent si le navigateur est ouvert après l'arrêt de `ng serve`; elles ne signalent pas une erreur applicative.
- Garder Angular 19 et `rootDir: "./src"`; ne pas lancer `ng update` ni `npm audit fix --force` pour masquer un diagnostic de configuration.
