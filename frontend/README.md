# Frontend Angular

Application Angular 19 (composants autonomes, sans NgModule) qui interroge le backend FastAPI.
Prérequis : Node.js LTS (voir `docs/guide-installation.md`) et le backend lancé sur http://localhost:8000.

```bash
cd frontend
npm install        # une seule fois (1 à 3 minutes)
npm start          # puis ouvrir http://localhost:4200
npm test           # 7 tests des fonctions utilitaires (Node 22.18 ou plus)
```

Ne pas installer Angular CLI globalement : `npm start` utilise celui du projet.

## Où se trouve quoi

```
frontend/
├── package.json, angular.json, tsconfig*.json   ← configuration (versions Angular 19.x)
└── src/
    ├── index.html, main.ts, styles.css          ← page, démarrage, styles globaux
    ├── vis-network.d.ts                         ← déclaration minimale de la bibliothèque de graphe
    └── app/
        ├── config.ts                            ← API_URL : adresse du backend (à changer si autre port)
        ├── app.config.ts                        ← fournisseurs (HttpClient)
        ├── app.component.{ts,html}              ← racine : charge les personnes, gère les 3 onglets
        ├── models/api.models.ts                 ← interfaces TypeScript du JSON du backend
        ├── services/api.service.ts              ← TOUS les appels HTTP
        ├── utils/                               ← fonctions pures + leurs tests (*.test.mjs)
        └── components/
            ├── selecteur-personne/              ← liste déroulante réutilisable
            ├── famille/                         ← onglet « Famille d'une personne »
            ├── lien/                            ← onglet « Lien entre deux personnes »
            └── arbre/                           ← onglet « Arbre familial » (vis-network)
```

## Flux
`AppComponent` appelle `GET /api/personnes` au démarrage et transmet la liste aux onglets (`@Input`).
`FamilleComponent` → `GET /api/personnes/{id}/famille` ; `LienComponent` → `GET /api/lien?a=&b=` ;
`ArbreComponent` → `GET /api/graphe`. Les erreurs HTTP sont converties en messages lisibles par `utils/erreurs.ts`.

## Remarques
- Angular 19 est fixé volontairement : c'est la version pour laquelle la configuration a été écrite. Pour passer à une version plus récente plus tard : `npx ng update @angular/core @angular/cli`.
- Après `npm install`, commiter `package-lock.json` (il fige les versions installées).
