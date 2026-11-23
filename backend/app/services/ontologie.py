"""
Lecture de l'ontologie OWL/XML (format de Protégé) avec la bibliothèque standard.

On ne lit que les FAITS de base des individus :
  - leur sexe (classe Masculin ou Feminin),
  - leur âge (propriété de données `age`),
  - leur libellé (rdfs:label),
  - parentDe(parent, enfant),
  - marierA(a, b).
Tous les autres liens (oncle, cousin...) sont déduits par services/relations.py.
Les ajouts de l'application peuvent être lus depuis un fichier OWL complémentaire.
"""
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

OWL = "{http://www.w3.org/2002/07/owl#}"


@dataclass(frozen=True)
class Personne:
    id: str
    nom: str
    sexe: str  # "M" ou "F"
    age: int | None


class Famille:
    """Graphe familial : personnes + faits de base + accès pratiques."""

    def __init__(self, personnes: dict[str, Personne],
                 parente: set[tuple[str, str]], mariages: set[frozenset]):
        self.personnes = personnes
        self._parents = {p: set() for p in personnes}
        self._enfants = {p: set() for p in personnes}
        self._conjoints = {p: set() for p in personnes}
        for parent, enfant in parente:
            self._enfants[parent].add(enfant)
            self._parents[enfant].add(parent)
        for couple in mariages:
            a, b = tuple(couple)
            self._conjoints[a].add(b)
            self._conjoints[b].add(a)

    def parents(self, x: str) -> set[str]:
        return set(self._parents[x])

    def enfants(self, x: str) -> set[str]:
        return set(self._enfants[x])

    def conjoints(self, x: str) -> set[str]:
        return set(self._conjoints[x])

    def fratrie(self, x: str) -> dict[str, str]:
        """Frères et sœurs de x : {id: "complet" | "demi"}.

        Frère/sœur = partage au moins un parent. "complet" si l'ensemble des
        parents connus est identique, "demi" sinon.
        """
        resultat: dict[str, str] = {}
        for p in self._parents[x]:
            for c in self._enfants[p]:
                if c != x:
                    resultat[c] = "complet" if self._parents[c] == self._parents[x] else "demi"
        return resultat

    def existe(self, x: str) -> bool:
        return x in self.personnes

    def niveau(self) -> dict[str, int]:
        """Génération de chaque personne (0 = la plus ancienne), pour dessiner l'arbre.

        Contraintes, appliquées jusqu'à stabilité (les niveaux ne font qu'augmenter) :
          - un enfant est au moins un niveau sous chacun de ses parents ;
          - les époux sont au même niveau ;
          - les deux parents d'un même enfant sont au même niveau.
        """
        niveaux = {x: 0 for x in self.personnes}

        def aligner(groupe: list[str]) -> bool:
            haut = max(niveaux[x] for x in groupe)
            modifie = False
            for x in groupe:
                if niveaux[x] != haut:
                    niveaux[x] = haut
                    modifie = True
            return modifie

        for _ in range(len(self.personnes) + 5):  # borne de sécurité si les données bouclent
            modifie = False
            for x in self.personnes:
                for parent in self._parents[x]:
                    if niveaux[x] < niveaux[parent] + 1:
                        niveaux[x] = niveaux[parent] + 1
                        modifie = True
                for conjoint in self._conjoints[x]:
                    modifie |= aligner([x, conjoint])
                for parent_a in self._parents[x]:
                    for parent_b in self._parents[x]:
                        if parent_a < parent_b:
                            modifie |= aligner([parent_a, parent_b])
            if not modifie:
                break
        return niveaux


def _iri(e: ET.Element) -> str:
    return e.attrib.get("IRI", "").lstrip("#")


def charger_famille(chemin: Path, chemin_ajouts: Path | None = None) -> Famille:
    racines = [ET.parse(chemin).getroot()]
    if chemin_ajouts is not None and chemin_ajouts.exists():
        racines.append(ET.parse(chemin_ajouts).getroot())

    sexes: dict[str, str] = {}
    ages: dict[str, int] = {}
    noms: dict[str, str] = {}
    parente: set[tuple[str, str]] = set()
    mariages: set[frozenset] = set()

    for racine in racines:
        for ax in racine.findall(OWL + "ClassAssertion"):
            classe, individu = _iri(ax[0]), _iri(ax[1])
            if classe == "Masculin":
                sexes[individu] = "M"
            elif classe == "Feminin":
                sexes[individu] = "F"

        for ax in racine.findall(OWL + "DataPropertyAssertion"):
            if _iri(ax[0]) == "age":
                ages[_iri(ax[1])] = int(ax[2].text)

        for ax in racine.findall(OWL + "AnnotationAssertion"):
            if ax[0].attrib.get("abbreviatedIRI") == "rdfs:label":
                noms[ax[1].text.lstrip("#")] = ax[2].text

        for ax in racine.findall(OWL + "ObjectPropertyAssertion"):
            propriete, a, b = _iri(ax[0]), _iri(ax[1]), _iri(ax[2])
            if propriete == "parentDe":
                parente.add((a, b))
            elif propriete == "marierA":
                mariages.add(frozenset((a, b)))

    personnes = {
        pid: Personne(id=pid, nom=noms.get(pid, pid), sexe=sexe, age=ages.get(pid))
        for pid, sexe in sorted(sexes.items())
    }
    # Contrôle de cohérence minimal : toute relation doit viser une personne connue
    for a, b in parente:
        if a not in personnes or b not in personnes:
            raise ValueError(f"parentDe({a}, {b}) : individu sans sexe déclaré")
    for couple in mariages:
        if not all(x in personnes for x in couple):
            raise ValueError(f"marierA{tuple(couple)} : individu sans sexe déclaré")
    return Famille(personnes, parente, mariages)
