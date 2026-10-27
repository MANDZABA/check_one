import json
import unicodedata
from dataclasses import dataclass


@dataclass
class ResultatScreening:
    est_fiche: bool
    message: str
    entree: dict | None = None


def normaliser(nom, prenoms):
    texte = unicodedata.normalize("NFD", f"{nom} {prenoms}")
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")  # sans accents
    texte = texte.replace("-", " ").upper()
    return " ".join(sorted(texte.split()))  # l'ordre nom / prénoms n'a plus d'importance


def rechercher(nom, prenoms, chemin_base):
    with open(chemin_base, encoding="utf-8") as f:
        entrees = json.load(f)["entries"]

    cle = normaliser(nom, prenoms)
    for entree in entrees:
        if normaliser(entree["nom"], entree["prenoms"]) == cle:
            return ResultatScreening(True, "Individu fiché détecté", entree)
    return ResultatScreening(False, "Aucun fichage détecté")