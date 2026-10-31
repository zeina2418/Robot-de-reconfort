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

Les quatre arguments correspondent à :

1. **Carte** : décrit l'appartement, ses dimensions, sa grille et les emplacements des éléments.
2. **Scénario** : contient les demandes auxquelles le robot doit répondre.
3. **Dossier de données** : contient notamment les données de l'armoire et le dictionnaire des émotions.
4. **Trace de sortie** : chemin du fichier JSON dans lequel les actions et les perceptions du robot sont enregistrées.

Tester avec une autre armoire (option de développement)

Un cinquième argument facultatif permet de remplacer l'armoire désignée par le scénario, sans modifier celui-ci. Il s'agit du nom du fichier, sans .json, qui doit se trouver dans le dossier de données :

```bash
python3 src/agent.py data/cartes/appartement_01.json data/cartes/scenario_01.json data/donnees test/sortie_agent.json armoire_standard2
```

Sans cet argument, le comportement est exactement celui du contrat d'appel (quatre arguments, armoire choisie par le scénario).

**Dépendances :** Python 3. Le projet utilise les modules de la bibliothèque standard de Python ; aucune dépendance externe n'est nécessaire.

## Comment fonctionne le robot ?

Le programme suit une boucle de perception, de mise à jour de la mémoire, de décision et d'action.

1. **Perception :** le simulateur fournit au robot les informations concernant les quatre cases voisines : nord, sud, est et ouest. Le robot ne consulte pas directement la grille réelle de l'appartement ni le champ objet des casiers : le contenu d'un casier ne se découvre qu'en plaçant le sélecteur devant.

2. **Construction de la carte mentale :** à partir de ses observations, le robot met à jour sa propre carte. Toute case non vue est supposée libre (hypothèse optimiste). Les cases inconnues sont progressivement remplacées par les informations découvertes : murs, cases libres, armoire, dictionnaire et résidents.

3. **Planification et déplacement :** le robot utilise l'algorithme BFS (*Breadth-First Search*) pour trouver un chemin vers ses objectifs. Lorsqu'il ne connaît pas encore de chemin vers une cible, il explore les zones accessibles de sa carte mentale afin de découvrir de nouvelles cases. La planification est recalculée à partir des nouvelles observations.Si le BFS échoue sur la carte mentale, il n'existe aucun chemin dans la réalité (la carte mentale contient au moins autant de cases libres que la réalité) : le résident est déclaré inaccessible.

4. **Consultation du dictionnaire :** le robot se rend au dictionnaire physique et exécute CONSULTER. Le message est normalisé (minuscules, sans accents, découpé sur tout ce qui n'est pas une lettre) et le premier mot reconnu donne l'émotion et l'intensité. Le robot mémorise les mots appris, y compris ceux qu'il sait absents, et ne retourne au dictionnaire que lorsqu'un mot du message pourrait encore y figurer.

5. **Recherche dans l'armoire :** à partir de l'émotion et de son intensité, le robot recherche un objet correspondant dans l'armoire à l'aide de son module de recherche. On calcule la liste des casiers candidats (distance sur la roue de Plutchik ≤ 2, triés par distance, écart d'intensité, intensité la plus faible, sens horaire). Le sélecteur se déplace avec CHERCHER, le robot lit chaque casier devant lequel il passe, mémorise son contenu et prend l'objet du premier candidat garni dans l'ordre de priorité, même s'il en a croisé un autre garni en chemin. Les colonnes bouclent, les lignes non.

6. **Livraison :** une fois l'objet trouvé, le robot se déplace jusqu'au résident concerné et lui remet l'objet. La demande suivante commence là où il se trouve ; la carte mentale, la position du sélecteur et les casiers vus persistent d'une demande à l'autre.

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
- Lecture du dictionnaire : premier mot reconnu, mémorisation des mots appris et des mots absents.
- Fouille de l'armoire selon l'ordre de priorité de la section 6.2, avec mémorisation de tous les casiers traversés.
- avec l'étiquette repli et des échecs avec leur motif_echec.
- Enregistrement des actions et des perceptions dans une trace JSON.

**Limites connues :**
- La navigation dépend des informations découvertes : le robot ne connaît pas initialement l'ensemble de l'appartement.
- La carte mentale reste une représentation construite à partir des perceptions locales ; elle peut donc être incomplète pendant l'exploration.

## Vidéo de démonstration

La vidéo de démonstration est fournie dans le fichier `demo.mp4` du scenario 01 appartement 01.

Elle présente l'exécution du programme depuis le lancement jusqu'à la livraison de l'objet au résident.