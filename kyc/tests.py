import json
from datetime import date

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from . import scoring, screening
from .models import Controle

LT, MID, GT = scoring.VOLUME_MOINS_1M, scoring.VOLUME_1M_10M, scoring.VOLUME_PLUS_10M


def premiere_entree_fichee():
    """Première personne de la base de sanctions (quel que soit son nom)."""
    with open(settings.SANCTIONS_DB_PATH, encoding="utf-8") as f:
        return json.load(f)["entries"][0]


class ScoringTests(TestCase):
    """Table de vérité complète des règles du cahier des charges."""

    CAS = [
        # (PPE, nationalité, volume, niveau attendu)
        (False, "BF", LT, scoring.FAIBLE),
        (False, "BF", MID, scoring.MOYEN),
        (False, "BF", GT, scoring.ELEVE),
        (True, "BF", LT, scoring.ELEVE),
        (True, "BF", MID, scoring.ELEVE),
        (True, "BF", GT, scoring.ELEVE),
        # Nationalité sanctionnée : Rouge quel que soit le volume
        (False, "KP", LT, scoring.ELEVE),
        (False, "IR", LT, scoring.ELEVE),
        (False, "SY", MID, scoring.ELEVE),
        (False, "RU", LT, scoring.ELEVE),
        (True, "RU", GT, scoring.ELEVE),
    ]

    def test_table_de_verite(self):
        for ppe, nat, vol, attendu in self.CAS:
            with self.subTest(ppe=ppe, nationalite=nat, volume=vol):
                self.assertEqual(scoring.calculer_risque(ppe, nat, vol).niveau, attendu)

    def test_motifs_cumules(self):
        r = scoring.calculer_risque(True, "IR", GT)
        self.assertEqual(len(r.motifs), 3)

    def test_volume_inconnu(self):
        with self.assertRaises(ValueError):
            scoring.calculer_risque(False, "BF", "???")


class ScreeningTests(TestCase):
    base = settings.SANCTIONS_DB_PATH

    def test_correspondance_exacte(self):
        e = premiere_entree_fichee()
        r = screening.rechercher(e["nom"], e["prenoms"], self.base)
        self.assertTrue(r.est_fiche)
        self.assertEqual(r.message, "Individu fiché détecté")
        self.assertEqual(r.entree["id"], e["id"])

    def test_insensible_casse_et_ordre(self):
        e = premiere_entree_fichee()
        # prénoms et nom inversés, en minuscules
        r = screening.rechercher(e["prenoms"].lower(), e["nom"].lower(), self.base)
        self.assertTrue(r.est_fiche)

    def test_aucune_correspondance(self):
        r = screening.rechercher("PERSONNE", "Inconnue Totalement", self.base)
        self.assertFalse(r.est_fiche)
        self.assertEqual(r.message, "Aucun fichage détecté")


class ParcoursTests(TestCase):
    def donnees(self, **kw):
        d = {
            "nom": "Sawadogo",
            "prenoms": "awa",
            "date_naissance": "1990-04-12",
            "nationalite": "BF",
            "type_piece": "CNIB",
            "numero_piece": "B 1234 5678",
            "profession": "Commerçante",
            "est_ppe": "non",
            "volume_mensuel": MID,
        }
        d.update(kw)
        return d

    def test_controle_complet_et_fiche(self):
        r = self.client.post(reverse("kyc:new"), self.donnees())
        c = Controle.objects.get()
        self.assertRedirects(r, reverse("kyc:fiche", args=[c.pk]))
        self.assertEqual(c.nom, "SAWADOGO")
        self.assertEqual(c.numero_piece, "B12345678")
        self.assertEqual(c.niveau_risque, scoring.MOYEN)
        self.assertFalse(c.est_fiche)

        page = self.client.get(reverse("kyc:fiche", args=[c.pk]))
        self.assertContains(page, "Check One, Fiche de Conformité KYC")
        self.assertContains(page, "Risque moyen")
        self.assertContains(page, "Aucun fichage détecté")

    def test_individu_fiche(self):
        e = premiere_entree_fichee()
        self.client.post(reverse("kyc:new"),
                         self.donnees(nom=e["nom"], prenoms=e["prenoms"], volume_mensuel=LT))
        c = Controle.objects.get()
        self.assertTrue(c.est_fiche)
        page = self.client.get(reverse("kyc:fiche", args=[c.pk]))
        self.assertContains(page, "Individu fiché détecté")

    def test_ppe_obligatoire(self):
        d = self.donnees()
        del d["est_ppe"]
        r = self.client.post(reverse("kyc:new"), d)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Controle.objects.count(), 0)

    def test_date_future_refusee(self):
        r = self.client.post(reverse("kyc:new"),
                             self.donnees(date_naissance=f"{date.today().year + 1}-01-01"))
        self.assertContains(r, "doit être dans le passé")

    def test_pdf(self):
        e = premiere_entree_fichee()
        self.client.post(reverse("kyc:new"),
                         self.donnees(nom=e["nom"], prenoms=e["prenoms"], est_ppe="oui"))
        c = Controle.objects.get()
        r = self.client.get(reverse("kyc:fiche_pdf", args=[c.pk]))
        self.assertEqual(r["Content-Type"], "application/pdf")
        self.assertTrue(r.content.startswith(b"%PDF"))

    def test_historique_filtre(self):
        self.client.post(reverse("kyc:new"), self.donnees())
        self.client.post(reverse("kyc:new"), self.donnees(nom="Traoré", est_ppe="oui"))
        r = self.client.get(reverse("kyc:historique"), {"niveau": scoring.ELEVE})
        self.assertContains(r, "TRAORÉ")
        self.assertNotContains(r, "SAWADOGO")