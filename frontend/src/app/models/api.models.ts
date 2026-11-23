/** Formes des données JSON renvoyées par le backend (miroir de backend/app/schemas/modeles.py). */

export interface Personne {
  id: string;
  nom: string;
  sexe: string; // "M" ou "F"
  age: number | null;
}

export type RelationCreation = 'parent' | 'enfant' | 'conjoint';

export interface PersonneCreation {
  nom: string;
  sexe: 'M' | 'F';
  age: number | null;
  personne_liee_id: string;
  relation: RelationCreation;
}

export interface Lien {
  libelle: string;
  precision: string;
  phrase: string;
}

export interface Membre extends Personne {
  liens: Lien[];
}

export interface Famille {
  personne: Personne;
  membres: Membre[];
}

export interface LienEntre {
  a: Personne;
  b: Personne;
  a_vers_b: Lien[];
  b_vers_a: Lien[];
  resume: string;
}

export interface Noeud {
  id: string;
  label: string;
  sexe: string;
  age: number | null;
  niveau: number;
}

export interface Arete {
  source: string;
  cible: string;
  type: string; // "parent" ou "mariage"
}

export interface Graphe {
  noeuds: Noeud[];
  aretes: Arete[];
}
