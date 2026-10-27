from django.contrib import admin

from .models import Controle


@admin.register(Controle)
class ControleAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenoms", "nationalite", "est_ppe", "volume_mensuel",
                    "niveau_risque", "est_fiche", "date_controle")
    list_filter = ("niveau_risque", "est_fiche", "est_ppe", "nationalite")
    search_fields = ("nom", "prenoms", "numero_piece")
    readonly_fields = ("niveau_risque", "motifs_risque", "est_fiche",
                       "resultat_screening", "correspondance", "date_controle")