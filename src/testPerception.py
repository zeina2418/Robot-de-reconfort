from perception import valider_perception

# Test 1: valid observations
observations = {
    "N": "mur",
    "S": "libre",
    "E": "resident",
    "O": "armoire",
}

print("Test 1 — valid observations")
print(valider_perception(observations))

# Test 2: missing direction
print("\nTest 2 — missing direction")
try:
    valider_perception({"N": "mur", "S": "libre", "E": "resident"})
except ValueError as erreur:
    print("Correctly rejected:", erreur)

# Test 3: invalid cell type
print("\nTest 3 — invalid cell type")
try:
    valider_perception({
        "N": "mur",
        "S": "libre",
        "E": "dragon",
        "O": "armoire",
    })
except ValueError as erreur:
    print("Correctly rejected:", erreur)