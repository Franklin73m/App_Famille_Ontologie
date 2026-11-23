import test from 'node:test';
import assert from 'node:assert/strict';
import { messageErreur } from './erreurs.ts';

test('API injoignable (status 0)', () => {
  assert.match(messageErreur({ status: 0 }), /Impossible de joindre l'API/);
});

test('message du backend (404 / 400)', () => {
  assert.equal(messageErreur({ status: 404, error: { detail: 'Personne inconnue : X' } }), 'Personne inconnue : X');
});

test('erreur inattendue', () => {
  assert.equal(messageErreur({ status: 500, error: null }), 'Erreur inattendue (code 500).');
  assert.equal(messageErreur(undefined), 'Erreur inattendue.');
});
