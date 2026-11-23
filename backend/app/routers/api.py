"""Endpoints REST. Tous sont préfixés par /api (voir main.py)."""
import re
import unicodedata
from functools import lru_cache
from threading import RLock

from fastapi import APIRouter, HTTPException, Query, status

from ..config import CHEMIN_AJOUTS_ONTOLOGIE, CHEMIN_ONTOLOGIE
from ..schemas.modeles import (AreteOut, FamilleOut, GrapheOut, LienEntreOut,
                               LienOut, MembreOut, NoeudOut, PersonneCreationIn,
                               PersonneOut)
from ..services import relations
from ..services.ecriture_ontologie import enregistrer_personne
from ..services.ontologie import Famille, Personne, charger_famille

router = APIRouter()
_verrou_ecriture = RLock()


@lru_cache(maxsize=1)
def obtenir_famille() -> Famille:
    """L'ontologie est lue une seule fois, au premier appel."""
    with _verrou_ecriture:
        return charger_famille(CHEMIN_ONTOLOGIE, CHEMIN_AJOUTS_ONTOLOGIE)


def _personne(p: Personne) -> PersonneOut:
    return PersonneOut(id=p.id, nom=p.nom, sexe=p.sexe, age=p.age)


def _verifier(f: Famille, *ids: str) -> None:
    for i in ids:
        if not f.existe(i):
            raise HTTPException(status_code=404, detail=f"Personne inconnue : {i}")


def _liens_out(f: Famille, a: str, b: str) -> list[LienOut]:
    return [LienOut(libelle=l.libelle, precision=l.precision, phrase=relations.phrase(f, a, b, l))
            for l in relations.liens(f, a, b)]


@router.get("/sante", summary="Vérifie que l'API fonctionne")
def sante():
    f = obtenir_famille()
    return {"statut": "ok", "personnes": len(f.personnes)}


@router.get("/personnes", response_model=list[PersonneOut], summary="Liste de toutes les personnes")
def lister_personnes():
    f = obtenir_famille()
    return [_personne(p) for p in sorted(f.personnes.values(), key=lambda p: p.nom)]


def _identifiant_unique(nom: str, existants: set[str]) -> str:
    ascii_nom = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^a-z0-9]+", "-", ascii_nom.casefold()).strip("-") or "personne"
    identifiant = base
    suffixe = 2
    while identifiant in existants:
        identifiant = f"{base}-{suffixe}"
        suffixe += 1
    return identifiant


@router.post("/personnes", response_model=PersonneOut, status_code=status.HTTP_201_CREATED,
             summary="Crée une personne et la rattache à un membre existant")
def creer_personne(donnees: PersonneCreationIn):
    with _verrou_ecriture:
        f = obtenir_famille()
        _verifier(f, donnees.personne_liee_id)
        personne = Personne(
            id=_identifiant_unique(donnees.nom, set(f.personnes)),
            nom=donnees.nom,
            sexe=donnees.sexe,
            age=donnees.age,
        )
        enregistrer_personne(
            CHEMIN_ONTOLOGIE,
            CHEMIN_AJOUTS_ONTOLOGIE,
            personne,
            donnees.relation,
            donnees.personne_liee_id,
        )
        obtenir_famille.cache_clear()
    return _personne(personne)


@router.get("/personnes/{personne_id}/famille", response_model=FamilleOut,
            summary="Toute la famille d'une personne, avec le lien de chacun")
def famille_d_une_personne(personne_id: str):
    f = obtenir_famille()
    _verifier(f, personne_id)
    membres = [
        MembreOut(**_personne(f.personnes[y]).model_dump(), liens=_liens_out(f, y, personne_id))
        for y, _ in relations.famille_de(f, personne_id)
    ]
    return FamilleOut(personne=_personne(f.personnes[personne_id]), membres=membres)


@router.get("/lien", response_model=LienEntreOut, summary="Lien entre deux personnes")
def lien_entre(a: str = Query(..., description="id de la première personne"),
               b: str = Query(..., description="id de la seconde personne")):
    f = obtenir_famille()
    _verifier(f, a, b)
    if a == b:
        raise HTTPException(status_code=400, detail="Choisissez deux personnes différentes.")
    a_vers_b, b_vers_a = _liens_out(f, a, b), _liens_out(f, b, a)
    if a_vers_b:
        resume = " ; ".join(l.phrase for l in a_vers_b)
    else:
        resume = (f"Aucun lien familial direct n'a été trouvé entre "
                  f"{f.personnes[a].nom} et {f.personnes[b].nom}.")
    return LienEntreOut(a=_personne(f.personnes[a]), b=_personne(f.personnes[b]),
                        a_vers_b=a_vers_b, b_vers_a=b_vers_a, resume=resume)


@router.get("/graphe", response_model=GrapheOut, summary="Données pour dessiner l'arbre familial")
def graphe():
    f = obtenir_famille()
    niveaux = f.niveau()
    noeuds = [NoeudOut(id=p.id, label=p.nom, sexe=p.sexe, age=p.age, niveau=niveaux[p.id])
              for p in f.personnes.values()]
    aretes = [AreteOut(source=parent, cible=enfant, type="parent")
              for enfant in f.personnes for parent in sorted(f.parents(enfant))]
    vus = set()
    for x in f.personnes:
        for c in f.conjoints(x):
            couple = tuple(sorted((x, c)))
            if couple not in vus:
                vus.add(couple)
                aretes.append(AreteOut(source=couple[0], cible=couple[1], type="mariage"))
    return GrapheOut(noeuds=noeuds, aretes=aretes)
