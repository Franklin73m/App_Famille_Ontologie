"""Modèles Pydantic pour les requêtes et réponses JSON de l'API."""
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PersonneCreationIn(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    sexe: Literal["M", "F"]
    age: int | None = Field(default=None, ge=0, le=130)
    personne_liee_id: str = Field(min_length=1)
    relation: Literal["parent", "enfant", "conjoint"]

    @field_validator("nom", "personne_liee_id")
    @classmethod
    def champs_non_vides(cls, valeur: str) -> str:
        valeur = valeur.strip()
        if not valeur:
            raise ValueError("Ce champ ne peut pas être vide.")
        return valeur


class PersonneOut(BaseModel):
    id: str
    nom: str
    sexe: str            # "M" ou "F"
    age: int | None = None


class LienOut(BaseModel):
    libelle: str         # "Père", "Cousine"...
    precision: str = ""  # "par alliance", "remariage d'un parent"...
    phrase: str          # "Koffi est le père de Mawuli"


class MembreOut(PersonneOut):
    liens: list[LienOut]  # liens « ce membre est ___ de la personne choisie »


class FamilleOut(BaseModel):
    personne: PersonneOut
    membres: list[MembreOut]


class LienEntreOut(BaseModel):
    a: PersonneOut
    b: PersonneOut
    a_vers_b: list[LienOut]   # « a est ___ de b »
    b_vers_a: list[LienOut]   # « b est ___ de a »
    resume: str               # phrase de synthèse prête à afficher


class NoeudOut(BaseModel):
    id: str
    label: str
    sexe: str
    age: int | None = None
    niveau: int               # génération (0 = plus ancienne)


class AreteOut(BaseModel):
    source: str
    cible: str
    type: str                 # "parent" (source parent de cible) ou "mariage"


class GrapheOut(BaseModel):
    noeuds: list[NoeudOut]
    aretes: list[AreteOut]
