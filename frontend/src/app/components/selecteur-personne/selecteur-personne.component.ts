import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { SelectModule } from 'primeng/select';

import { Personne } from '../../models/api.models';

/** Liste déroulante réutilisable pour choisir une personne. */
@Component({
  selector: 'app-selecteur-personne',
  standalone: true,
  imports: [FormsModule, SelectModule],
  templateUrl: './selecteur-personne.component.html',
})
export class SelecteurPersonneComponent {
  @Input() etiquette = 'Personne';
  @Input() inputId = 'personne-select';
  @Input() placeholder = 'Rechercher une personne';
  @Input() valeur = '';
  @Input() personnes: Personne[] = [];
  @Output() valeurChange = new EventEmitter<string>();

  selectionner(id: string | null | undefined): void {
    this.valeurChange.emit(id ?? '');
  }
}
