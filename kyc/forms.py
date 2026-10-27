import re
from datetime import date

from django import forms

from .models import Controle

OUI_NON = [("oui", "Oui"), ("non", "Non")]


class ControleForm(forms.ModelForm):
    # PPE en boutons radio Oui / Non, sans valeur par défaut :
    # le juriste doit répondre explicitement.
    est_ppe = forms.TypedChoiceField(
        label="Le client est il une Personne Politiquement Exposée (PPE) ?",
        choices=OUI_NON,
        coerce=lambda v: v == "oui",
        widget=forms.RadioSelect,
        help_text="Président, Ministre, député, directeur général d'État, haut gradé militaire, "
        "en fonction ou l'ayant été.",
    )

    class Meta:
        model = Controle
        fields = [
            "nom",
            "prenoms",
            "date_naissance",
            "nationalite",
            "type_piece",
            "numero_piece",
            "profession",
            "est_ppe",
            "volume_mensuel",
        ]
        widgets = {
            "nom": forms.TextInput(attrs={"placeholder": "Ex. OUÉDRAOGO", "autocomplete": "off"}),
            "prenoms": forms.TextInput(attrs={"placeholder": "Ex. Awa Mariam", "autocomplete": "off"}),
            "date_naissance": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "type_piece": forms.RadioSelect,
            "numero_piece": forms.TextInput(attrs={"placeholder": "Ex. B12345678", "autocomplete": "off"}),
            "profession": forms.TextInput(attrs={"placeholder": "Ex. Commerçante, import export"}),
            "volume_mensuel": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nationalite"].choices = [("", "Sélectionner un pays")] + list(
            self.fields["nationalite"].choices
        )[1:]
        self.fields["type_piece"].choices = Controle.TypePiece.choices
        self.fields["volume_mensuel"].choices = Controle.Volume.choices
        self.fields["volume_mensuel"].label = "Volume mensuel estimé des opérations"

    def clean_nom(self):
        return " ".join(self.cleaned_data["nom"].split()).upper()

    def clean_prenoms(self):
        return " ".join(self.cleaned_data["prenoms"].split()).title()

    def clean_date_naissance(self):
        d = self.cleaned_data["date_naissance"]
        today = date.today()
        if d >= today:
            raise forms.ValidationError("La date de naissance doit être dans le passé.")
        age = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
        if age > 120:
            raise forms.ValidationError("Date de naissance invraisemblable, merci de vérifier.")
        return d

    def clean_numero_piece(self):
        num = re.sub(r"\s+", "", self.cleaned_data["numero_piece"]).upper()
        if not re.fullmatch(r"[A-Z0-9]{5,20}", num):
            raise forms.ValidationError(
                "Le numéro doit contenir entre 5 et 20 lettres ou chiffres, sans caractère spécial."
            )
        return num