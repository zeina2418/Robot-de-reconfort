
#!/usr/bin/env python3

import sys
from pathlib import Path

import time

# Allow imports from the existing src directory.
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import reconfort_io as rio

from shared.Map import Map
from shared.Emotion import Emotion
from shared.Intensity import Intensity
from shared.Wardrobe import Wardrobe
from robot.memory import Memory, DictionaryMemory, WardrobeMemory
from logic.bfs import shortest_path, adjacent_goals, to_directions, exploration_goals, is_walkable, best_frontier
from perception import valider_perception
from appartement import Appartement

from logic.dictionary import Dictionary
from shared.errors import UndeterminedEmotionError

from robot.wardrobe_searcher import WardrobeSearcher, Position, EmptyWardrobeError
from logic.emotion_wheel import EmotionWheel


def main(argv):

    # Check command-line arguments.
    if len(argv) not in (5, 6):
        print("Usage: python agent.py carte.json scenario.json dossier_donnees trace.json [armoire]",
          file=sys.stderr)
        return 2

    chemin_carte = Path(argv[1])
    chemin_scenario = Path(argv[2])
    dossier_donnees = Path(argv[3])
    chemin_sortie = Path(argv[4])
    


    # --------------------------------------------------
    # 1. LOAD INPUT DATA
    # --------------------------------------------------

    try:
        carte = rio.charger_carte(chemin_carte)
        scenario = rio.charger_scenario(chemin_scenario)
        nom_armoire = argv[5] if len(argv) == 6 else scenario["armoire"]

        donnees_dictionnaire = rio.charger_dictionnaire(
            dossier_donnees / "dictionnaire.json"
        )

        donnees_armoire = rio.charger_armoire(
            (dossier_donnees / f"{nom_armoire}.json")
        )

    except rio.ErreurFichier as err:
        print(f"Erreur de chargement : {err}", file=sys.stderr)
        return 1

    appartement = Appartement(carte)

    # --------------------------------------------------
    # 2. INITIALIZE ROBOT COMPONENTS
    # --------------------------------------------------

    appartement.placer_robot(tuple(carte["depart_robot"]))

    wardrobe = Wardrobe()
    wardrobe.fill_wardrobe(donnees_armoire)

    # Create the robot's mental map.
    mental_map = Map(
        height=carte["dimensions"]["hauteur"],
        width=carte["dimensions"]["largeur"],
    )

   # Initialize the robot's mental dictionary.
    dictionary = DictionaryMemory()
    emotion_dictionary = Dictionary(donnees_dictionnaire)

    # Initialize the robot's memory.
    memory = Memory(
        mentalMap=mental_map,
        mentalWardrobe=WardrobeMemory(),
        mentalDictionnary=dictionary
    )
    memory.map.set_tile_type(".", *appartement.robot_position)

    
    
    
    
    # --------------------------------------------------
    # 3. INITIALIZE TRACE
    # --------------------------------------------------

    trace = rio.Trace(
        nom_carte=carte["nom"],
        nom_scenario=scenario["nom"],
        equipe=["A completer", "A completer"],
    )

        
    def move_robot(direction, numero, observations):
        display_mental_map()
        old_position = appartement.robot_position
        _, success = appartement.move(direction)

        trace.ajouter_pas(
            demande=numero,
            position=old_position,
            casier=wardrobe.current_casier(),
            action="AVANCER",
            argument=direction,
            perception=observations
        )
        return success
    # --------------------------------------------------
    # 4. PROCESS REQUESTS
    # --------------------------------------------------
    def receive_perception():
        observations = appartement.perceive()
        observations = valider_perception(observations)
        
        memory.update_map(
            appartement.robot_position,
            observations
        )

        return observations

    def display_mental_map():
        print("\n--- Carte mentale du robot ---")

        for row_index, row in enumerate(memory.map.grid):
            display_row = list(row)

            if row_index == appartement.robot_position[0]:
                display_row[appartement.robot_position[1]] = "R"

            print(" ".join(display_row))

        print("------------------------------\n")

    

    def navigate_to(target, numero):
        print(f"Navigating to {target}")

        while True:
            observations = receive_perception()

            # Can the robot reach a cell adjacent to the target?
            walkable = lambda pos: is_walkable(memory.map, pos)
            goals = adjacent_goals(target, walkable)

            current_position = appartement.robot_position
            path = shortest_path(current_position, goals, walkable)

            # Target reached!
            if path == [current_position]:
                return True

            # If no known path, explore one frontier.
            if path is None:
                path = best_frontier(
                    current_position,
                    target,
                    memory.map,
                    walkable
                )

                if path is None or len(path) < 2:
                    return False

            direction = to_directions(path)[0]

            if not move_robot(direction, numero, observations):
                return False
            
    def search_mental_dictionary(message, memory):
        words = Dictionary.normaliser(message)

        for word in words:
            result = memory.dictionary.lookup(word)
            if result is not None:
                
                return word, result
        
        return None

    def log_failure(numero, resident, emotion, intensite, motif):
        print(f"Request {numero} failed: {motif}")
        trace.ajouter_livraison(
            demande=numero,
            resident=resident,
            emotion=emotion.name.lower() if emotion else None,
            intensite=intensite.name.lower() if intensite else None,
            casier_choisi=None,
            repli="aucun",
            objet=None,
            succes=False,
            motif_echec=motif,
        )
    
    n = 1
    for demande in scenario["demandes"]:
        print(f"Numero de la demande : {n}")
        n = n + 1

        numero = demande["numero"]
        resident = demande["resident"]


        # TODO: Implement the decision-making loop:

        message = demande["message"]
        print(message)

        result = search_mental_dictionary(message, memory)

        if result is not None:
            word, (emotion, intensite) = result
            observations = receive_perception()
            #display_mental_map()
            
            print(f"Found '{word}' in mental dictionary!")
            print(f"Emotion: {emotion.name}")
            print(f"Intensity: {intensite.name}")
        else:
            print("New word detected... Physical dictionary needed.")
            dictionary_position = tuple(carte["dictionnaire"]["position"])
            #print(dictionary_position)
        
            print("Navigating to Dictionary.")
            if navigate_to(dictionary_position, numero):
                observations = receive_perception()
                #display_mental_map()
              

                display_mental_map()
                trace.ajouter_pas(
                    demande=numero,
                    position=appartement.robot_position,
                    casier=wardrobe.current_casier(),
                    action="CONSULTER",
                    perception=observations
                )

                try:
                    emotion, intensite = emotion_dictionary.find_emotion(message)

                    # Store the newly discovered word
                    for word in Dictionary.normaliser(message):
                        if word in emotion_dictionary:
                            memory.dictionary.record(word, emotion, intensite)
                            print(f"Word detected: '{word}'")
                            print(f"Emotion: {emotion.name}")
                            print(f"Intensity: {intensite.name}")
                            break

                except UndeterminedEmotionError as err:
                    print("Emotion could not be determined.")
                    log_failure(numero, resident, None, None, err.MOTIF)
                    continue

            else:
                print("Could not reach dictionary.")
                log_failure(numero, resident, None, None, "dictionnaire inaccessible")
                continue
        display_mental_map()
        trace.ajouter_pas(
            demande=numero,
            position=appartement.robot_position,
            casier=wardrobe.current_casier(),
            action="ATTENDRE",
            argument=None,
            perception=observations
        )

        wardrobe_position = tuple(carte["armoire"]["position"])

        print("Navigating to wardrobe...")

        if navigate_to(wardrobe_position, numero):
            #display_mental_map()
            #appartement.display()
            print("Reached wardrobe!")
        else:
            print("Could not reach wardrobe.")
            log_failure(numero, resident, emotion, intensite, "armoire inaccessible")
            continue

        
        # Initializing wardrobe searcher
        wheel = EmotionWheel()
        
    
        start_position = Position(
            emotion=Emotion(wardrobe.current.emotion),
            intensity=Intensity(wardrobe.current.intensity)
        )
        wardrobe_searcher = WardrobeSearcher(
                        memory.wardrobe,
                        wheel,
                        start_position,
                        trace,
                        numero,
                        appartement.robot_position
                    )
        print("Resident demandé :", repr(resident))
        print("Résidents disponibles :", [
            repr(r["id"]) for r in carte["residents"]
        ])
        resident_data = next(
            r for r in carte["residents"]
            if r["id"] == resident
        )

        try:
            objet = wardrobe_searcher.search(emotion, intensite, wardrobe)
            print(f"Object found: {objet}")
        except EmptyWardrobeError as err:
            print("No suitable object found.")
            log_failure(numero, resident, emotion, intensite, err.MOTIF)   # "armoire vide"
            continue

        resident_position = tuple(resident_data["position"])

        print(f"Navigating to resident {resident}...")

        if not navigate_to(resident_position, numero):
            log_failure(numero, resident, emotion, intensite, "resident inaccessible")
            continue

        observations = receive_perception()

        print(f"Giving {objet} to {resident}...")

        display_mental_map()
        trace.ajouter_pas(
            demande=numero,
            position=appartement.robot_position,
            casier=wardrobe.current_casier(),
            action="DONNER",
            argument=objet,
            perception=observations
        )

        trace.ajouter_livraison(
            demande=numero,
            resident=resident,
            emotion=emotion.name,
            intensite=intensite.name,
            casier_choisi=(
                wardrobe_searcher.current.intensity.value,
                wardrobe_searcher.current.emotion.value
            ),
            repli=wheel.fallback_label(emotion, intensite, 
                                       wardrobe_searcher.current.emotion, wardrobe_searcher.current.intensity),
            objet=objet,
            succes=True
        )

        print(f"Object {objet} delivered to {resident}!")

        # 3. Update the mental map.
        # 4. Find a path using BFS.
        # 5. Navigate to the dictionary.
        # 6. Consult the dictionary to identify emotion and intensity.
        # 7. Navigate to the wardrobe.
        # 8. Search for an acceptable compartment.
        # 9. Take the object.
        # 10. Navigate to the resident.
        # 11. Give the object to the resident.
        #
        # Record EVERY action using trace.ajouter_pas().
        # Record the delivery using trace.ajouter_livraison().

        pass

    # --------------------------------------------------
    # 5. WRITE OUTPUT TRACE
    # --------------------------------------------------

    try:
        trace.ecrire(chemin_sortie)

    except (OSError, rio.ErreurFichier) as err:
        print(f"Erreur d'ecriture de la trace : {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
