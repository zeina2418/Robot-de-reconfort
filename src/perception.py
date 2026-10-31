
# les quatre directions le robot peut observer
DIRECTIONS = ("N", "S", "E", "O")

TYPES_CASES = {
    "mur",
    "libre",
    "armoire",
    "dictionnaire",
    "resident",
}

""" voici un example d'une observation observations = {
    "N": "mur",
    "S": "libre",
    "E": "resident",
    "O": "armoire"
}"""
def valider_perception(observations):
    """Vérifie que les quatre observations locales sont valides."""
    if set(observations) != set(DIRECTIONS):
        raise ValueError("La perception doit contenir N, S, E et O.")

    if any(type_case not in TYPES_CASES
           for type_case in observations.values()):
        raise ValueError("Type de case inconnu dans la perception.")

    return observations
