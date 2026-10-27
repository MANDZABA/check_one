from dataclasses import dataclass, field

FAIBLE, MOYEN, ELEVE = "FAIBLE", "MOYEN", "ELEVE"

VOLUME_MOINS_1M = "LT_1M"
VOLUME_1M_10M = "1M_10M"
VOLUME_PLUS_10M = "GT_10M"

VOLUME_LIBELLES = {
    VOLUME_MOINS_1M: "Moins de 1 000 000 FCFA",
    VOLUME_1M_10M: "De 1 000 000 à 10 000 000 FCFA",
    VOLUME_PLUS_10M: "Plus de 10 000 000 FCFA",
}

PAYS_SANCTIONNES = {"KP": "Corée du Nord", "IR": "Iran", "SY": "Syrie", "RU": "Russie"}

NIVEAUX = {
    FAIBLE: {"libelle": "Risque faible", "couleur": "vert"},
    MOYEN: {"libelle": "Risque moyen", "couleur": "jaune"},
    ELEVE: {"libelle": "Risque élevé", "couleur": "rouge"},
}


@dataclass
class ResultatScoring:
    niveau: str
    motifs: list = field(default_factory=list)


def calculer_risque(est_ppe, nationalite, volume):
    if volume not in VOLUME_LIBELLES:
        raise ValueError(f"Tranche de volume inconnue : {volume!r}")

    motifs = []
    if est_ppe:
        motifs.append("Le client est une Personne Politiquement Exposée (PPE).")
    if nationalite in PAYS_SANCTIONNES:
        motifs.append(f"Nationalité sous sanctions internationales : {PAYS_SANCTIONNES[nationalite]}.")
    if volume == VOLUME_PLUS_10M:
        motifs.append("Volume mensuel estimé supérieur à 10 000 000 FCFA.")

    if motifs:
        return ResultatScoring(ELEVE, motifs)
    if volume == VOLUME_1M_10M:
        return ResultatScoring(MOYEN, ["Volume entre 1 000 000 et 10 000 000 FCFA, client non PPE."])
    return ResultatScoring(FAIBLE, ["Volume inférieur à 1 000 000 FCFA, client non PPE, aucun critère aggravant."])