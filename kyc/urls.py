from django.urls import path

from . import views

app_name = "kyc"

urlpatterns = [
    path("", views.nouveau_controle, name="nouveau"),
    path("controles/", views.historique, name="historique"),
    path("controles/<int:pk>/", views.fiche, name="fiche"),
    path("controles/<int:pk>/pdf/", views.fiche_pdf, name="fiche_pdf"),
]