/** Transforme une erreur HTTP en message lisible. Fonction pure, testée dans erreurs.test.mjs. */
interface ErreurHttp {
  status?: number;
  error?: { detail?: unknown } | null;
}

export function messageErreur(err: unknown): string {
  const e = (err ?? {}) as ErreurHttp;
  if (e.status === 0) {
    return "Impossible de joindre l'API. Vérifiez que le backend est lancé " +
      "(uvicorn app.main:app --reload) sur http://localhost:8000.";
  }
  const detail = e.error && typeof e.error === 'object' ? e.error.detail : undefined;
  if (typeof detail === 'string') {
    return detail;
  }
  return e.status ? `Erreur inattendue (code ${e.status}).` : 'Erreur inattendue.';
}
