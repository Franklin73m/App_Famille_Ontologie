"""
Calcul des liens familiaux à partir des faits de base (parentDe, marierA, sexe).

Convention : liens(f, a, b) renvoie les liens de la forme « a est <lien> de b ».
Exemple : liens(f, "Koffi", "Mawuli") -> [Lien("Père")]  (Koffi est le père de Mawuli)

Les définitions suivent les classes de l'ontologie (Oncle, Cousin, Neveu, BeauPere,
DemiFrere...). Le détail est dans docs/ontologie.md.
"""
from dataclasses import dataclass

from .ontologie import Famille


@dataclass(frozen=True)
class Lien:
    libelle: str          # "Père", "Demi-sœur", "Oncle"...
    precision: str = ""   # "par alliance", "remariage"...
    rang: int = 0         # sert à trier : proches d'abord


def _etendre(f: Famille, ids, fonction) -> set[str]:
    """Applique `fonction` (id -> ensemble d'ids) à chaque id et réunit les résultats."""
    resultat: set[str] = set()
    for i in ids:
        resultat |= fonction(i)
    return resultat


def liens(f: Famille, a: str, b: str) -> list[Lien]:
    """Tous les liens « a est ___ de b ». Liste vide si aucun lien (ou si a == b)."""
    if a == b:
        return []
    m = f.personnes[a].sexe == "M"
    resultat: list[Lien] = []

    def ajouter(rang, masc, fem, precision=""):
        lien = Lien(masc if m else fem, precision, rang)
        if lien not in resultat:
            resultat.append(lien)

    parents_b = f.parents(b)
    grands_parents = _etendre(f, parents_b, f.parents)
    arr_grands_parents = _etendre(f, grands_parents, f.parents)
    enfants_b = f.enfants(b)
    petits_enfants = _etendre(f, enfants_b, f.enfants)
    arr_petits_enfants = _etendre(f, petits_enfants, f.enfants)
    conjoints_b = f.conjoints(b)
    fratrie_b = f.fratrie(b)

    # --- ligne directe -------------------------------------------------------
    if a in parents_b:
        ajouter(10, "Père", "Mère")
    if a in enfants_b:
        ajouter(10, "Fils", "Fille")
    if a in conjoints_b:
        ajouter(5, "Époux", "Épouse")
    if a in grands_parents:
        ajouter(20, "Grand-père", "Grand-mère")
    if a in petits_enfants:
        ajouter(20, "Petit-fils", "Petite-fille")
    if a in arr_grands_parents:
        ajouter(30, "Arrière-grand-père", "Arrière-grand-mère")
    if a in arr_petits_enfants:
        ajouter(30, "Arrière-petit-fils", "Arrière-petite-fille")

    # --- fratrie ---------------------------------------------------------------
    if a in fratrie_b:
        if fratrie_b[a] == "complet":
            ajouter(15, "Frère", "Sœur")
        else:
            ajouter(16, "Demi-frère", "Demi-sœur")

    # --- oncles / tantes, neveux / nièces, cousins -----------------------------
    freres_des_parents = _etendre(f, parents_b, _fratrie_ids_fn(f))
    if a in freres_des_parents and a not in parents_b:
        ajouter(40, "Oncle", "Tante")
    else:
        conjoints_de_ces_oncles = _etendre(f, freres_des_parents, f.conjoints)
        if a in conjoints_de_ces_oncles and a not in parents_b:
            ajouter(41, "Oncle", "Tante", "par alliance")

    enfants_de_la_fratrie = _etendre(f, fratrie_b, f.enfants)
    if a in enfants_de_la_fratrie:
        ajouter(40, "Neveu", "Nièce")
    else:
        fratrie_des_conjoints = _etendre(f, conjoints_b, _fratrie_ids_fn(f))
        if a in _etendre(f, fratrie_des_conjoints, f.enfants):
            ajouter(41, "Neveu", "Nièce", "par alliance")

    if a in _etendre(f, freres_des_parents, f.enfants):
        ajouter(50, "Cousin", "Cousine")

    # --- belle-famille -----------------------------------------------------------
    if a in _etendre(f, parents_b, f.conjoints) and a not in parents_b:
        ajouter(60, "Beau-père", "Belle-mère", "remariage d'un parent")
    if a in _etendre(f, conjoints_b, f.parents):
        ajouter(61, "Beau-père", "Belle-mère", "parent du conjoint")
    if a in _etendre(f, conjoints_b, f.enfants) and a not in enfants_b:
        ajouter(62, "Beau-fils", "Belle-fille", "enfant du conjoint")
    if a in _etendre(f, enfants_b, f.conjoints):
        ajouter(63, "Gendre", "Belle-fille", "conjoint(e) de l'enfant")
    beaux_freres = _etendre(f, conjoints_b, _fratrie_ids_fn(f)) \
        | _etendre(f, fratrie_b, f.conjoints)
    if a in beaux_freres:
        ajouter(64, "Beau-frère", "Belle-sœur")

    return sorted(resultat, key=lambda l: l.rang)


def _fratrie_ids_fn(f: Famille):
    return lambda x: set(f.fratrie(x))


# --------------------------------------------------------------- phrases en français
def _article(libelle: str, masculin: bool) -> str:
    if libelle[0].lower() in "aeiouéèêâhî":
        return "l'"
    return "le " if masculin else "la "


def phrase(f: Famille, a: str, b: str, lien: Lien) -> str:
    """Ex. : « Koffi est le père de Mawuli » ou « Afi est la belle-mère de Fabrice (remariage d'un parent) »."""
    masculin = f.personnes[a].sexe == "M"
    nom = lien.libelle[0].lower() + lien.libelle[1:]
    cible = f.personnes[b].nom
    de = "d'" if cible[0].lower() in "aeiouyéèêâîô" else "de "
    texte = f"{f.personnes[a].nom} est {_article(lien.libelle, masculin)}{nom} {de}{cible}"
    return texte + (f" ({lien.precision})" if lien.precision else "")


def famille_de(f: Famille, x: str) -> list[tuple[str, list[Lien]]]:
    """Tous les parents de x : [(id, [liens « id est ___ de x »])], triés des plus proches aux plus éloignés."""
    membres = [(y, liens(f, y, x)) for y in f.personnes if y != x]
    membres = [(y, ls) for y, ls in membres if ls]
    membres.sort(key=lambda t: (t[1][0].rang, f.personnes[t[0]].nom))
    return membres
