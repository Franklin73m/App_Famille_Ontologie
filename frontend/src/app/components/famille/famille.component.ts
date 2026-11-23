import { Component, Input, inject } from '@angular/core';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { TagModule } from 'primeng/tag';

import { Famille, Lien, Membre, Personne } from '../../models/api.models';
import { ApiService } from '../../services/api.service';
import { ageTexte, classeSexe, symboleSexe } from '../../utils/affichage';
import { messageErreur } from '../../utils/erreurs';
import { SelecteurPersonneComponent } from '../selecteur-personne/selecteur-personne.component';

/** Onglet « Famille d'une personne » : tous ses liens de parenté. */
@Component({
  selector: 'app-famille',
  standalone: true,
  imports: [CardModule, MessageModule, ProgressSpinnerModule, SelecteurPersonneComponent, TagModule],
  templateUrl: './famille.component.html',
})
export class FamilleComponent {
  @Input() personnes: Personne[] = [];

  @Input()
  set personneInitiale(id: string) {
    if (id && id !== this.selection) {
      this.choisir(id);
    }
  }

  private api = inject(ApiService);

  selection = '';
  resultat: Famille | null = null;
  chargement = false;
  erreur = '';

  get groupes(): { type: string; membres: { personne: Membre; liens: Lien[] }[] }[] {
    const groupes = new Map<string, Map<string, { personne: Membre; liens: Lien[] }>>();

    for (const membre of this.resultat?.membres ?? []) {
      for (const lien of membre.liens) {
        const type = lien.libelle || lien.precision || 'Autres liens';
        let membres = groupes.get(type);
        if (!membres) {
          membres = new Map();
          groupes.set(type, membres);
        }
        let entree = membres.get(membre.id);
        if (!entree) {
          entree = { personne: membre, liens: [] };
          membres.set(membre.id, entree);
        }
        entree.liens.push(lien);
      }
    }

    return Array.from(groupes, ([type, membres]) => ({ type, membres: Array.from(membres.values()) }));
  }

  choisir(id: string): void {
    this.selection = id;
    this.resultat = null;
    this.erreur = '';
    this.chargement = false;
    if (!id) {
      return;
    }
    this.chargement = true;
    this.api.famille(id).subscribe({
      next: (famille) => {
        if (this.selection !== id) return; // réponse périmée : une autre personne a été choisie entre-temps
        this.resultat = famille;
        this.chargement = false;
      },
      error: (err) => {
        if (this.selection !== id) return;
        this.erreur = messageErreur(err);
        this.chargement = false;
      },
    });
  }

  age(p: Personne): string {
    return ageTexte(p.age);
  }

  symbole(p: Personne): string {
    return symboleSexe(p.sexe);
  }

  classe(p: Personne): string {
    return classeSexe(p.sexe);
  }
}
