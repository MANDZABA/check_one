#Génération du rapport PDF de la fiche KYC (bonus du cahier des charges).*/

from io import BytesIO

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Couleur des pastilles (cercles) selon le résultat
PASTILLES = {
    "vert": colors.HexColor("#22A05A"),
    "jaune": colors.HexColor("#E0A400"),
    "rouge": colors.HexColor("#E0352B"),
}

ENCRE = colors.HexColor("#14213D")
GRIS = colors.HexColor("#5B6475")
FILET = colors.HexColor("#E3E7EE")

class Pastille(Flowable):
    #Cercle plein de couleur, utilisé comme indicateur visuel.

    def __init__(self, couleur, diametre=12):
        super().__init__()
        self.couleur = couleur
        self.diametre = diametre
        self.width = self.height = diametre

    def draw(self):
        r = self.diametre / 2
        self.canv.setFillColor(self.couleur)
        self.canv.circle(r, r, r, stroke=0, fill=1)


def encadre(titre, valeur, couleur, s_txt):
    #Rectangle de synthèse : pastille de couleur + titre + résultat en texte normal
    contenu = Table(
        [[Pastille(couleur), Paragraph(f"<b>{titre}</b><br/><font size=13>{valeur}</font>", s_txt)]],
        colWidths=[8 * mm, 73 * mm],
    )
    contenu.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return contenu

def generer_pdf(controle) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
        title=f"Fiche KYC {controle.reference}", author="Check One",
    )

    base = getSampleStyleSheet()
    s_titre = ParagraphStyle("titre", parent=base["Title"], alignment=TA_LEFT,
                             fontSize=17, textColor=ENCRE, spaceAfter=2)
    s_sous = ParagraphStyle("sous", parent=base["Normal"], fontSize=9, textColor=GRIS)
    s_h2 = ParagraphStyle("h2", parent=base["Heading2"], fontSize=11, textColor=ENCRE,
                          spaceBefore=10, spaceAfter=4)
    s_txt = ParagraphStyle("txt", parent=base["Normal"], fontSize=9.5, leading=13, textColor=ENCRE)
    s_lbl = ParagraphStyle("lbl", parent=s_txt, textColor=GRIS)

    date_locale = timezone.localtime(controle.date_controle)
    els = [
        Paragraph("Check One, Fiche de Conformité KYC", s_titre),
        Paragraph(f"Référence {controle.reference} &nbsp;·&nbsp; Contrôle effectué le "
                  f"{date_locale:%d/%m/%Y à %H:%M}", s_sous),
        Spacer(1, 8),
    ]
    # Rectangles de synthèse : pastille de couleur + texte normal
    couleur_screening = "rouge" if controle.est_fiche else "vert"
    synthese = Table(
            [[
                encadre("Niveau de risque", controle.libelle_risque,
                        PASTILLES[controle.couleur_risque], s_txt),
                encadre("Screening check", controle.resultat_screening,
                        PASTILLES[couleur_screening], s_txt),
            ]],
            colWidths=[87 * mm, 87 * mm],
        )
    synthese.setStyle(TableStyle([
            ("BOX", (0, 0), (0, 0), 0.8, FILET),
            ("BOX", (1, 0), (1, 0), 0.8, FILET),
            ("PADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
    els.append(synthese)

    if controle.est_fiche and controle.correspondance:
            c = controle.correspondance
            els += [
                Spacer(1, 6),
                Paragraph(
                    f"<b>Correspondance :</b> {c['prenoms']} {c['nom']} &nbsp;·&nbsp; "
                    f"Motif : {c['motif']} &nbsp;·&nbsp; Source : {c['source']} &nbsp;·&nbsp; Réf. {c['id']}",
                    s_txt,
                ),
            ]

    els.append(Paragraph("Motifs du niveau de risque", s_h2))
    for m in controle.motifs_risque:
            els.append(Paragraph(f"• {m}", s_txt))

    els.append(Paragraph("Conduite à tenir suggérée", s_h2))
    els.append(Paragraph(controle.recommandation, s_txt))

    els.append(Paragraph("Données du client", s_h2))
    lignes = [
            ("Nom et prénom(s)", controle.nom_complet),
            ("Date de naissance", controle.date_naissance.strftime("%d/%m/%Y")),
            ("Nationalité", controle.nationalite_libelle),
            ("Pièce d'identité", f"{controle.get_type_piece_display()} n° {controle.numero_piece}"),
            ("Profession / secteur", controle.profession),
            ("Statut PPE", "Oui" if controle.est_ppe else "Non"),
            ("Volume mensuel estimé", controle.get_volume_mensuel_display()),
        ]
    t = Table([[Paragraph(a, s_lbl), Paragraph(b, s_txt)] for a, b in lignes],
                colWidths=[55 * mm, 119 * mm])
    t.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, FILET),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
    els.append(t)

    els += [Spacer(1, 18), Paragraph(
        "Document généré automatiquement par Check One. Le screening est effectué sur une "
        "base de sanction de test. Cette fiche constitue une aide à la "
        "décision et ne remplace pas l'appréciation du responsable conformité.",
        ParagraphStyle("pied", parent=s_sous, fontSize=8),
    )]

    doc.build(els)
    return buffer.getvalue()