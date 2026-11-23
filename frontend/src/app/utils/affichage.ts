/**
 * Fonctions d'affichage (textes, couleurs, conversion du graphe pour vis-network).
 * Fonctions pures, testées dans affichage.test.mjs et graphe.test.mjs.
 * Ce fichier n'importe rien d'exécutable : Node peut donc le tester directement.
 */
import type { Graphe } from '../models/api.models';

export function ageTexte(age: number | null): string {
  if (age === null || age === undefined) {
    return '';
  }
  return age <= 1 ? `${age} an` : `${age} ans`;
}

export function symboleSexe(sexe: string): string {
  return sexe === 'F' ? '♀' : '♂';
}

export function classeSexe(sexe: string): string {
  return sexe === 'F' ? 'femme' : 'homme';
}

/** Convertit les données du backend (/api/graphe) en nœuds et arêtes pour vis-network. */

const COULEURS: Record<string, { background: string; border: string }> = {
  M: { background: '#F4EDE0', border: '#14213D' },
  F: { background: '#FF6B5B', border: '#14213D' },
};

export interface NoeudVis {
  id: string;
  label: string;
  level: number;
  shape: string;
  color: { background: string; border: string };
  title: string;
}

export interface AreteVis {
  from: string;
  to: string;
  arrows?: string;
  dashes?: boolean;
  smooth?: boolean;
  width: number;
  color: { color: string };
}

export function versVis(g: Graphe): { noeuds: NoeudVis[]; aretes: AreteVis[] } {
  const noeuds = g.noeuds.map((n) => {
    const age = ageTexte(n.age);
    return {
      id: n.id,
      label: age ? `${n.label}\n${age}` : n.label,
      level: n.niveau,
      shape: 'box',
      color: COULEURS[n.sexe] ?? COULEURS['M'],
      title: age ? `${n.label} (${age})` : n.label,
    };
  });
  const aretes = g.aretes.map((a): AreteVis =>
    a.type === 'mariage'
      ? { from: a.source, to: a.cible, dashes: true, smooth: false, width: 2, color: { color: '#FF6B5B' } }
      : { from: a.source, to: a.cible, arrows: 'to', width: 1, color: { color: '#14213D' } },
  );
  return { noeuds, aretes };
}
