import test from 'node:test';
import assert from 'node:assert/strict';
import { ageTexte, symboleSexe, classeSexe } from './affichage.ts';

test('ageTexte', () => {
  assert.equal(ageTexte(30), '30 ans');
  assert.equal(ageTexte(1), '1 an');
  assert.equal(ageTexte(0), '0 an');
  assert.equal(ageTexte(null), '');
});

test('sexe', () => {
  assert.equal(symboleSexe('F'), '♀');
  assert.equal(symboleSexe('M'), '♂');
  assert.equal(classeSexe('F'), 'femme');
  assert.equal(classeSexe('M'), 'homme');
});
