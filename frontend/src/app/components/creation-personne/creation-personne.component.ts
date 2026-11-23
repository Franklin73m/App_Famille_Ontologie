import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { RadioButtonModule } from 'primeng/radiobutton';
import { SelectModule } from 'primeng/select';

import { Personne, PersonneCreation, RelationCreation } from '../../models/api.models';
import { ApiService } from '../../services/api.service';
import { messageErreur } from '../../utils/erreurs';

/** Formulaire de création d'une personne rattachée à un membre existant. */
@Component({
  selector: 'app-creation-personne',
  standalone: true,
  imports: [ButtonModule, DialogModule, FormsModule, InputTextModule, MessageModule, RadioButtonModule, SelectModule],
  templateUrl: './creation-personne.component.html',
})
export class CreationPersonneComponent {
  @Input() personnes: Personne[] = [];
  @Input() visible = false;
  @Output() visibleChange = new EventEmitter<boolean>();
  @Output() personneCreee = new EventEmitter<Personne>();

  private api = inject(ApiService);

  readonly sexes = [
    { label: 'Femme', value: 'F' as const },
    { label: 'Homme', value: 'M' as const },
  ];

  readonly relations: { label: string; value: RelationCreation }[] = [
    { label: 'Parent de la personne choisie', value: 'parent' },
    { label: 'Enfant de la personne choisie', value: 'enfant' },
    { label: 'Conjoint(e) de la personne choisie', value: 'conjoint' },
  ];

  nom = '';
  sexe: 'M' | 'F' | null = null;
  age: number | null = null;
  personneLieeId = '';
  relation: RelationCreation | null = null;
  chargement = false;
  erreur = '';

  formulaireValide(): boolean {
    return Boolean(
      this.nom.trim()
      && this.sexe
      && this.personneLieeId
      && this.relation
      && (this.age === null || (Number.isInteger(this.age) && this.age >= 0 && this.age <= 130)),
    );
  }

  changerVisibilite(visible: boolean): void {
    if (!visible && this.chargement) {
      return;
    }
    this.visible = visible;
    this.visibleChange.emit(visible);
    if (!visible) {
      this.reinitialiser();
    }
  }

  creer(): void {
    this.erreur = '';
    if (!this.formulaireValide() || !this.sexe || !this.relation) {
      this.erreur = 'Complétez les champs obligatoires et vérifiez l’âge.';
      return;
    }

    const nouvellePersonne: PersonneCreation = {
      nom: this.nom.trim(),
      sexe: this.sexe,
      age: this.age,
      personne_liee_id: this.personneLieeId,
      relation: this.relation,
    };

    this.chargement = true;
    this.api.creerPersonne(nouvellePersonne).subscribe({
      next: (personne) => {
        this.chargement = false;
        this.personneCreee.emit(personne);
        this.changerVisibilite(false);
      },
      error: (err) => {
        this.erreur = messageErreur(err);
        this.chargement = false;
      },
    });
  }

  private reinitialiser(): void {
    this.nom = '';
    this.sexe = null;
    this.age = null;
    this.personneLieeId = '';
    this.relation = null;
    this.erreur = '';
  }
}
