import { Component, Input, inject } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { TagModule } from 'primeng/tag';

import { LienEntre, Personne } from '../../models/api.models';
import { ApiService } from '../../services/api.service';
import { messageErreur } from '../../utils/erreurs';
import { SelecteurPersonneComponent } from '../selecteur-personne/selecteur-personne.component';

/** Onglet « Lien entre deux personnes ». */
@Component({
  selector: 'app-lien',
  standalone: true,
  imports: [ButtonModule, CardModule, MessageModule, ProgressSpinnerModule, SelecteurPersonneComponent, TagModule],
  templateUrl: './lien.component.html',
})
export class LienComponent {
  @Input() personnes: Personne[] = [];

  private api = inject(ApiService);

  a = '';
  b = '';
  resultat: LienEntre | null = null;
  chargement = false;
  erreur = '';

  choisirA(id: string): void {
    this.a = id;
    this.reinitialiserResultat();
  }

  choisirB(id: string): void {
    this.b = id;
    this.reinitialiserResultat();
  }

  inverser(): void {
    [this.a, this.b] = [this.b, this.a];
    this.reinitialiserResultat();
  }

  chercher(): void {
    this.reinitialiserResultat();
    if (!this.a || !this.b) {
      return;
    }
    if (this.a === this.b) {
      this.erreur = 'Choisissez deux personnes différentes.';
      return;
    }

    const a = this.a;
    const b = this.b;
    const perime = () => a !== this.a || b !== this.b;
    this.chargement = true;
    this.api.lien(a, b).subscribe({
      next: (lien) => {
        if (perime()) return;
        this.resultat = lien;
        this.chargement = false;
      },
      error: (err) => {
        if (perime()) return;
        this.erreur = messageErreur(err);
        this.chargement = false;
      },
    });
  }

  private reinitialiserResultat(): void {
    this.resultat = null;
    this.erreur = '';
    this.chargement = false;
  }
}
