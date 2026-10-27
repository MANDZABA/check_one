"""Orchestration d'un contrôle KYC : scoring + screening + enregistrement."""

from django.conf import settings

from . import scoring, screening
from .models import Controle


def effectuer_controle(controle: Controle) -> Controle:
    """Complète un contrôle (non encore enregistré) avec ses résultats, puis l'enregistre."""
    res_scoring = scoring.calculer_risque(
        est_ppe=controle.est_ppe,
        nationalite=controle.nationalite,
        volume=controle.volume_mensuel,
    )
    res_screening = screening.rechercher(
        controle.nom, controle.prenoms, settings.SANCTIONS_DB_PATH
    )

    controle.niveau_risque = res_scoring.niveau
    controle.motifs_risque = res_scoring.motifs
    controle.est_fiche = res_screening.est_fiche
    controle.resultat_screening = res_screening.message
    controle.correspondance = res_screening.entree
    controle.save()
    return controle