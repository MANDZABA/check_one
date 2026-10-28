# Check One · Module Screening & Scoring KYC

Prototype réalisé dans le cadre du test technique **Check One (SAMB Group)**.

L'application permet à un juriste ou chargé de conformité de saisir un client (personne physique) et d'obtenir instantanément :

- un **niveau de risque** (Vert / Jaune / Rouge) accompagné des motifs de la décision ;
- le résultat du **screening** contre une base de sanctions simulée ;
- une **fiche de conformité KYC** consultable à l'écran et téléchargeable en **PDF**.

Chaque contrôle est enregistré et horodaté. L'onglet *Historique* permet de rechercher un client (nom, prénoms, numéro de pièce) et de filtrer par niveau de risque.

---

## Tester le prototype en ligne (sans installation)

🔗 **Lien de démonstration : [lien ngrok à compléter]**

Le prototype tourne sur le poste du développeur et il est rendu accessible sur Internet par un tunnel sécurisé **ngrok**. Le lien est donc actif **pendant les créneaux de démonstration convenus**. Si la page ne répond pas, il suffit de me contacter pour que je relance l'accès.

**Mode d'emploi**

1. Ouvrir le lien. Une page d'avertissement ngrok s'affiche la première fois : cliquer sur **« Visit Site »**.
2. Remplir le formulaire avec un client fictif, puis cliquer sur **« Lancer le contrôle »**.
3. Lire la fiche de conformité. Le bouton **« Générer le rapport PDF »** permet de la télécharger.
4. Le menu **« Historique »** liste tous les contrôles effectués.

Aucune connaissance technique n'est nécessaire. Des cas de test prêts à l'emploi sont proposés plus bas, dans la section *Scénarios de test rapides*.

---

## Stack technique

| Couche | Choix |
|---|---|
| Back end | Python 3.12+, Django |
| Base de données | SQLite |
| Front end | Templates Django, CSS sur mesure (sans framework) |
| Rapport PDF | ReportLab |
| Accès de démonstration | Tunnel ngrok vers le serveur Django |

---

## Installation locale

```bash
git clone https://github.com/<compte>/checkone-kyc.git
cd checkone-kyc

python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Linux / macOS

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Ouvrir ensuite http://127.0.0.1:8000

**Interface d'administration (facultatif)**

```bash
python manage.py createsuperuser
```

Puis http://127.0.0.1:8000/admin (les résultats de contrôle y sont en lecture seule).

**Lancer les tests**

```bash
python manage.py test kyc
```

---

## Règles métier

### 1. Scoring du risque (`kyc/scoring.py`)

| Niveau | Condition |
|---|---|
| 🔴 **Élevé** | PPE = Oui **ou** nationalité sous sanctions internationales (Corée du Nord, Iran, Syrie, Russie) **ou** volume mensuel > 10 000 000 FCFA |
| 🟡 **Moyen** | Volume entre 1 000 000 et 10 000 000 FCFA **et** PPE = Non |
| 🟢 **Faible** | Volume < 1 000 000 FCFA **et** PPE = Non |

Les critères *Élevé* sont évalués en premier : un seul suffit. Un client de nationalité sanctionnée avec un volume inférieur à 1M FCFA est donc classé **Rouge**.

Tous les motifs applicables sont listés sur la fiche, afin que le juriste comprenne la décision et ne se contente pas d'une couleur.

Le moteur est une fonction pure, indépendante de Django, couverte par une table de vérité complète dans `kyc/tests.py`.

### 2. Screening (`kyc/screening.py`)

Le nom saisi est comparé à la base simulée `data/sanctions_db.json`.

- Correspondance trouvée : **« Individu fiché détecté »**, avec le motif, la source et la référence de l'entrée.
- Aucune correspondance : **« Aucun fichage détecté »**.

**Interprétation de la « correspondance exacte »** : avant comparaison, les noms sont normalisés (majuscules, accents et espaces superflus ignorés) et l'ordre nom / prénoms n'a pas d'importance. Ainsi, « dubois marie », « Marie DUBOIS » et « DUBOIS Marie » correspondent tous à l'entrée *Marie DUBOIS*.

En revanche, un nom approchant (« Mari DUBOIS ») ne correspond pas : aucune recherche floue n'a été ajoutée, faute de demande explicite.

### 3. Fiche de conformité KYC

- En-tête « Check One, Fiche de Conformité KYC »
- Référence unique (ex. `KYC-20261027-00001`) et date / heure du contrôle
- Récapitulatif des données saisies
- Badge couleur du niveau de risque et motifs
- Résultat du screening
- Conduite à tenir suggérée (aide à la décision)
- Bouton **« Générer le rapport PDF »**

---

## Base de sanctions de test

> ⚠️ **Toutes les identités ci dessous sont entièrement fictives** et servent uniquement à la démonstration. Les sources indiquées sont des rattachements simulés : aucune de ces personnes ne figure sur une liste officielle.

Fichier : `data/sanctions_db.json`

| Réf. | Nom | Prénom(s) | Pays | Motif | Source (simulée) |
|---|---|---|---|---|---|
| SAN-001 | DUBOIS | Marie | France | Sanctions économiques internationales | Conseil de sécurité des Nations Unies |
| SAN-002 | HADDAD | Omar | Liban | Corruption et blanchiment d'argent | Office of Foreign Assets Control (OFAC) |
| SAN-003 | PETROV | Anatoly | Russie | Infractions liées à la sécurité nationale | Union européenne, liste de sanctions |
| SAN-004 | ALVAREZ | Sofia | Espagne | Fraude fiscale et financement illicite | Autorités financières européennes |
| SAN-005 | BENALI | Khaled | Maroc | Violation des réglementations financières | Banque centrale et organismes de surveillance |

Structure d'une entrée :

```json
{
  "id": "SAN-001",
  "nom": "Dubois",
  "prenoms": "Marie",
  "pays": "France",
  "motif": "Sanctions économiques internationales",
  "source": "Conseil de sécurité des Nations Unies"
}
```

Pour ajouter une personne, il suffit d'ajouter une entrée avec les clés `id`, `nom`, `prenoms`, `motif` et `source`. Aucune modification du code n'est nécessaire.

---

## Scénarios de test rapides

| Saisie | Résultat attendu |
|---|---|
| Burkina Faso, PPE Non, moins de 1M FCFA | 🟢 Risque faible · Aucun fichage |
| Burkina Faso, PPE Non, 1M à 10M FCFA | 🟡 Risque moyen · Aucun fichage |
| Burkina Faso, PPE Non, plus de 10M FCFA | 🔴 Risque élevé |
| PPE **Oui**, volume quelconque | 🔴 Risque élevé |
| Nationalité **Iran**, moins de 1M FCFA | 🔴 Risque élevé (pays sanctionné) |
| Nom **Sofia ALVAREZ** (ou tout nom de la liste) | ⚠️ Individu fiché détecté |
| Nom **alvarez sofia** (minuscules, ordre inversé) | ⚠️ Individu fiché détecté |
| Formulaire vide ou date de naissance future | Messages d'erreur sous les champs concernés |

---

## Choix orientés utilisateur (juriste)

- Vocabulaire métier, aucun terme technique à l'écran.
- Les décisions sont **expliquées** (motifs listés) et non seulement affichées.
- Une **conduite à tenir** est suggérée selon le résultat ; elle reste une aide à la décision.
- PPE et volume se saisissent par boutons, **sans valeur par défaut** : le juriste doit répondre explicitement.
- Normalisation automatique des saisies (nom en majuscules, numéro de pièce sans espaces).
- Validations : date de naissance dans le passé, format du numéro de pièce, tous les champs obligatoires.
- Résultats **figés** au moment du contrôle et non modifiables dans l'administration (traçabilité).
- Interface responsive (ordinateur, tablette, mobile) et imprimable.

---

## Points soumis à validation

Questions transmises au commanditaire, avec le comportement retenu par défaut :

1. **Un individu fiché doit il forcer le niveau de risque en Rouge ?**
   Actuellement non : le scoring applique strictement les règles du cahier des charges, et le screening s'affiche séparément en alerte, avec la consigne de ne pas entrer en relation. Le passage en Rouge automatique est une modification d'une ligne.
2. **Priorité de la nationalité sanctionnée sur le volume** : retenue (Rouge dans tous les cas).
3. **Correspondance exacte** : interprétée comme décrit plus haut.
4. **Liste des pays sanctionnés** : limitée aux 4 pays du cahier des charges, centralisée dans `scoring.PAYS_SANCTIONNES` pour faciliter sa mise à jour.

---

## Structure du projet

```
checkone-kyc/
├── config/                 # Paramètres et URLs du projet Django
├── data/
│   └── sanctions_db.json   # Base de sanctions simulée
├── kyc/
│   ├── scoring.py          # Moteur de scoring (règles du cahier des charges)
│   ├── screening.py        # Moteur de screening
│   ├── services.py         # Orchestration d'un contrôle
│   ├── models.py           # Modèle Controle (traçabilité)
│   ├── forms.py            # Formulaire et validations
│   ├── views.py            # Pages : saisie, fiche, PDF, historique
│   ├── urls.py
│   ├── pdf.py              # Rapport PDF
│   ├── pays.py             # Liste des nationalités
│   ├── admin.py            # Administration en lecture seule
│   ├── templates/kyc/      # Gabarits HTML
│   ├── static/kyc/         # Feuille de style
│   └── tests.py            # Tests unitaires et fonctionnels
├── requirements.txt
└── README.md
```

---

## Mise à disposition via ngrok

Pour rendre le prototype accessible depuis Internet à partir du poste local :

```bash
# Terminal 1 : lancer l'application
python manage.py runserver

# Terminal 2 : ouvrir le tunnel
ngrok http 8000
```

ngrok affiche une adresse publique (`https://xxxx.ngrok-free.app`) sur la ligne *Forwarding*. C'est ce lien qui est partagé.

Réglages nécessaires dans `config/settings.py` pendant la démonstration :

```python
ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".ngrok-free.app"]
CSRF_TRUSTED_ORIGINS = ["https://*.ngrok-free.app"]
```

**Pourquoi ngrok pour ce test**

- Mise en ligne immédiate, sans configuration de serveur.
- La démonstration se fait sur la version exacte du code présente dans ce dépôt.
- L'historique des contrôles est conservé entre deux sessions (base SQLite locale).

**Limites assumées**

- Le lien n'est actif que lorsque le poste du développeur et le tunnel sont allumés.
- L'adresse peut changer à chaque redémarrage du tunnel (offre gratuite).
- Le serveur de développement Django n'est pas destiné à la production. Une mise en production réelle passerait par un hébergement dédié (Gunicorn, serveur web, base PostgreSQL) et `DEBUG = False`.

---

## Avertissement

Les données de sanctions sont fictives et servent uniquement à la démonstration. L'outil constitue une aide à la décision et ne remplace pas l'appréciation du responsable conformité.
