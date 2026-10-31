"""Tests de la regle de repli, sur tout le flux : remplissage de l'armoire reelle,
fouille par WardrobeSearcher, memoire du robot.

Couvre : casier exact garni ; casier vide avec repli en intensite ; colonne
entiere vide avec repli sur une voisine ; aucun casier garni a distance <= 2.

A lancer depuis src/ :   python3 -m unittest testWardrobeFlow -v
"""
import inspect
import unittest

from shared.Emotion import Emotion
from shared.Intensity import Intensity
from shared.Wardrobe import Wardrobe, BoxState
from shared.errors import EmptyWardrobeError
from robot.memory import WardrobeMemory
from robot.wardrobe_searcher import WardrobeSearcher, Position
from logic.emotion_wheel import EmotionWheel

EMOTIONS = ["joie", "confiance", "peur", "surprise",
            "tristesse", "degout", "colere", "anticipation"]
INTENSITIES = ["faible", "moyenne", "forte"]


def make_armoire(empty=(), start=(1, 0)):
    """Armoire complete ; le casier [l, c] contient '<emotion>/<intensite>',
    sauf ceux de `empty` (ensemble de (ligne, colonne)) qui valent null."""
    casiers = []
    for line, intensity in enumerate(INTENSITIES):
        for col, emotion in enumerate(EMOTIONS):
            casiers.append({
                "ligne": line, "colonne": col,
                "emotion": emotion, "intensite": intensity,
                "objet": None if (line, col) in empty else f"{emotion}/{intensity}",
            })
    return {"format": "robot-reconfort/armoire", "version": 1, "nom": "test",
            "emotions": EMOTIONS, "intensites": INTENSITIES,
            "casier_depart": list(start), "casiers": casiers}


def empty_columns(*cols):
    """Tous les casiers (3 intensites) des colonnes donnees."""
    return {(line, col) for line in range(3) for col in cols}


class FakeTrace:
    """Remplace Trace : on garde les pas pour les inspecter."""
    def __init__(self):
        self.pas = []

    def ajouter_pas(self, **kwargs):
        self.pas.append(kwargs)

    def actions(self):
        return [p["action"] for p in self.pas]


class Scenario:
    """Une armoire reelle + un robot (memoire, chercheur) pret a fouiller."""

    def __init__(self, empty=(), start=(1, 0)):
        self.wardrobe = Wardrobe()
        self.wardrobe.fill_wardrobe(make_armoire(empty, start))
        self.memory = WardrobeMemory()
        self.wheel = EmotionWheel()
        self.trace = FakeTrace()

        kwargs = dict(memory=self.memory, wheel=self.wheel,
                      start=Position(Emotion(start[1]), Intensity(start[0])),
                      trace=self.trace, demande=1, robot_position=(6, 5))
        # `perception` n'est passe que si le constructeur l'accepte
        if "perception" in inspect.signature(WardrobeSearcher.__init__).parameters:
            kwargs["perception"] = {"N": "libre", "S": "libre",
                                    "E": "armoire", "O": "libre"}
        self.searcher = WardrobeSearcher(**kwargs)

    def ask(self, emotion, intensity):
        return self.searcher.search(emotion, intensity, self.wardrobe)

    def label(self, emotion, intensity):
        """Etiquette `repli` de la trace, d'apres le casier ou on s'est arrete."""
        found = self.searcher.current
        return self.wheel.fallback_label(emotion, intensity,
                                         found.emotion, found.intensity)

    def selector(self):
        return (self.wardrobe.current.intensity, self.wardrobe.current.emotion)

    def real_object(self, line, col):
        return self.wardrobe._boxes[line][col].object

    def real_state(self, line, col):
        return self.wardrobe._boxes[line][col].state


class FallbackTestCase(unittest.TestCase):

    def assertHigherPriorityBoxesWereSeenEmpty(self, scenario, emotion, intensity):
        """Un repli n'est legitime que si tous les casiers plus prioritaires
        ont ete vus vides par le robot (memoire a l'etat EMPTY)."""
        chosen = scenario.searcher.current
        for e, i in scenario.wheel.candidates(emotion, intensity):
            if (e, i) == (chosen.emotion, chosen.intensity):
                return
            with self.subTest(prioritaire=(e.name, i.name)):
                self.assertEqual(scenario.memory.state_at(e, i), BoxState.EMPTY)
        self.fail("le casier choisi n'est pas dans la liste des candidats")


class TestExactBox(FallbackTestCase):

    def test_exact_box_filled_is_taken(self):
        s = Scenario()
        obj = s.ask(Emotion.TRISTESSE, Intensity.MOYENNE)
        self.assertEqual(obj, "tristesse/moyenne")
        self.assertEqual(s.selector(), (1, 4))
        self.assertEqual(s.label(Emotion.TRISTESSE, Intensity.MOYENNE), "aucun")

    def test_exact_box_is_empty_afterwards_in_reality_and_in_memory(self):
        s = Scenario()
        s.ask(Emotion.TRISTESSE, Intensity.MOYENNE)
        self.assertEqual(s.real_state(1, 4), BoxState.EMPTY)
        self.assertEqual(s.memory.state_at(Emotion.TRISTESSE, Intensity.MOYENNE),
                         BoxState.EMPTY)

    def test_only_the_visited_boxes_are_known(self):
        s = Scenario()
        s.ask(Emotion.TRISTESSE, Intensity.MOYENNE)
        # un casier jamais regarde reste inconnu pour le robot
        self.assertEqual(s.memory.state_at(Emotion.PEUR, Intensity.FORTE),
                         BoxState.UNKNOWN)

    def test_trace_ends_with_prendre_of_the_object(self):
        s = Scenario()
        obj = s.ask(Emotion.TRISTESSE, Intensity.MOYENNE)
        last = s.trace.pas[-1]
        self.assertEqual(last["action"], "PRENDRE")
        self.assertEqual(last["argument"], obj)
        self.assertEqual(s.trace.actions().count("CHERCHER"), 4)  # [1,0] -> [1,4]


class TestIntensityFallback(FallbackTestCase):

    def test_empty_box_falls_back_on_lower_intensity_first(self):
        s = Scenario(empty={(1, 4)})
        obj = s.ask(Emotion.TRISTESSE, Intensity.MOYENNE)
        self.assertEqual(obj, "tristesse/faible")
        self.assertEqual(s.label(Emotion.TRISTESSE, Intensity.MOYENNE), "intensite")
        self.assertHigherPriorityBoxesWereSeenEmpty(
            s, Emotion.TRISTESSE, Intensity.MOYENNE)

    def test_then_higher_intensity_when_lower_is_empty_too(self):
        s = Scenario(empty={(1, 4), (0, 4)})
        obj = s.ask(Emotion.TRISTESSE, Intensity.MOYENNE)
        self.assertEqual(obj, "tristesse/forte")
        self.assertEqual(s.label(Emotion.TRISTESSE, Intensity.MOYENNE), "intensite")

    def test_forte_request_tries_moyenne_before_faible(self):
        s = Scenario(empty={(2, 4)})
        self.assertEqual(s.ask(Emotion.TRISTESSE, Intensity.FORTE),
                         "tristesse/moyenne")

        s = Scenario(empty={(2, 4), (1, 4)})
        self.assertEqual(s.ask(Emotion.TRISTESSE, Intensity.FORTE),
                         "tristesse/faible")

    def test_same_emotion_wins_over_a_neighbour_with_the_exact_intensity(self):
        # tristesse/moyenne vide : tristesse/faible passe avant degout/moyenne
        s = Scenario(empty={(1, 4)})
        self.assertEqual(s.ask(Emotion.TRISTESSE, Intensity.MOYENNE),
                         "tristesse/faible")
        self.assertEqual(s.real_object(1, 5), "degout/moyenne")   # intact


class TestNeighbourFallback(FallbackTestCase):

    def test_empty_column_falls_back_on_clockwise_neighbour(self):
        # colonne surprise entierement vide, demande surprise/forte
        s = Scenario(empty=empty_columns(3))
        obj = s.ask(Emotion.SURPRISE, Intensity.FORTE)
        self.assertEqual(obj, "tristesse/forte")
        self.assertEqual(s.selector(), (2, 4))
        self.assertEqual(s.label(Emotion.SURPRISE, Intensity.FORTE), "voisine_1")
        self.assertHigherPriorityBoxesWereSeenEmpty(
            s, Emotion.SURPRISE, Intensity.FORTE)

    def test_clockwise_neighbour_wins_over_anticlockwise_one(self):
        s = Scenario(empty=empty_columns(3))
        s.ask(Emotion.SURPRISE, Intensity.FORTE)
        # peur/forte (sens antihoraire) etait garni et le robot est passe devant
        self.assertEqual(s.real_object(2, 2), "peur/forte")
        self.assertEqual(s.real_state(2, 2), BoxState.FILLED)

    def test_anticlockwise_neighbour_when_clockwise_column_is_empty(self):
        s = Scenario(empty=empty_columns(3, 4))
        obj = s.ask(Emotion.SURPRISE, Intensity.FORTE)
        self.assertEqual(obj, "peur/forte")
        self.assertEqual(s.label(Emotion.SURPRISE, Intensity.FORTE), "voisine_1")

    def test_boxes_crossed_on_the_way_are_recorded_as_seen(self):
        # [1,0] -> [2,3] passe devant [1,0], [2,0], [2,1] et [2,2] : le robot les a vus
        s = Scenario(empty=empty_columns(3))
        s.ask(Emotion.SURPRISE, Intensity.FORTE)
        self.assertEqual(s.memory.state_at(Emotion.JOIE, Intensity.MOYENNE),
                         BoxState.FILLED)
        self.assertEqual(s.memory.state_at(Emotion.PEUR, Intensity.FORTE),
                         BoxState.FILLED)
        # ... mais pas ceux devant lesquels il n'est jamais passe
        self.assertEqual(s.memory.state_at(Emotion.COLERE, Intensity.FAIBLE),
                         BoxState.UNKNOWN)

    def test_neighbour_search_keeps_the_closest_intensity(self):
        # les deux voisines (tristesse, peur) n'ont plus que de la 'faible' :
        # on prend la plus proche en intensite parmi les restantes
        empty = empty_columns(3) | {(2, 4), (1, 4), (2, 2), (1, 2)}
        s = Scenario(empty=empty)
        obj = s.ask(Emotion.SURPRISE, Intensity.FORTE)
        self.assertEqual(obj, "tristesse/faible")

    def test_fallback_on_distance_2_labelled_voisine_2(self):
        # joie/faible : joie, confiance et anticipation (distance <= 1) vides
        s = Scenario(empty=empty_columns(0, 1, 7))
        obj = s.ask(Emotion.JOIE, Intensity.FAIBLE)
        self.assertEqual(obj, "peur/faible")                 # horaire avant colere
        self.assertEqual(s.selector(), (0, 2))
        self.assertEqual(s.label(Emotion.JOIE, Intensity.FAIBLE), "voisine_2")
        self.assertHigherPriorityBoxesWereSeenEmpty(
            s, Emotion.JOIE, Intensity.FAIBLE)

    def test_search_cost_matches_the_worked_example(self):
        # 9 mouvements pour surprise/forte avec la colonne surprise vide
        s = Scenario(empty=empty_columns(3))
        s.ask(Emotion.SURPRISE, Intensity.FORTE)
        self.assertEqual(s.trace.actions().count("CHERCHER"), 9)
        self.assertEqual(s.trace.actions().count("PRENDRE"), 1)


class TestNothingWithinDistanceTwo(FallbackTestCase):

    def setUp(self):
        # tout ce qui est a distance <= 2 de la joie est vide ; le reste est plein
        self.s = Scenario(empty=empty_columns(0, 1, 2, 6, 7))

    def test_raises_when_every_candidate_is_empty(self):
        with self.assertRaises(EmptyWardrobeError):
            self.s.ask(Emotion.JOIE, Intensity.FAIBLE)

    def test_every_candidate_was_actually_looked_at(self):
        with self.assertRaises(EmptyWardrobeError):
            self.s.ask(Emotion.JOIE, Intensity.FAIBLE)
        candidates = self.s.wheel.candidates(Emotion.JOIE, Intensity.FAIBLE)
        self.assertEqual(len(candidates), 15)
        for e, i in candidates:
            with self.subTest(casier=(e.name, i.name)):
                self.assertEqual(self.s.memory.state_at(e, i), BoxState.EMPTY)

    def test_boxes_at_distance_3_and_4_are_never_used(self):
        with self.assertRaises(EmptyWardrobeError):
            self.s.ask(Emotion.JOIE, Intensity.FAIBLE)
        for col in (3, 4, 5):
            for line in range(3):
                with self.subTest(casier=(line, col)):
                    self.assertEqual(self.s.real_state(line, col), BoxState.FILLED)

    def test_no_prendre_step_is_written(self):
        with self.assertRaises(EmptyWardrobeError):
            self.s.ask(Emotion.JOIE, Intensity.FAIBLE)
        self.assertNotIn("PRENDRE", self.s.trace.actions())


class TestSeveralRequests(FallbackTestCase):

    def test_a_taken_object_empties_the_box_for_the_next_request(self):
        s = Scenario()
        got = [s.ask(Emotion.JOIE, Intensity.FAIBLE) for _ in range(4)]
        self.assertEqual(got, ["joie/faible", "joie/moyenne", "joie/forte",
                               "confiance/faible"])
        self.assertEqual(s.label(Emotion.JOIE, Intensity.FAIBLE), "voisine_1")

    def test_second_request_does_not_revisit_boxes_known_empty(self):
        s = Scenario()
        s.ask(Emotion.TRISTESSE, Intensity.MOYENNE)
        before = s.trace.actions().count("CHERCHER")
        self.assertEqual(s.ask(Emotion.TRISTESSE, Intensity.MOYENNE),
                         "tristesse/faible")
        # [1,4] est vide et connu : un seul mouvement (N) suffit
        self.assertEqual(s.trace.actions().count("CHERCHER") - before, 1)


if __name__ == "__main__":
    unittest.main()