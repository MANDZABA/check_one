#Un « Controle » est l'enregistrement d'une vérification KYC :
#les données saisies, le résultat du scoring et celui du screening,
#figés au moment du contrôle (traçabilité pour la conformité).

from django.db import models

from . import scoring
from .pays import CHOIX_PAYS, PAYS_DICT

class Controle(models.Model):
    class TypePiece(models.TextChoices):
        CNIB = "CNIB", "CNIB"
        PASSEPORT = "PASSEPORT", "Passeport"

    class Volume(models.TextChoices):
        MOINS_1M = scoring.VOLUME_MOINS_1M, scoring.VOLUME_LIBELLES[scoring.VOLUME_MOINS_1M]
        DE_1M_A_10M = scoring.VOLUME_1M_10M, scoring.VOLUME_LIBELLES[scoring.VOLUME_1M_10M]
        PLUS_10M = scoring.VOLUME_PLUS_10M, scoring.VOLUME_LIBELLES[scoring.VOLUME_PLUS_10M]

    class Niveau(models.TextChoices):
        FAIBLE = scoring.FAIBLE, "Faible"
        MOYEN = scoring.MOYEN, "Moyen"
        ELEVE = scoring.ELEVE, "Élevé"

    #Données saisies
    nom = models.CharField("Nom", max_length=100)
    prenoms = models.CharField("Prénom(s)", max_length=150)
    date_naissance = models.DateField("Date de naissance")
    nationalite = models.CharField("Nationalité", max_length=2, choices=CHOIX_PAYS)
    type_piece = models.CharField("Type de pièce", max_length=10, choices=TypePiece.choices)
    numero_piece = models.CharField("Numéro de pièce", max_length=20)
    profession = models.CharField("Profession / secteur d'activité", max_length=150)
    est_ppe = models.BooleanField("Personne Politiquement Exposée (PPE)")
    volume_mensuel = models.CharField(
        "Volume mensuel estimé", max_length=10, choices=Volume.choices
    )

    # Résultats figés au moment du contrôle
    niveau_risque = models.CharField(max_length=10, choices=Niveau.choices)
    motifs_risque = models.JSONField(default=list)
    est_fiche = models.BooleanField(default=False)
    resultat_screening = models.CharField(max_length=100)
    correspondance = models.JSONField(null=True, blank=True)

    date_controle = models.DateTimeField("Date du contrôle", auto_now_add=True)

    class Meta:
        ordering = ["-date_controle"]
        verbose_name = "contrôle KYC"
        verbose_name_plural = "contrôles KYC"

    def __str__(self):
        return f"{self.reference} · {self.nom_complet}"

    @property
    def reference(self) -> str:
        return f"KYC-{self.date_controle:%Y%m%d}-{self.pk:05d}"

    @property
    def nom_complet(self) -> str:
        return f"{self.prenoms} {self.nom.upper()}"

    @property
    def nationalite_libelle(self) -> str:
        return PAYS_DICT.get(self.nationalite, self.nationalite)

    @property
    def couleur_risque(self) -> str:
        return scoring.NIVEAUX[self.niveau_risque]["couleur"]

    @property
    def libelle_risque(self) -> str:
        return scoring.NIVEAUX[self.niveau_risque]["libelle"]

    @property
    def nationalite_sanctionnee(self) -> bool:
        return self.nationalite in scoring.PAYS_SANCTIONNES

    @property
    def recommandation(self) -> str:
        """Conduite à tenir suggérée au juriste (aide à la décision)."""
        if self.est_fiche:
            return (
                "Ne pas entrer en relation. Bloquer le dossier et transmettre "
                "immédiatement au responsable conformité pour vérification "
                "et, le cas échéant, déclaration à la CENTIF."
            )
        if self.niveau_risque == scoring.ELEVE:
            return (
                "Vigilance renforcée : obtenir la validation du responsable "
                "conformité, justifier l'origine des fonds et prévoir un suivi "
                "rapproché des opérations."
            )
        if self.niveau_risque == scoring.MOYEN:
            return (
                "Vigilance standard renforcée : vérifier les justificatifs "
                "d'activité et revoir le dossier périodiquement."
            )
        return "Vigilance simplifiée : entrée en relation possible selon la procédure habituelle."