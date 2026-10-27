"""Liste des nationalités proposées dans le formulaire (codes ISO 3166 alpha 2)."""

import unicodedata

PAYS = [
    ("BF", "Burkina Faso"),
    ("BJ", "Bénin"),
    ("CI", "Côte d'Ivoire"),
    ("GW", "Guinée-Bissau"),
    ("ML", "Mali"),
    ("NE", "Niger"),
    ("SN", "Sénégal"),
    ("TG", "Togo"),
    ("GH", "Ghana"),
    ("NG", "Nigeria"),
    ("GN", "Guinée"),
    ("MR", "Mauritanie"),
    ("CM", "Cameroun"),
    ("TD", "Tchad"),
    ("GA", "Gabon"),
    ("CG", "Congo"),
    ("CD", "RD Congo"),
    ("MA", "Maroc"),
    ("DZ", "Algérie"),
    ("TN", "Tunisie"),
    ("EG", "Égypte"),
    ("LB", "Liban"),
    ("FR", "France"),
    ("BE", "Belgique"),
    ("CH", "Suisse"),
    ("DE", "Allemagne"),
    ("GB", "Royaume-Uni"),
    ("ES", "Espagne"),
    ("IT", "Italie"),
    ("US", "États-Unis"),
    ("CA", "Canada"),
    ("CN", "Chine"),
    ("IN", "Inde"),
    ("TR", "Turquie"),
    ("AE", "Émirats arabes unis"),
    # Pays sous sanctions internationales (cf. scoring.PAYS_SANCTIONNES)
    ("KP", "Corée du Nord"),
    ("IR", "Iran"),
    ("SY", "Syrie"),
    ("RU", "Russie"),
]

PAYS_DICT = dict(PAYS)


def _cle_tri(pays):
    nom = unicodedata.normalize("NFKD", pays[1])
    return "".join(c for c in nom if not unicodedata.combining(c)).lower()


# Burkina Faso en tête, puis ordre alphabétique (accents ignorés)
CHOIX_PAYS = [PAYS[0]] + sorted(PAYS[1:], key=_cle_tri)
