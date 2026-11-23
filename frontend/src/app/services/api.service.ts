import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_URL } from '../config';
import { Famille, Graphe, LienEntre, Personne, PersonneCreation } from '../models/api.models';

/** Tous les appels HTTP vers le backend passent par ce service. */
@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  personnes(): Observable<Personne[]> {
    return this.http.get<Personne[]>(`${API_URL}/personnes`);
  }

  creerPersonne(personne: PersonneCreation): Observable<Personne> {
    return this.http.post<Personne>(`${API_URL}/personnes`, personne);
  }

  famille(id: string): Observable<Famille> {
    return this.http.get<Famille>(`${API_URL}/personnes/${encodeURIComponent(id)}/famille`);
  }

  lien(a: string, b: string): Observable<LienEntre> {
    return this.http.get<LienEntre>(`${API_URL}/lien`, { params: { a, b } });
  }

  graphe(): Observable<Graphe> {
    return this.http.get<Graphe>(`${API_URL}/graphe`);
  }
}
