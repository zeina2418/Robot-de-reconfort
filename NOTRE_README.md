# Robot de réconfort — ABDEL SATTAR & GUIMARAES CAIXETA SILVA

Projet de semestre — Master Informatique.

Ce projet consiste à développer un robot de réconfort capable d'aider un résident en réponse à une demande exprimant un besoin émotionnel. À partir de ses perceptions locales, le robot construit progressivement une représentation mentale de l'appartement, consulte un dictionnaire des émotions, recherche un objet adapté dans une armoire et le rapporte au résident concerné.

**Langage :** Python 3  
**Version :** Python 3.10.12

## Lancer le programme

Depuis la racine du projet, exécuter la commande suivante :

```bash
python3 src/agent.py <carte.json> <scenario.json> <dossier_donnees> <trace_sortie.json> [<armoire>]
```

Exemple :

```bash
python3 src/agent.py data/cartes/appartement_01.json data/cartes/scenario_01.json data/donnees test/sortie_agent.json
```

```bash
python3 src/agent.py data/cartes/appartement_01.json data/cartes/scenario_01.json data/donnees test/sortie_agent.json armoire_standard2
```

Les quatre arguments correspondent à :

1. **Carte** : décrit l'appartement, ses dimensions, sa grille et les emplacements des éléments.
2. **Scénario** : contient les demandes auxquelles le robot doit répondre.
3. **Dossier de données** : contient notamment les données de l'armoire et le dictionnaire des émotions.
4. **Trace de sortie** : chemin du fichier JSON dans lequel les actions et les perceptions du robot sont enregistrées.

**Dépendances :** Python 3. Le projet utilise les modules de la bibliothèque standard de Python ; aucune dépendance externe n'est nécessaire.

## Comment fonctionne le robot ?

Le programme suit une boucle de perception, de mise à jour de la mémoire, de décision et d'action.

1. **Perception :** le simulateur fournit au robot les informations concernant les quatre cases voisines : nord, sud, est et ouest. Le robot ne consulte pas directement la grille réelle de l'appartement.

2. **Construction de la carte mentale :** à partir de ses observations, le robot met à jour sa propre carte. Les cases inconnues sont progressivement remplacées par les informations découvertes : murs, cases libres, armoire, dictionnaire et résidents.

3. **Planification et déplacement :** le robot utilise l'algorithme BFS (*Breadth-First Search*) pour trouver un chemin vers ses objectifs. Lorsqu'il ne connaît pas encore de chemin vers une cible, il explore les zones accessibles de sa carte mentale afin de découvrir de nouvelles cases. La planification est recalculée à partir des nouvelles observations.

4. **Consultation du dictionnaire :** si le robot ne connaît pas le mot ou l'expression associé à la demande, il se rend au dictionnaire physique pour identifier l'émotion et son intensité. Le résultat est conservé dans sa mémoire.

5. **Recherche dans l'armoire :** à partir de l'émotion et de son intensité, le robot recherche un objet correspondant dans l'armoire à l'aide de son module de recherche.

6. **Livraison :** une fois l'objet trouvé, le robot se déplace jusqu'au résident concerné et lui remet l'objet.

Les actions et les perceptions sont enregistrées dans le fichier de trace fourni en argument.

## Tester

Le projet contient notamment un module de test consacré au BFS.

Pour lancer les tests, utiliser la commande correspondant aux fichiers de test présents dans le dépôt.

**Commande exacte à compléter après vérification de l'organisation des tests.**

Les scénarios disponibles dans `data/cartes/` et `data/scenario/` permettent également de lancer le programme avec différentes configurations d'appartement et différentes demandes.

## Organisation du code

| Fichier | Rôle |
|---|---|
| `src/agent.py` | Point d'entrée du programme et orchestration de la boucle de décision du robot. |
| `src/appartement.py` | Simulateur de l'appartement : déplacement physique du robot, validation des mouvements et perception des cases voisines. |
| `src/perception.py` | Validation des observations reçues du simulateur. |
| `src/robot/memory.py` | Gestion de la mémoire du robot et mise à jour de sa carte mentale. |
| `src/shared/Map.py` | Représentation de la carte mentale de l'appartement. |
| `src/shared/Wardrobe.py` | Représentation des données de l'armoire. |
| `src/logic/bfs.py` | Recherche de chemins avec BFS et sélection des objectifs d'exploration. |
| `src/logic/dictionary.py` | Consultation et recherche dans le dictionnaire des émotions. |
| `src/logic/emotion_wheel.py` | Gestion des émotions et de leurs intensités. |
| `src/robot/wardrobe_searcher.py` | Recherche d'un objet adapté dans l'armoire. |
| `reconfort_io.py` | Gestion des entrées et sorties du projet, notamment la trace. |
| `data/cartes/` | Cartes des appartements disponibles. |
| `data/scenario/` | Scénarios de demandes. |
| `data/donnees/` | Données du dictionnaire et de l'armoire. |

## État du projet

**Ce qui fonctionne :**
- Perception locale des quatre cases voisines.
- Construction et mise à jour progressive de la carte mentale.
- Exploration des cases inconnues accessibles.
- Recherche de chemins avec BFS.
- Navigation vers le dictionnaire, l'armoire et les résidents.
- Consultation du dictionnaire des émotions.
- Recherche d'un objet dans l'armoire.
- Livraison de l'objet au résident.
- Enregistrement des actions et des perceptions dans une trace JSON.

**Limites connues :**
- La navigation dépend des informations découvertes : le robot ne connaît pas initialement l'ensemble de l'appartement.
- La carte mentale reste une représentation construite à partir des perceptions locales ; elle peut donc être incomplète pendant l'exploration.

## Vidéo de démonstration

La vidéo de démonstration est fournie dans le fichier `demo.mp4` du scenario 01 appartement 01.

Elle présente l'exécution du programme depuis le lancement jusqu'à la livraison de l'objet au résident.