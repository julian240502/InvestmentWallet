# InvestmentWallet

Un tableau de bord interactif pour la gestion, l’analyse et l’optimisation de portefeuilles financiers. Ce projet permet de récupérer des données financières en temps réel, d’analyser les performances d’un portefeuille et de proposer des stratégies d’optimisation en s’appuyant sur des techniques d’optimisation des portefeuilles (par exemple, la méthode moyenne-variance de Markowitz).

## Objectifs du Projet

- **Collecte de données financières :** Récupérer automatiquement des données (cours boursiers, volumes, indicateurs économiques) via une API (ex. : Yahoo Finance).
- **Prétraitement des données :** Nettoyer et structurer les données pour une analyse fiable.
- **Analyse de performance :** Calculer des indicateurs clés (rendement, volatilité, ratio Sharpe, etc.) pour chaque actif.
- **Optimisation du portefeuille :** Implémenter un algorithme d’optimisation pour définir une allocation optimale en fonction du risque et du rendement.
- **Visualisation interactive :** Développer un dashboard interactif (avec Dash ou Streamlit) pour explorer les données et simuler différentes allocations.

## Fonctionnalités

- **Ingestion automatisée :** Téléchargement des données en direct grâce à une intégration avec des API financières.
- **Pipeline de traitement :** Traitement et transformation des données pour assurer leur qualité avant l’analyse.
- **Analyse approfondie :** Visualisations interactives et calcul d’indicateurs de performance.
- **Optimisation de portefeuille :** Simulation de réallocations basée sur des modèles d’optimisation.
- **Interface utilisateur intuitive :** Accès facile aux graphiques interactifs et aux analyses via un dashboard.


## Installation

### Prérequis

- **Python 3.8** (ou supérieur)
- Un gestionnaire d’environnements virtuels (virtualenv ou conda)
- Git (pour cloner le dépôt)

### Étapes d’installation

1. **Cloner le dépôt :**
```bash
git clone https://github.com/votre-utilisateur/projet_finance.git
cd projet_finance
```

2. **Créer et activer un environnement virtuel :**

Avec virtualenv :
```bash
python -m venv env
source env/bin/activate  # Sous Linux/Mac
env\Scripts\activate     # Sous Windows
```
Avec Conda :
```bash
conda create -n projet_finance python=3.8
conda activate projet_finance
```
3. **Installer les dépendances :**

```bash
pip install -r requirements.txt
```

## Utilisation 

**Lancer la collecte et le traitement des données :**

```bash
#Exécute le script d’ingestion pour récupérer et stocker les données financières dans le dossier data/raw
python src/ingestion.py  
```
**Prétraiter les données :**

```bash
#Nettoyez et transformez les données pour préparer l’analyse avec :
python src/preprocessing.py
```
**Analyser et optimiser le portefeuille :**

```bash
#Lancez le script d’analyse pour calculer les indicateurs de performance et simuler l’optimisation du portefeuille :
python src/analysis.py
```

**Démarrer le dashboard interactif :**

```bash
streamlit run src/dashboard.py
```
Puis, ouvrez votre navigateur à l’URL indiquée (souvent http://localhost:8501 pour Streamlit).
