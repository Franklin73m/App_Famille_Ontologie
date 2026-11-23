"""
Tests du moteur de relations sur la famille d'exemple (ontology/famille.owl).
Lancer depuis backend/ :   python -m unittest discover -s tests -v     (ou : pytest)
"""
import unittest

from app.config import CHEMIN_ONTOLOGIE
from app.services.ontologie import charger_famille
from app.services.relations import famille_de, liens, phrase

F = charger_famille(CHEMIN_ONTOLOGIE)


def libelles(a, b):
    return [(l.libelle + (f" ({l.precision})" if l.precision else "")) for l in liens(F, a, b)]


class TestChargement(unittest.TestCase):
    def test_nombre_de_personnes(self):
        self.assertEqual(len(F.personnes), 22)

    def test_faits_de_base(self):
        self.assertEqual(F.personnes["Nadege"].nom, "Nadège")
        self.assertEqual(F.personnes["Koffi"].sexe, "M")
        self.assertEqual(F.personnes["Edem"].age, 27)
        self.assertEqual(F.parents("Mawuli"), {"Koffi", "Ayaba"})
        self.assertEqual(F.conjoints("Dossou"), {"Adjoa"})

    def test_mariage_symetrique(self):
        for p in F.personnes:
            for c in F.conjoints(p):
                self.assertIn(p, F.conjoints(c))


class TestLiensDirects(unittest.TestCase):
    def test_pere_mere(self):
        self.assertEqual(libelles("Koffi", "Mawuli"), ["Père"])
        self.assertEqual(libelles("Ayaba", "Mawuli"), ["Mère"])

    def test_fils_fille(self):
        self.assertEqual(libelles("Mawuli", "Koffi"), ["Fils"])
        self.assertEqual(libelles("Edem", "Koffi"), ["Fille"])

    def test_epoux(self):
        self.assertEqual(libelles("Dossou", "Adjoa"), ["Époux"])
        self.assertEqual(libelles("Adjoa", "Dossou"), ["Épouse"])

    def test_grands_parents_et_arriere(self):
        self.assertEqual(libelles("Dossou", "Mawuli"), ["Grand-père"])
        self.assertEqual(libelles("Adjoa", "Yawa"), ["Grand-mère"])
        self.assertEqual(libelles("Mawuli", "Dossou"), ["Petit-fils"])
        self.assertEqual(libelles("Dossou", "Selom"), ["Arrière-grand-père"])
        self.assertEqual(libelles("Ama", "Adjoa"), ["Arrière-petite-fille"])


class TestFratrie(unittest.TestCase):
    def test_frere_soeur(self):
        self.assertEqual(libelles("Mawuli", "Edem"), ["Frère"])
        self.assertEqual(libelles("Edem", "Mawuli"), ["Sœur"])
        self.assertEqual(libelles("Koffi", "Afi"), ["Frère"])

    def test_demi_frere(self):
        self.assertEqual(libelles("Fabrice", "Yawa"), ["Demi-frère"])
        self.assertEqual(libelles("Yawa", "Fabrice"), ["Demi-sœur"])
        self.assertEqual(libelles("Kossi", "Fabrice"), ["Demi-frère"])

    def test_pas_de_fratrie_avec_soi_meme(self):
        self.assertEqual(liens(F, "Koffi", "Koffi"), [])


class TestFamilleElargie(unittest.TestCase):
    def test_oncle_tante(self):
        self.assertEqual(libelles("Sena", "Mawuli"), ["Oncle"])
        self.assertEqual(libelles("Afi", "Edem"), ["Tante"])

    def test_oncle_tante_par_alliance(self):
        self.assertEqual(libelles("Esther", "Mawuli"), ["Tante (par alliance)"])
        self.assertEqual(libelles("Roland", "Gilles"), ["Oncle (par alliance)"])

    def test_neveu_niece(self):
        self.assertEqual(libelles("Mawuli", "Sena"), ["Neveu"])
        self.assertEqual(libelles("Amavi", "Afi"), ["Nièce"])
        self.assertEqual(libelles("Gilles", "Ayaba"), ["Neveu (par alliance)"])

    def test_cousins(self):
        self.assertEqual(libelles("Mawuli", "Gilles"), ["Cousin"])
        self.assertEqual(libelles("Amavi", "Yawa"), ["Cousine"])

    def test_pas_de_cousin_pour_un_oncle(self):
        self.assertNotIn("Cousin", [l.libelle for l in liens(F, "Sena", "Mawuli")])

    def test_branches_sans_parent_commun(self):
        # Daniel (fils de Fabrice) et Mawuli n'ont aucun ancêtre commun
        self.assertEqual(libelles("Daniel", "Mawuli"), [])


class TestBelleFamille(unittest.TestCase):
    def test_belle_mere_remariage(self):
        self.assertEqual(libelles("Afi", "Fabrice"), ["Belle-mère (remariage d'un parent)"])

    def test_beau_fils_enfant_du_conjoint(self):
        self.assertEqual(libelles("Fabrice", "Afi"), ["Beau-fils (enfant du conjoint)"])

    def test_beau_parent_du_conjoint(self):
        self.assertEqual(libelles("Koffi", "Nadege"), ["Beau-père (parent du conjoint)"])

    def test_gendre_belle_fille(self):
        self.assertEqual(libelles("Nadege", "Koffi"), ["Belle-fille (conjoint(e) de l'enfant)"])
        self.assertEqual(libelles("Prosper", "Afi"), ["Gendre (conjoint(e) de l'enfant)"])

    def test_beau_frere_belle_soeur(self):
        self.assertEqual(libelles("Roland", "Sena"), ["Beau-frère"])
        self.assertEqual(libelles("Ayaba", "Afi"), ["Belle-sœur"])


class TestPhrases(unittest.TestCase):
    def test_articles(self):
        self.assertEqual(phrase(F, "Koffi", "Mawuli", liens(F, "Koffi", "Mawuli")[0]),
                         "Koffi est le père de Mawuli")
        self.assertEqual(phrase(F, "Sena", "Mawuli", liens(F, "Sena", "Mawuli")[0]),
                         "Sena est l'oncle de Mawuli")
        self.assertEqual(phrase(F, "Ayaba", "Afi", liens(F, "Ayaba", "Afi")[0]),
                         "Ayaba est la belle-sœur d'Afi")


class TestFamilleDe(unittest.TestCase):
    def test_famille_de_mawuli(self):
        membres = dict(famille_de(F, "Mawuli"))
        self.assertIn("Dossou", membres)
        self.assertIn("Gilles", membres)
        self.assertNotIn("Mawuli", membres)
        self.assertNotIn("Ablavi", membres)  # aucun lien avec Mawuli

    def test_proches_d_abord(self):
        resultat = famille_de(F, "Mawuli")
        self.assertEqual(resultat[0][0], "Nadege")  # l'épouse passe en premier
        rangs = [ls[0].rang for _, ls in resultat]
        self.assertEqual(rangs, sorted(rangs))

    def test_symetrie(self):
        """Si a a un lien avec b, alors b a un lien avec a (pour toutes les paires)."""
        for a in F.personnes:
            for b in F.personnes:
                if a == b:
                    continue
                la = {l.libelle for l in liens(F, a, b)}
                lb = {l.libelle for l in liens(F, b, a)}
                self.assertEqual(bool(la), bool(lb), f"asymétrie de présence entre {a} et {b}")


class TestNiveaux(unittest.TestCase):
    """Niveaux de génération utilisés pour dessiner l'arbre."""

    def setUp(self):
        self.n = F.niveau()

    def test_generations(self):
        self.assertEqual([self.n[x] for x in ("Dossou", "Koffi", "Mawuli", "Selom")], [0, 1, 2, 3])

    def test_epoux_meme_niveau(self):
        for p in F.personnes:
            for c in F.conjoints(p):
                self.assertEqual(self.n[p], self.n[c], f"{p} / {c}")

    def test_coparents_meme_niveau(self):
        self.assertEqual(self.n["Ablavi"], self.n["Roland"])

    def test_demi_freres_meme_niveau(self):
        self.assertEqual(self.n["Fabrice"], self.n["Yawa"])

    def test_enfant_sous_ses_parents(self):
        for p in F.personnes:
            for parent in F.parents(p):
                self.assertGreater(self.n[p], self.n[parent])


if __name__ == "__main__":
    unittest.main()
