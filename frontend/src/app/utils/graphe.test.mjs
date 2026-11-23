import test from 'node:test';
import assert from 'node:assert/strict';
import { versVis } from './affichage.ts';

const g = {
  noeuds: [
    { id: 'A', label: 'Anna', sexe: 'F', age: 40, niveau: 0 },
    { id: 'B', label: 'Bob', sexe: 'M', age: null, niveau: 1 },
  ],
  aretes: [
    { source: 'A', cible: 'B', type: 'parent' },
    { source: 'A', cible: 'B', type: 'mariage' },
  ],
};

test('noeuds : libellé, niveau, couleur', () => {
  const { noeuds } = versVis(g);
  assert.equal(noeuds[0].label, 'Anna\n40 ans');
  assert.equal(noeuds[0].level, 0);
  assert.equal(noeuds[0].color.background, '#FF6B5B');
  assert.equal(noeuds[0].color.border, '#14213D');
  assert.equal(noeuds[1].label, 'Bob');
  assert.equal(noeuds[1].color.background, '#F4EDE0');
  assert.equal(noeuds[1].color.border, '#14213D');
});

test('arêtes : parent = flèche, mariage = pointillés sans flèche', () => {
  const { aretes } = versVis(g);
  assert.equal(aretes[0].arrows, 'to');
  assert.equal(aretes[0].dashes, undefined);
  assert.equal(aretes[1].dashes, true);
  assert.equal(aretes[1].arrows, undefined);
  assert.equal(aretes[1].color.color, '#FF6B5B');
  assert.equal(aretes[0].color.color, '#14213D');
});
