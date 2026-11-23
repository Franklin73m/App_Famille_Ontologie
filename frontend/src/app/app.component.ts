import { Component, OnInit, inject } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { TabsModule } from 'primeng/tabs';

import { ArbreComponent } from './components/arbre/arbre.component';
import { CreationPersonneComponent } from './components/creation-personne/creation-personne.component';
import { FamilleComponent } from './components/famille/famille.component';
import { LienComponent } from './components/lien/lien.component';
import { Personne } from './models/api.models';
import { ApiService } from './services/api.service';
import { messageErreur } from './utils/erreurs';

/** Composant racine : charge la liste des personnes puis affiche l'onglet choisi. */
@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    ArbreComponent,
    ButtonModule,
    CardModule,
    CreationPersonneComponent,
    FamilleComponent,
    LienComponent,
    MessageModule,
    ProgressSpinnerModule,
    TabsModule,
  ],
  templateUrl: './app.component.html',
})
export class AppComponent implements OnInit {
  private api = inject(ApiService);

  personnes: Personne[] = [];
  chargement = true;
  erreur = '';
  onglet: string | number = 'family';
  creationOuverte = false;
  succes = '';
  personneInitiale = '';

  ngOnInit(): void {
    this.charger();
  }

  charger(): void {
    this.chargement = true;
    this.erreur = '';
    this.succes = '';
    this.api.personnes().subscribe({
      next: (personnes) => {
        this.personnes = personnes;
        this.chargement = false;
      },
      error: (err) => {
        this.erreur = messageErreur(err);
        this.chargement = false;
      },
    });
  }

  ouvrirCreation(): void {
    this.succes = '';
    this.creationOuverte = true;
  }

  personneAjoutee(personne: Personne): void {
    this.personnes = [...this.personnes, personne].sort((a, b) => a.nom.localeCompare(b.nom, 'fr'));
    this.personneInitiale = personne.id;
    this.onglet = 'family';
    this.succes = `${personne.nom} a été créée et rattachée à sa famille.`;
  }
}
