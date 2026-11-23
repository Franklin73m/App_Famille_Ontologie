import { AfterViewInit, Component, ElementRef, OnDestroy, ViewChild, inject } from '@angular/core';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { TagModule } from 'primeng/tag';
import { Network } from 'vis-network/standalone';

import { ApiService } from '../../services/api.service';
import { versVis } from '../../utils/affichage';
import { messageErreur } from '../../utils/erreurs';

/** Disposition en niveaux : une ligne par génération (le niveau vient du backend). */
const OPTIONS = {
  layout: {
    hierarchical: {
      enabled: true,
      direction: 'UD',
      levelSeparation: 120,
      nodeSpacing: 130,
      treeSpacing: 170,
    },
  },
  physics: false,
  interaction: { hover: true, zoomView: true, dragNodes: true },
  edges: { smooth: { enabled: true, type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.5 } },
  nodes: {
    font: { size: 15, color: '#14213D', background: '#F4EDE0' },
    margin: { top: 8, right: 10, bottom: 8, left: 10 },
  },
};

/** Onglet « Arbre familial » : graphe interactif (vis-network). */
@Component({
  selector: 'app-arbre',
  standalone: true,
  imports: [CardModule, MessageModule, ProgressSpinnerModule, TagModule],
  templateUrl: './arbre.component.html',
})
export class ArbreComponent implements AfterViewInit, OnDestroy {
  @ViewChild('conteneur', { static: true }) conteneur!: ElementRef<HTMLDivElement>;

  private api = inject(ApiService);
  private reseau?: Network;
  private detruit = false;

  chargement = true;
  erreur = '';

  ngAfterViewInit(): void {
    this.api.graphe().subscribe({
      next: (graphe) => {
        this.chargement = false;
        if (this.detruit) return;
        const { noeuds, aretes } = versVis(graphe);
        this.reseau = new Network(this.conteneur.nativeElement, { nodes: noeuds, edges: aretes }, OPTIONS);
      },
      error: (err) => {
        this.chargement = false;
        this.erreur = messageErreur(err);
      },
    });
  }

  ngOnDestroy(): void {
    this.detruit = true;
    this.reseau?.destroy();
  }
}
