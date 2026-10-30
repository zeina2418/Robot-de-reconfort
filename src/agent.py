#!/usr/bin/env python3

import sys
from pathlib import Path

# Allow imports from the existing src directory.
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import reconfort_io as rio
from shared.Map import Map
from robot.memory import Memory

def main(argv):
    if len(argv) != 5:
        print(
            "Usage: python agent.py "
            "carte.json scenario.json dossier_donnees trace_sortie.json",
            file=sys.stderr,
        )
        return 2

    chemin_carte = Path(argv[1])
    chemin_scenario = Path(argv[2])
    dossier_donnees = Path(argv[3])
    chemin_sortie = Path(argv[4])

    try:
        carte = rio.charger_carte(chemin_carte)
        scenario = rio.charger_scenario(chemin_scenario)
        dictionnaire = rio.charger_dictionnaire(
            dossier_donnees / "dictionnaire.json"
        )
        armoire = rio.charger_armoire(
            dossier_donnees / f"{scenario['armoire']}.json"
        )
    except rio.ErreurFichier as err:
        print(f"Erreur de chargement : {err}", file=sys.stderr)
        return 1

    trace = rio.Trace(
        nom_carte=carte["nom"],
        nom_scenario=scenario["nom"],
        equipe=["A completer", "A completer"],
    )

    # Temporary skeleton: the decision-making loop comes next.
    position = tuple(carte["depart_robot"])
    casier = tuple(armoire["casier_depart"])

    mental_map = Map(
    height=carte["dimensions"]["hauteur"],
    width=carte["dimensions"]["largeur"],
    )

    for demande in scenario["demandes"]:
        numero = demande["numero"]

        # Placeholder until navigation and delivery are implemented.
        trace.ajouter_pas(
            demande=numero,
            position=position,
            casier=casier,
            action="ATTENDRE",
            commentaire="Boucle principale en cours d'implementation",
        )

        trace.ajouter_livraison(
            demande=numero,
            resident=demande["resident"],
            emotion=None,
            intensite=None,
            casier_choisi=None,
            repli="aucun",
            objet=None,
            succes=False,
            motif_echec="navigation et decision non implementees",
        )

    try:
        trace.ecrire(chemin_sortie)
    except (OSError, rio.ErreurFichier) as err:
        print(f"Erreur d'ecriture de la trace : {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
