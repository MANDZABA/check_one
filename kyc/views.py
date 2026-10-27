from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ControleForm
from .models import Controle
from .pdf import generer_pdf
from .services import effectuer_controle


def nouveau_controle(request):
    """Formulaire de saisie d'un nouveau client (personne physique)."""
    if request.method == "POST":
        form = ControleForm(request.POST)
        if form.is_valid():
            controle = effectuer_controle(form.save(commit=False))
            return redirect("kyc:fiche", pk=controle.pk)
    else:
        form = ControleForm()

    stats = Controle.objects.aggregate(
        total=Count("id"),
        eleve=Count("id", filter=Q(niveau_risque=Controle.Niveau.ELEVE)),
        moyen=Count("id", filter=Q(niveau_risque=Controle.Niveau.MOYEN)),
        faible=Count("id", filter=Q(niveau_risque=Controle.Niveau.FAIBLE)),
        fiches=Count("id", filter=Q(est_fiche=True)),
    )
    return render(request, "kyc/nouveau.html", {
        "form": form,
        "stats": stats,
        "recents": Controle.objects.all()[:5],
        "nav": "nouveau",
    })


def fiche(request, pk):
    """Fiche de conformité KYC (sortie attendue, section 2.D)."""
    controle = get_object_or_404(Controle, pk=pk)
    return render(request, "kyc/fiche.html", {"c": controle, "nav": "historique"})


def fiche_pdf(request, pk):
    controle = get_object_or_404(Controle, pk=pk)
    response = HttpResponse(generer_pdf(controle), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{controle.reference}.pdf"'
    return response


def historique(request):
    controles = Controle.objects.all()
    q = request.GET.get("q", "").strip()
    niveau = request.GET.get("niveau", "")
    if q:
        controles = controles.filter(
            Q(nom__icontains=q) | Q(prenoms__icontains=q) | Q(numero_piece__icontains=q)
        )
    if niveau in Controle.Niveau.values:
        controles = controles.filter(niveau_risque=niveau)
    return render(request, "kyc/historique.html", {
        "controles": controles[:200],
        "q": q,
        "niveau": niveau,
        "niveaux": Controle.Niveau.choices,
        "nav": "historique",
    })