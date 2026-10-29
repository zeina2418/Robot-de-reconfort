
from Map import Map


def test_initialization():
    mental_map = Map(5, 7)

    assert mental_map.height == 5
    assert mental_map.width == 7
    assert mental_map.grid == ["???????" for _ in range(5)]

    print("Initialization: OK")


def test_set_tile_type():
    mental_map = Map(3, 4)

    mental_map.set_tile_type("#", 0, 0)
    mental_map.set_tile_type(".", 1, 2)
    mental_map.set_tile_type("R", 2, 3)

    assert mental_map.tile_type(0, 0) == "#"
    assert mental_map.tile_type(1, 2) == "."
    assert mental_map.tile_type(2, 3) == "R"

    print("Updating cells: OK")


def test_display():
    mental_map = Map(3, 4)

    mental_map.set_tile_type("#", 0, 0)
    mental_map.set_tile_type("R", 1, 2)

    print("\nExpected map:")
    print("#???")
    print("??R?")
    print("????")

    print("\nActual map:")
    mental_map.display()

    assert mental_map.grid == ["#???", "??R?", "????"]

    print("Display: OK")


if __name__ == "__main__":
    test_initialization()
    test_set_tile_type()
    test_display()

    print("\nAll tests passed!")
