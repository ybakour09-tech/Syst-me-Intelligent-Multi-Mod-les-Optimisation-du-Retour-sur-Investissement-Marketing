# PRISMA : Système Intelligent Multi-Modèles pour l'Optimisation du ROI Marketing

Bienvenue sur **PRISMA**, un Data Product avancé conçu pour révolutionner la façon dont les décideurs allouent leurs budgets marketing. 
Ce projet utilise une architecture d'Intelligence Artificielle multi-modèles pour non seulement prédire les performances financières, mais surtout pour **expliquer mathématiquement** l'impact et la synergie de chaque canal (TV, Radio, Réseaux Sociaux).

## Lancement Rapide

Vous utilisez Windows ? Lancer l'application est un jeu d'enfant :
1. Clonez ce dépôt.
2. Double-cliquez sur le script **`lancer_prisma.bat`** à la racine du projet.
3. Le backend IA va démarrer automatiquement en arrière-plan et votre navigateur s'ouvrira sur le **Dashboard Prisma**.

> **Note :** Ne fermez pas la fenêtre de console noire tant que vous utilisez l'application. Elle fait tourner le moteur IA.

---

## Architecture Multi-Modèles

Plutôt que de s'appuyer sur un algorithme unique, PRISMA déploie une cascade de modèles experts :

1. **Identification (Random Forest Classifier)** : 
   Prend en entrée la configuration budgétaire et classifie instantanément la campagne future comme étant à `Haute Performance` ou `Basse Performance`.
2. **Prédiction Exacte (Réseau de Neurones - MLPRegressor)** : 
   Ingère les budgets ainsi que la classification précédente pour prédire avec une haute précision le `ROI (%)` et le Chiffre d'Affaires estimé (Ventes).
3. **Explicabilité Combinatoire (SHAPley Values)** : 
   L'explicateur SHAP "ouvre la boîte noire" du réseau de neurones. Il calcule la contribution exacte (positive ou négative) de la TV, de la Radio et des Réseaux Sociaux dans la formation du ROI, mettant en évidence les phénomènes de cannibalisation ou de synergie.

---

## Structure du Dépôt

Le code source a été organisé selon les standards de Data Science :

```text
/
├── api.py                  # Serveur backend (FastAPI) exposant les modèles IA
├── test_api.py             # Script de test de charge/réponse de l'API
├── lancer_prisma.bat       # Script d'auto-lancement sous Windows
├── dashboard/              # Code source du Frontend web (HTML, CSS, JS)
├── models/                 # Objets de Machine Learning pré-entraînés (joblib)
├── scripts/                # Tous les scripts Python d'exploration et d'entraînement (ML Pipeline)
├── notebooks/              # Cahiers Jupyter d'exploration de données
├── docs/                   # Documentation, rapports de performances et compte-rendus textuels
├── data/                   # Données brutes et normalisées (fichiers CSV)
└── plots/                  # Graphiques d'analyse générés lors de l'entraînement
```

---

## Documentation de l'API (FastAPI)

Le moteur IA est servi par une API REST ultra-rapide tournant sur le port `8000`. 
Vous pouvez accéder à la documentation interactive (Swagger UI) en visitant : `http://127.0.0.1:8000/docs` lorsque l'API tourne.

### Endpoints principaux :
- `POST /predict/performance` : Renvoie la catégorie de performance d'un scénario budgétaire.
- `POST /predict/roi` : Renvoie l'estimation brute du ROI.
- `POST /predict/shap_impact` : Renvoie le ROI complet ainsi que la décomposition mathématique SHAP par canal.

### Exemple de Payload JSON attendu :
```json
{
  "TV": 150.0,
  "Radio": 45.0,
  "Social Media": 30.0
}
```

---

## Interface Utilisateur (Prisma Dashboard)

L'interface a été conçue sans aucun framework lourd (Vanilla HTML/CSS/JS) mais arbore un design premium et futuriste inspiré du *Glassmorphism*. 
- **Temps Réel** : Les curseurs mettent à jour dynamiquement les prédictions.
- **Data Visualization** : Intégration de `Chart.js` pour tracer l'évolution du ROI et comparer visuellement différents scénarios d'investissement.

---

## Technologies Utilisées

- **Backend & IA** : Python 3.10+, FastAPI, Uvicorn, Scikit-Learn, SHAP, Pandas.
- **Frontend** : HTML5, CSS3 (Glassmorphism), Vanilla JavaScript, Chart.js.
- **Outils** : Git, Jupyter.