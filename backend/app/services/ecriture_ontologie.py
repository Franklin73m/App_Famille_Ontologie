"""Écriture atomique des personnes ajoutées par l'application dans un OWL complémentaire."""
from copy import deepcopy
from pathlib import Path
import os
import tempfile
import xml.etree.ElementTree as ET
from typing import Literal

from .ontologie import Personne

OWL_URI = "http://www.w3.org/2002/07/owl#"
OWL = "{" + OWL_URI + "}"
XML_BASE = "{http://www.w3.org/XML/1998/namespace}base"
RDFS_URI = "http://www.w3.org/2000/01/rdf-schema#"
XSD_URI = "http://www.w3.org/2001/XMLSchema#"


def _nouvelle_ontologie(chemin_base: Path) -> ET.Element:
    racine_base = ET.parse(chemin_base).getroot()
    base_iri = racine_base.attrib.get(XML_BASE) or racine_base.attrib.get("ontologyIRI", "")
    attributs = {XML_BASE: base_iri} if base_iri else {}
    if base_iri:
        attributs["ontologyIRI"] = base_iri.rstrip("/") + "/ajouts"
    racine = ET.Element(OWL + "Ontology", attributs)
    for prefixe in racine_base.findall(OWL + "Prefix"):
        racine.append(deepcopy(prefixe))
    if not any(prefixe.attrib.get("name") == "rdfs" for prefixe in racine.findall(OWL + "Prefix")):
        ET.SubElement(racine, OWL + "Prefix", {"name": "rdfs", "IRI": RDFS_URI})
    return racine


def enregistrer_personne(
    chemin_base: Path,
    chemin_ajouts: Path,
    personne: Personne,
    relation: Literal["parent", "enfant", "conjoint"],
    personne_liee_id: str,
) -> None:
    """Ajoute l'individu et son lien à l'OWL complémentaire, sans réécrire l'ontologie source."""
    if relation not in {"parent", "enfant", "conjoint"}:
        raise ValueError(f"Relation non prise en charge : {relation}")

    ET.register_namespace("", OWL_URI)
    if chemin_ajouts.exists():
        racine = ET.parse(chemin_ajouts).getroot()
        if racine.tag != OWL + "Ontology":
            raise ValueError(f"Le fichier d'ajouts n'est pas une ontologie OWL valide : {chemin_ajouts}")
    else:
        racine = _nouvelle_ontologie(chemin_base)

    individu = ET.SubElement(racine, OWL + "Declaration")
    ET.SubElement(individu, OWL + "NamedIndividual", {"IRI": f"#{personne.id}"})

    for classe in ("Personne", "Masculin" if personne.sexe == "M" else "Feminin"):
        assertion = ET.SubElement(racine, OWL + "ClassAssertion")
        ET.SubElement(assertion, OWL + "Class", {"IRI": f"#{classe}"})
        ET.SubElement(assertion, OWL + "NamedIndividual", {"IRI": f"#{personne.id}"})

    if personne.age is not None:
        assertion = ET.SubElement(racine, OWL + "DataPropertyAssertion")
        ET.SubElement(assertion, OWL + "DataProperty", {"IRI": "#age"})
        ET.SubElement(assertion, OWL + "NamedIndividual", {"IRI": f"#{personne.id}"})
        ET.SubElement(
            assertion,
            OWL + "Literal",
            {"datatypeIRI": XSD_URI + "integer"},
        ).text = str(personne.age)

    assertion = ET.SubElement(racine, OWL + "AnnotationAssertion")
    ET.SubElement(assertion, OWL + "AnnotationProperty", {"abbreviatedIRI": "rdfs:label"})
    ET.SubElement(assertion, OWL + "IRI").text = f"#{personne.id}"
    ET.SubElement(assertion, OWL + "Literal").text = personne.nom

    if relation == "parent":
        source, cible, propriete = personne.id, personne_liee_id, "parentDe"
    elif relation == "enfant":
        source, cible, propriete = personne_liee_id, personne.id, "parentDe"
    else:
        source, cible, propriete = personne.id, personne_liee_id, "marierA"

    assertion = ET.SubElement(racine, OWL + "ObjectPropertyAssertion")
    ET.SubElement(assertion, OWL + "ObjectProperty", {"IRI": f"#{propriete}"})
    ET.SubElement(assertion, OWL + "NamedIndividual", {"IRI": f"#{source}"})
    ET.SubElement(assertion, OWL + "NamedIndividual", {"IRI": f"#{cible}"})

    arbre = ET.ElementTree(racine)
    ET.indent(arbre, space="    ")
    chemin_ajouts.parent.mkdir(parents=True, exist_ok=True)
    chemin_temporaire: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=chemin_ajouts.parent,
            prefix=chemin_ajouts.name + ".",
            suffix=".tmp",
            delete=False,
        ) as fichier:
            chemin_temporaire = Path(fichier.name)
            arbre.write(fichier, encoding="utf-8", xml_declaration=True)
        os.replace(chemin_temporaire, chemin_ajouts)
        chemin_temporaire = None
    finally:
        if chemin_temporaire is not None and chemin_temporaire.exists():
            chemin_temporaire.unlink()
