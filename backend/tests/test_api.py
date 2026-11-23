"""
Tests de l'API (nécessitent fastapi et httpx : pip install -r requirements.txt).
Ignorés automatiquement si ces paquets ne sont pas installés.
Lancer depuis backend/ :   python -m unittest discover -s tests -v     (ou : pytest)
"""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    from app.routers import api as routes
    from fastapi.testclient import TestClient
    from app.main import app
    DISPONIBLE = True
except ImportError:  # fastapi / httpx absents
    DISPONIBLE = False


@unittest.skipUnless(DISPONIBLE, "fastapi/httpx non installés")
class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self._dossier_temporaire = TemporaryDirectory()
        self._ancien_chemin_ajouts = routes.CHEMIN_AJOUTS_ONTOLOGIE
        routes.CHEMIN_AJOUTS_ONTOLOGIE = Path(self._dossier_temporaire.name) / "ajouts.owl"
        routes.obtenir_famille.cache_clear()

    def tearDown(self):
        routes.CHEMIN_AJOUTS_ONTOLOGIE = self._ancien_chemin_ajouts
        routes.obtenir_famille.cache_clear()
        self._dossier_temporaire.cleanup()

    def test_sante(self):
        r = self.client.get("/api/sante")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"statut": "ok", "personnes": 22})

    def test_liste_personnes(self):
        r = self.client.get("/api/personnes")
        self.assertEqual(r.status_code, 200)
        noms = [p["nom"] for p in r.json()]
        self.assertEqual(len(noms), 22)
        self.assertEqual(noms, sorted(noms))

    def test_famille(self):
        r = self.client.get("/api/personnes/Mawuli/famille")
        self.assertEqual(r.status_code, 200)
        corps = r.json()
        self.assertEqual(corps["personne"]["id"], "Mawuli")
        par_id = {m["id"]: m for m in corps["membres"]}
        self.assertEqual(par_id["Koffi"]["liens"][0]["phrase"], "Koffi est le père de Mawuli")
        self.assertNotIn("Mawuli", par_id)

    def test_famille_personne_inconnue(self):
        self.assertEqual(self.client.get("/api/personnes/Inconnu/famille").status_code, 404)

    def test_lien(self):
        r = self.client.get("/api/lien", params={"a": "Sena", "b": "Mawuli"})
        self.assertEqual(r.status_code, 200)
        corps = r.json()
        self.assertEqual(corps["resume"], "Sena est l'oncle de Mawuli")
        self.assertEqual(corps["b_vers_a"][0]["phrase"], "Mawuli est le neveu de Sena")

    def test_lien_inexistant(self):
        r = self.client.get("/api/lien", params={"a": "Ablavi", "b": "Yawa"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["a_vers_b"], [])
        self.assertIn("Aucun lien", r.json()["resume"])

    def test_lien_meme_personne(self):
        r = self.client.get("/api/lien", params={"a": "Koffi", "b": "Koffi"})
        self.assertEqual(r.status_code, 400)

    def test_creer_personne_et_la_rattacher_comme_parent(self):
        r = self.client.post("/api/personnes", json={
            "nom": "Élodie Martin",
            "sexe": "F",
            "age": 36,
            "personne_liee_id": "Ama",
            "relation": "parent",
        })
        self.assertEqual(r.status_code, 201, r.text)
        personne = r.json()
        self.assertEqual(personne, {
            "id": "elodie-martin",
            "nom": "Élodie Martin",
            "sexe": "F",
            "age": 36,
        })

        personnes = self.client.get("/api/personnes").json()
        self.assertEqual(len(personnes), 23)
        self.assertIn(personne, personnes)

        famille_ama = self.client.get("/api/personnes/Ama/famille").json()
        elodie = next(m for m in famille_ama["membres"] if m["id"] == personne["id"])
        self.assertEqual(elodie["liens"][0]["phrase"], "Élodie Martin est la mère d'Ama")

        famille_elodie = self.client.get("/api/personnes/elodie-martin/famille").json()
        ama = next(m for m in famille_elodie["membres"] if m["id"] == "Ama")
        self.assertEqual(ama["liens"][0]["phrase"], "Ama est la fille d'Élodie Martin")

        graphe = self.client.get("/api/graphe").json()
        self.assertIn(
            {"source": "elodie-martin", "cible": "Ama", "type": "parent"},
            graphe["aretes"],
        )

    def test_creer_conjoint_et_generer_un_identifiant_unique(self):
        donnees = {
            "nom": "Hugo Martin",
            "sexe": "M",
            "personne_liee_id": "Ama",
            "relation": "conjoint",
        }
        premiere = self.client.post("/api/personnes", json=donnees)
        seconde = self.client.post("/api/personnes", json=donnees)
        self.assertEqual(premiere.status_code, 201, premiere.text)
        self.assertEqual(seconde.status_code, 201, seconde.text)
        self.assertEqual(premiere.json()["id"], "hugo-martin")
        self.assertEqual(seconde.json()["id"], "hugo-martin-2")
        self.assertIsNone(premiere.json()["age"])

        famille_ama = self.client.get("/api/personnes/Ama/famille").json()
        hugo = next(m for m in famille_ama["membres"] if m["id"] == "hugo-martin")
        self.assertEqual(hugo["liens"][0]["libelle"], "Époux")

    def test_creer_enfant_dune_personne_existante(self):
        r = self.client.post("/api/personnes", json={
            "nom": "Luc Martin",
            "sexe": "M",
            "age": 0,
            "personne_liee_id": "Ama",
            "relation": "enfant",
        })
        self.assertEqual(r.status_code, 201, r.text)

        famille_ama = self.client.get("/api/personnes/Ama/famille").json()
        luc = next(m for m in famille_ama["membres"] if m["id"] == "luc-martin")
        self.assertEqual(luc["liens"][0]["phrase"], "Luc Martin est le fils d'Ama")

        famille_luc = self.client.get("/api/personnes/luc-martin/famille").json()
        ama = next(m for m in famille_luc["membres"] if m["id"] == "Ama")
        self.assertEqual(ama["liens"][0]["phrase"], "Ama est la mère de Luc Martin")

    def test_creation_refuse_personne_rattachee_inconnue_et_donnees_invalides(self):
        donnees = {
            "nom": "Personne Test",
            "sexe": "F",
            "personne_liee_id": "Inconnu",
            "relation": "enfant",
        }
        self.assertEqual(self.client.post("/api/personnes", json=donnees).status_code, 404)
        donnees["personne_liee_id"] = "Ama"
        donnees["age"] = 131
        self.assertEqual(self.client.post("/api/personnes", json=donnees).status_code, 422)
        self.assertFalse(routes.CHEMIN_AJOUTS_ONTOLOGIE.exists())

    def test_graphe(self):
        r = self.client.get("/api/graphe")
        self.assertEqual(r.status_code, 200)
        corps = r.json()
        self.assertEqual(len(corps["noeuds"]), 22)
        types = {a["type"] for a in corps["aretes"]}
        self.assertEqual(types, {"parent", "mariage"})
        self.assertEqual(sum(a["type"] == "mariage" for a in corps["aretes"]), 7)
        self.assertEqual(sum(a["type"] == "parent" for a in corps["aretes"]), 26)


if __name__ == "__main__":
    unittest.main()
