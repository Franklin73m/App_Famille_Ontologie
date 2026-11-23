"""
Construit ontology/famille.owl à partir de l'ontologie originale (v0).

Étapes :
  1. Corrige les défauts de l'ontologie originale (voir docs/ontologie.md, section "Corrections").
  2. Ajoute les individus de la famille d'exemple.

Usage (depuis la racine du projet) :
    python tools/construire_ontologie.py

Le script est reproductible : le relancer régénère famille.owl à l'identique.
Aucune dépendance externe (bibliothèque standard Python uniquement).
"""
import copy
import xml.etree.ElementTree as ET
from pathlib import Path

OWL = "http://www.w3.org/2002/07/owl#"
XSD = "http://www.w3.org/2001/XMLSchema#"
ET.register_namespace("", OWL)

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "ontology" / "versions" / "famille_v0_original.owl"
CIBLE = RACINE / "ontology" / "famille.owl"


# ------------------------------------------------------------ petits outils XML
def q(tag):
    return f"{{{OWL}}}{tag}"


def el(tag, attrs=None, *enfants, texte=None):
    e = ET.Element(q(tag), attrs or {})
    for c in enfants:
        e.append(c)
    if texte is not None:
        e.text = texte
    return e


def cls(nom): return el("Class", {"IRI": "#" + nom})
def op(nom): return el("ObjectProperty", {"IRI": "#" + nom})
def dp(nom): return el("DataProperty", {"IRI": "#" + nom})
def ind(nom): return el("NamedIndividual", {"IRI": "#" + nom})
def inter(*parties): return el("ObjectIntersectionOf", None, *parties)


def iri_de(e):
    return e.attrib.get("IRI", "").lstrip("#")


def entier(valeur):
    return el("Literal", {"datatypeIRI": XSD + "integer"}, texte=str(valeur))


def seuil_age(facette, valeur):
    """age a une valeur entière vérifiant la facette (minInclusive / maxExclusive)."""
    return el(
        "DataSomeValuesFrom", None, dp("age"),
        el("DatatypeRestriction", None,
           el("Datatype", {"abbreviatedIRI": "xsd:integer"}),
           el("FacetRestriction", {"facet": XSD + facette}, entier(valeur))),
    )


def equivalence_de(racine, nom):
    for ax in racine.findall(q("EquivalentClasses")):
        if ax[0].tag == q("Class") and iri_de(ax[0]) == nom:
            return ax
    return None


def remplacer_equivalence(racine, nom, definition):
    ancien = equivalence_de(racine, nom)
    if ancien is not None:
        racine.remove(ancien)
    racine.append(el("EquivalentClasses", None, cls(nom), definition))


# ------------------------------------------------------------------ corrections
PROPRIETES_NUMEROTEES = {
    "parentDe1", "parentDe2", "parentDe3",
    "enfantDe1", "enfantDe2", "enfantDe3",
    "marierA1", "marierA2", "marierA3", "marierA4",
}


def corriger(racine):
    # C1 : définition circulaire Parent <-> Enfant
    for nom, fautif in (("Parent", "Enfant"), ("Enfant", "Parent")):
        for e in equivalence_de(racine, nom).iter(q("Class")):
            if iri_de(e) == fautif:
                e.set("IRI", "#Personne")

    # C2 + C3 : grandParentDe n'est ni sous-propriété de parentDe,
    #           ni inverse-fonctionnelle ; on la déduit par une chaîne.
    for ax in list(racine):
        if ax.tag in (q("SubObjectPropertyOf"), q("InverseFunctionalObjectProperty")) \
                and ax[0].tag == q("ObjectProperty") and iri_de(ax[0]) == "grandParentDe":
            racine.remove(ax)
    racine.append(el("SubObjectPropertyOf", None,
                     el("ObjectPropertyChain", None, op("parentDe"), op("parentDe")),
                     op("grandParentDe")))

    # C4 : frereDe / soeurDe ne sont pas transitives
    for ax in racine.findall(q("TransitiveObjectProperty")):
        racine.remove(ax)

    # C5 : Masculin et Feminin sont disjoints
    racine.append(el("DisjointClasses", None, cls("Masculin"), cls("Feminin")))

    # C6 : un neveu n'est pas un fils, une nièce n'est pas une fille
    for ax in racine.findall(q("SubClassOf")):
        if ax[0].tag == q("Class") and iri_de(ax[0]) in ("Neuveu", "Niece") \
                and iri_de(ax[1]) in ("Fils", "Fille"):
            racine.remove(ax)

    # C7 : seuils d'âge (adulte >= 18, mineur < 18)
    adulte, mineur = seuil_age("minInclusive", 18), seuil_age("maxExclusive", 18)
    remplacer_equivalence(racine, "Homme", inter(cls("Masculin"), cls("Personne"), copy.deepcopy(adulte)))
    remplacer_equivalence(racine, "Femme", inter(cls("Feminin"), cls("Personne"), copy.deepcopy(adulte)))
    remplacer_equivalence(racine, "Garcon", inter(cls("Masculin"), cls("Personne"), copy.deepcopy(mineur)))
    remplacer_equivalence(racine, "Fillette", inter(cls("Feminin"), cls("Personne"), copy.deepcopy(mineur)))

    # C8 : suppression des propriétés numérotées (et de tous leurs axiomes)
    for ax in list(racine):
        if ax.tag != q("Prefix") and any(iri_de(x) in PROPRIETES_NUMEROTEES for x in ax.iter()):
            racine.remove(ax)

    # C9 : DemiFrere / DemiSoeur : définitions mal formées -> simples sous-classes
    for nom in ("DemiFrere", "DemiSoeur"):
        ax = equivalence_de(racine, nom)
        if ax is not None:
            racine.remove(ax)

    # C10 : faute de frappe Neuveu -> Neveu
    for e in racine.iter():
        if e.attrib.get("IRI") == "#Neuveu":
            e.set("IRI", "#Neveu")

    # Caractéristiques des propriétés
    racine.append(el("SymmetricObjectProperty", None, op("marierA")))
    racine.append(el("IrreflexiveObjectProperty", None, op("marierA")))
    racine.append(el("AsymmetricObjectProperty", None, op("parentDe")))
    for p in ("parentDe", "enfantDe", "marierA", "frereDe", "soeurDe", "grandParentDe"):
        racine.append(el("ObjectPropertyDomain", None, op(p), cls("Personne")))
        racine.append(el("ObjectPropertyRange", None, op(p), cls("Personne")))


# -------------------------------------------------------------------- individus
# (identifiant, libellé affiché, sexe, âge)
PERSONNES = [
    ("Dossou", "Dossou", "M", 84), ("Adjoa", "Adjoa", "F", 80),
    ("Koffi", "Koffi", "M", 58), ("Ayaba", "Ayaba", "F", 56),
    ("Afi", "Afi", "F", 55), ("Roland", "Roland", "M", 57),
    ("Sena", "Sena", "M", 52), ("Esther", "Esther", "F", 50),
    ("Ablavi", "Ablavi", "F", 60),
    ("Mawuli", "Mawuli", "M", 30), ("Nadege", "Nadège", "F", 29),
    ("Edem", "Edem", "F", 27),
    ("Yawa", "Yawa", "F", 29), ("Prosper", "Prosper", "M", 31),
    ("Kossi", "Kossi", "M", 25),
    ("Fabrice", "Fabrice", "M", 34), ("Carine", "Carine", "F", 33),
    ("Gilles", "Gilles", "M", 22), ("Amavi", "Amavi", "F", 19),
    ("Selom", "Selom", "M", 4), ("Ama", "Ama", "F", 2),
    ("Daniel", "Daniel", "M", 8),
]

# (parent, enfant)
PARENTE = [
    ("Dossou", "Koffi"), ("Adjoa", "Koffi"),
    ("Dossou", "Afi"), ("Adjoa", "Afi"),
    ("Dossou", "Sena"), ("Adjoa", "Sena"),
    ("Koffi", "Mawuli"), ("Ayaba", "Mawuli"),
    ("Koffi", "Edem"), ("Ayaba", "Edem"),
    ("Afi", "Yawa"), ("Roland", "Yawa"),
    ("Afi", "Kossi"), ("Roland", "Kossi"),
    ("Roland", "Fabrice"), ("Ablavi", "Fabrice"),
    ("Sena", "Gilles"), ("Esther", "Gilles"),
    ("Sena", "Amavi"), ("Esther", "Amavi"),
    ("Mawuli", "Selom"), ("Nadege", "Selom"),
    ("Yawa", "Ama"), ("Prosper", "Ama"),
    ("Fabrice", "Daniel"), ("Carine", "Daniel"),
]

# couples mariés (une seule direction : marierA est symétrique)
MARIAGES = [
    ("Dossou", "Adjoa"), ("Koffi", "Ayaba"), ("Roland", "Afi"),
    ("Sena", "Esther"), ("Mawuli", "Nadege"), ("Prosper", "Yawa"),
    ("Fabrice", "Carine"),
]


def ajouter_individus(racine):
    for pid, *_ in PERSONNES:
        racine.append(el("Declaration", None, ind(pid)))
    for pid, label, sexe, age in PERSONNES:
        racine.append(el("ClassAssertion", None, cls("Personne"), ind(pid)))
        racine.append(el("ClassAssertion", None,
                         cls("Masculin" if sexe == "M" else "Feminin"), ind(pid)))
        racine.append(el("DataPropertyAssertion", None, dp("age"), ind(pid), entier(age)))
        racine.append(el("AnnotationAssertion", None,
                         el("AnnotationProperty", {"abbreviatedIRI": "rdfs:label"}),
                         el("IRI", None, texte="#" + pid),
                         el("Literal", texte=label)))
    for p, e in PARENTE:
        racine.append(el("ObjectPropertyAssertion", None, op("parentDe"), ind(p), ind(e)))
    for a, b in MARIAGES:
        racine.append(el("ObjectPropertyAssertion", None, op("marierA"), ind(a), ind(b)))


def main():
    arbre = ET.parse(SOURCE)
    racine = arbre.getroot()
    corriger(racine)
    ajouter_individus(racine)
    ET.indent(arbre, space="    ")
    arbre.write(CIBLE, encoding="UTF-8", xml_declaration=True)
    print(f"OK : {CIBLE.relative_to(RACINE)} généré ({len(PERSONNES)} personnes, "
          f"{len(PARENTE)} liens de parenté, {len(MARIAGES)} mariages).")


if __name__ == "__main__":
    main()
