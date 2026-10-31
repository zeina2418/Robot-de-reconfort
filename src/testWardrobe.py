"""Tests du deplacement du selecteur dans l'armoire.

Couvre : les mouvements N/S/E/O, le bouclage des colonnes (7 <-> 0), l'absence
de bouclage des lignes, l'ordre libre des mouvements, et le calcul d'itineraire
de WardrobeSearcher.get_route (sens le plus court).

A lancer depuis src/ :   python3 -m unittest testWardrobe -v
"""
import inspect
import unittest

from shared.Emotion import Emotion
from shared.Intensity import Intensity
from shared.Wardrobe import Wardrobe, Direction
from robot.memory import WardrobeMemory
from robot.wardrobe_searcher import WardrobeSearcher, Position
from logic.emotion_wheel import EmotionWheel

EMOTIONS = ["joie", "confiance", "peur", "surprise",
            "tristesse", "degout", "colere", "anticipation"]
INTENSITIES = ["faible", "moyenne", "forte"]
N_LINES, N_COLUMNS = 3, 8


def make_armoire(start=(1, 0)):
    """Armoire complete ; le casier [l, c] contient '<emotion>/<intensite>'."""
    casiers = []
    for line, intensity in enumerate(INTENSITIES):
        for col, emotion in enumerate(EMOTIONS):
            casiers.append({"ligne": line, "colonne": col,
                            "emotion": emotion, "intensite": intensity,
                            "objet": f"{emotion}/{intensity}"})
    return {"format": "robot-reconfort/armoire", "version": 1, "nom": "test",
            "emotions": EMOTIONS, "intensites": INTENSITIES,
            "casier_depart": list(start), "casiers": casiers}


def wardrobe_at(line, col):
    """Vraie armoire remplie, selecteur place en [line, col]."""
    wardrobe = Wardrobe()
    wardrobe.fill_wardrobe(make_armoire(start=(line, col)))
    return wardrobe


def selector(wardrobe):
    """(ligne, colonne) du selecteur reel."""
    return wardrobe.current.intensity, wardrobe.current.emotion


class FakeTrace:
    """Remplace Trace : on ne teste pas le fichier de sortie ici."""
    def __init__(self):
        self.pas = []

    def ajouter_pas(self, **kwargs):
        self.pas.append(kwargs)


def make_searcher(line, col, memory=None):
    """WardrobeSearcher dont le selecteur 'mental' est en [line, col].

    On ne passe `perception` que si le constructeur l'accepte, pour que ce
    fichier marche avant et apres cet ajout.
    """
    kwargs = dict(memory=memory or WardrobeMemory(),
                  wheel=EmotionWheel(),
                  start=Position(Emotion(col), Intensity(line)),
                  trace=FakeTrace(), demande=1, robot_position=(6, 5))
    if "perception" in inspect.signature(WardrobeSearcher.__init__).parameters:
        kwargs["perception"] = {"N": "libre", "S": "libre",
                                "E": "armoire", "O": "libre"}
    return WardrobeSearcher(**kwargs)


class TestSelectorStart(unittest.TestCase):

    def test_selector_starts_at_casier_depart(self):
        self.assertEqual(selector(wardrobe_at(1, 0)), (1, 0))
        self.assertEqual(selector(wardrobe_at(2, 5)), (2, 5))
        self.assertEqual(selector(wardrobe_at(0, 7)), (0, 7))


class TestSelectorMoves(unittest.TestCase):

    def test_east_and_west_inside_a_line(self):
        w = wardrobe_at(1, 0)
        w.move_e()
        w.move_e()
        self.assertEqual(selector(w), (1, 2))
        w.move_w()
        self.assertEqual(selector(w), (1, 1))

    def test_north_and_south(self):
        w = wardrobe_at(1, 3)
        w.move_n()
        self.assertEqual(selector(w), (0, 3))
        w.move_s()
        w.move_s()
        self.assertEqual(selector(w), (2, 3))

    def test_east_from_column_7_wraps_to_column_0(self):
        w = wardrobe_at(1, 7)
        w.move_e()
        self.assertEqual(selector(w), (1, 0))

    def test_west_from_column_0_wraps_to_column_7(self):
        w = wardrobe_at(1, 0)
        w.move_w()
        self.assertEqual(selector(w), (1, 7))

    def test_wrap_keeps_the_line(self):
        for line in range(N_LINES):
            with self.subTest(line=line):
                w = wardrobe_at(line, 7)
                w.move_e()
                self.assertEqual(selector(w), (line, 0))
                w.move_w()
                self.assertEqual(selector(w), (line, 7))

    def test_a_full_turn_returns_to_the_start(self):
        for step, name in ((Wardrobe.move_e, "E"), (Wardrobe.move_w, "O")):
            with self.subTest(direction=name):
                w = wardrobe_at(1, 3)
                for _ in range(N_COLUMNS):
                    step(w)
                self.assertEqual(selector(w), (1, 3))

    def test_lines_do_not_wrap(self):
        w = wardrobe_at(0, 2)
        with self.assertRaises(ValueError):
            w.move_n()
        self.assertEqual(selector(w), (0, 2))     # le selecteur n'a pas bouge

        w = wardrobe_at(2, 2)
        with self.assertRaises(ValueError):
            w.move_s()
        self.assertEqual(selector(w), (2, 2))


class TestMoveRoute(unittest.TestCase):

    def test_move_route_returns_emotion_and_intensity(self):
        w = wardrobe_at(1, 0)
        self.assertEqual(w.move_route([Direction.E] * 4), (4, 1))
        self.assertEqual(selector(w), (1, 4))

    def test_route_crossing_the_wrap_from_column_7(self):
        # [2,7] -> [0,1] : 2 x N puis 2 x E (en passant par la colonne 0)
        w = wardrobe_at(2, 7)
        emotion, intensity = w.move_route(
            [Direction.N, Direction.N, Direction.E, Direction.E])
        self.assertEqual((intensity, emotion), (0, 1))

    def test_route_crossing_the_wrap_from_column_0(self):
        # [1,0] -> [2,6] : 1 x S puis 2 x O (plus court que 6 x E)
        w = wardrobe_at(1, 0)
        emotion, intensity = w.move_route(
            [Direction.S, Direction.W, Direction.W])
        self.assertEqual((intensity, emotion), (2, 6))

    def test_order_of_moves_is_free_but_boxes_crossed_differ(self):
        vertical_first = [Direction.S, Direction.W, Direction.W]
        horizontal_first = [Direction.W, Direction.W, Direction.S]

        def trail(moves):
            w = wardrobe_at(1, 0)
            crossed = []
            for move in moves:
                w.move_route([move])
                crossed.append(selector(w))
            return crossed

        a, b = trail(vertical_first), trail(horizontal_first)
        self.assertEqual(a, [(2, 0), (2, 7), (2, 6)])
        self.assertEqual(b, [(1, 7), (1, 6), (2, 6)])
        self.assertEqual(a[-1], b[-1])            # meme casier d'arrivee


class TestRoutePlanning(unittest.TestCase):
    """WardrobeSearcher.get_route : itineraire vertical puis horizontal."""

    def route(self, start, target):
        searcher = make_searcher(*start)
        return searcher.get_route(
            Position(Emotion(target[1]), Intensity(target[0])))

    def test_no_move_when_already_in_front_of_the_target(self):
        self.assertEqual(self.route((1, 4), (1, 4)), [])

    def test_straight_line_east(self):
        self.assertEqual(self.route((1, 0), (1, 4)), [Direction.E] * 4)

    def test_wrap_from_column_7_to_column_1(self):
        self.assertEqual(self.route((2, 7), (0, 1)),
                         [Direction.N, Direction.N, Direction.E, Direction.E])

    def test_wrap_takes_the_short_way_west(self):
        # colonne 0 -> 6 : 2 x O et non 6 x E
        self.assertEqual(self.route((1, 0), (2, 6)),
                         [Direction.S, Direction.W, Direction.W])

    def test_neighbouring_columns_across_the_wrap(self):
        self.assertEqual(self.route((1, 0), (1, 7)), [Direction.W])
        self.assertEqual(self.route((1, 7), (1, 0)), [Direction.E])

    def test_opposite_column_goes_clockwise(self):
        # a distance 4 les deux sens se valent : le sens horaire (E) l'emporte
        self.assertEqual(self.route((1, 0), (1, 4)), [Direction.E] * 4)
        self.assertEqual(self.route((1, 4), (1, 0)), [Direction.E] * 4)

    def test_vertical_moves_come_first(self):
        self.assertEqual(self.route((0, 0), (2, 3)),
                         [Direction.S, Direction.S,
                          Direction.E, Direction.E, Direction.E])

    def test_route_is_shortest_and_reaches_target_for_every_pair(self):
        for line in range(N_LINES):
            for col in range(N_COLUMNS):
                for t_line in range(N_LINES):
                    for t_col in range(N_COLUMNS):
                        with self.subTest(src=(line, col), dst=(t_line, t_col)):
                            route = self.route((line, col), (t_line, t_col))
                            a = (t_col - col) % N_COLUMNS
                            expected = abs(t_line - line) + min(a, N_COLUMNS - a)
                            self.assertEqual(len(route), expected)

                            w = wardrobe_at(line, col)
                            if route:
                                w.move_route(route)
                            self.assertEqual(selector(w), (t_line, t_col))


if __name__ == "__main__":
    unittest.main()