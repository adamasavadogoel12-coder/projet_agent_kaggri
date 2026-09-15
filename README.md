# Agent Kaggriculture V8


> Agent heuristique Python pour la simulation agricole Kaggriculture : cultures, animaux, ressources et marché.

Agent intelligent conçu pour optimiser la gestion d'une ferme virtuelle à l'aide de règles heuristiques.

## Présentation

Ce projet contient un agent intelligent destiné à l'environnement de simulation Kaggriculture.

L'agent observe l'état de la ferme, analyse les ressources disponibles et choisit automatiquement les meilleures actions pour progresser dans le jeu.

Le fichier principal du projet est :

```text
submission.py
```

## Fonctionnalités

- Gestion automatique des cultures.
- Achat et plantation de graines.
- Arrosage des plantes.
- Fertilisation et récolte.
- Construction et gestion des pâturages.
- Achat et placement des animaux.
- Nourrissage et entretien des animaux.
- Collecte du fertilisant.
- Vente des ressources au marché.
- Achat de terrain supplémentaire.
- Gestion des assistants.
- Attribution de tâches selon leur priorité.
- Déplacement automatique des unités.
- Gestion des actions en fin de partie.

## Stratégie de l'agent

L'agent utilise une stratégie heuristique basée sur :

- la distance entre les unités et les tâches ;
- la priorité des actions urgentes ;
- les ressources disponibles ;
- les prix du marché ;
- le nombre d'animaux et de cultures ;
- la réserve d'argent nécessaire aux prochaines actions ;
- la proximité du hangar ;
- le temps restant dans la simulation.

Les actions prioritaires sont notamment l'alimentation des animaux, l'arrosage des cultures, la récolte, la vente des ressources et la gestion des tâches urgentes.

## Technologies utilisées

- Python
- Structures de données Python
- Algorithmes heuristiques
- Simulation agricole
- Kaggriculture

Le fichier `submission.py` utilise principalement la bibliothèque standard Python.

## Structure du projet

```text
projet_agent_kaggri/
├── README.md
└── submission.py
```

## Installation

Clonez le dépôt :

```bash
git clone [https://github.com/adamasavadogoel12-coder/projet_agent_kaggri.git](https://github.com/adamasavadogoel12-coder/projet_agent_kaggri.git)
```

Accédez au dossier du projet :

```bash
cd projet_agent_kaggri
```

## Utilisation

Le fichier principal de soumission est :

```text
submission.py
```

L'agent expose la fonction principale suivante :

```python
agent(obs, config=None)
```

Cette fonction reçoit l'observation de l'environnement et retourne les actions du fermier, des assistants et du marché.

La réponse de l'agent suit la structure suivante :

```python
{
    "farmer": [...],
    "hands": [...],
    "market": [...]
}
```

Le fichier doit être utilisé dans l'environnement de simulation Kaggriculture selon les règles et le format de soumission de la compétition.

## Dépendances

Aucune bibliothèque externe n'est nécessaire pour le fonctionnement principal de cet agent.

Le code utilise notamment :

```python
from collections import defaultdict
```

## Sécurité

Ne publiez jamais dans ce dépôt :

- une clé API ;
- un mot de passe ;
- un token Hugging Face ;
- un fichier `.env` ;
- des informations confidentielles ;
- des données privées.

Ce projet n'utilise pas de clé API dans sa version actuelle.

## Limites connues

- La stratégie dépend du format des observations fourni par Kaggriculture.
- Les actions doivent respecter le schéma de l'environnement de simulation.
- Les performances peuvent varier selon la carte, les ressources et les décisions de l'adversaire.
- Les paramètres de stratégie peuvent nécessiter un ajustement pour différentes versions de la simulation.
- L'agent utilise des règles heuristiques et ne garantit pas la meilleure décision dans toutes les situations.

## Améliorations possibles

Les prochaines versions pourraient intégrer :

- une meilleure planification à long terme ;
- un système d'apprentissage automatique ;
- une analyse plus avancée des adversaires ;
- une optimisation des déplacements ;
- une gestion plus précise des ressources ;
- des tests automatisés ;
- des statistiques détaillées sur les performances ;
- une interface de visualisation des résultats.

## Auteur

**Adama Savadogo**

- GitHub : [adamasavadogoel12-coder](https://github.com/adamasavadogoel12-coder)

## Licence

Ce projet est présenté à des fins d'apprentissage, d'expérimentation et de participation à la compétition Kaggriculture.
