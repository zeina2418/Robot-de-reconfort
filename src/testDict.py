import unittest

from logic.dictionary import Dictionary
from shared.Emotion import Emotion
from shared.Intensity import Intensity
from shared.errors import UndeterminedEmotionError


def make_data(entries=None):
    """Small hand-written dictionary: one entry per emotion (tristesse has 2 forms)."""
    if entries is None:
        entries = [
            {"formes": ["heureux"],          "emotion": "joie",        "intensite": "moyenne"},
            {"formes": ["confiant"],         "emotion": "confiance",   "intensite": "faible"},
            {"formes": ["terrifie"],         "emotion": "peur",        "intensite": "forte"},
            {"formes": ["sidere"],           "emotion": "surprise",    "intensite": "forte"},
            {"formes": ["triste", "seule"],  "emotion": "tristesse",   "intensite": "moyenne"},
            {"formes": ["degoute"],          "emotion": "degout",      "intensite": "moyenne"},
            {"formes": ["furieux"],          "emotion": "colere",      "intensite": "forte"},
            {"formes": ["impatient"],        "emotion": "anticipation", "intensite": "faible"},
        ]
    return {"nom": "test_dictionnaire", "entrees": entries}


class TestNormaliser(unittest.TestCase):

    def test_lowercase_and_punctuation(self):
        self.assertEqual(Dictionary.normaliser("Je suis TERRIFIEE, vraiment !"),
                         ["je", "suis", "terrifiee", "vraiment"])

    def test_accents_removed(self):
        self.assertEqual(Dictionary.normaliser("Éléphant à côté"),
                         ["elephant", "a", "cote"])

    def test_apostrophe_splits_words(self):
        # section 6.1 : on découpe sur tout ce qui n'est pas une lettre
        self.assertEqual(Dictionary.normaliser("s'est allumée"),
                         ["s", "est", "allumee"])

    def test_digits_and_symbols_are_separators(self):
        self.assertEqual(Dictionary.normaliser("a1b--c"), ["a", "b", "c"])

    def test_empty_and_punctuation_only(self):
        self.assertEqual(Dictionary.normaliser(""), [])
        self.assertEqual(Dictionary.normaliser("... !?"), [])


class TestFindEmotion(unittest.TestCase):

    def setUp(self):
        self.dico = Dictionary(make_data())

    def test_one_message_per_emotion(self):
        cases = [
            ("Je suis heureux aujourd'hui", Emotion.JOIE,         Intensity.MOYENNE),
            ("Je suis confiant",            Emotion.CONFIANCE,    Intensity.FAIBLE),
            ("Je suis terrifié !",          Emotion.PEUR,         Intensity.FORTE),
            ("Je suis sidéré",              Emotion.SURPRISE,     Intensity.FORTE),
            ("Je suis triste",              Emotion.TRISTESSE,    Intensity.MOYENNE),
            ("Je suis dégoûté",             Emotion.DEGOUT,       Intensity.MOYENNE),
            ("Je suis FURIEUX",             Emotion.COLERE,       Intensity.FORTE),
            ("Je suis impatient",           Emotion.ANTICIPATION, Intensity.FAIBLE),
        ]
        for message, emotion, intensity in cases:
            with self.subTest(message=message):
                self.assertEqual(self.dico.find_emotion(message), (emotion, intensity))

    def test_every_form_of_an_entry_gives_same_result(self):
        self.assertEqual(self.dico.find_emotion("triste"),
                         self.dico.find_emotion("seule"))

    def test_first_known_word_wins(self):
        # exemple de l'énoncé : "sidere" (surprise/forte) avant "seule" (tristesse/moyenne)
        msg = "Je suis sidéré, la télévision s'est allumée toute seule."
        self.assertEqual(self.dico.find_emotion(msg),
                         (Emotion.SURPRISE, Intensity.FORTE))

    def test_first_wins_regardless_of_dictionary_order(self):
        # "seule" est avant "sidere" dans le message : c'est lui qui gagne
        msg = "Toute seule et sidérée"
        self.assertEqual(self.dico.find_emotion(msg),
                         (Emotion.TRISTESSE, Intensity.MOYENNE))

    def test_unknown_words_before_known_one_are_skipped(self):
        self.assertEqual(self.dico.find_emotion("blabla zzz furieux"),
                         (Emotion.COLERE, Intensity.FORTE))

    def test_accents_and_case_in_message_are_ignored(self):
        self.assertEqual(self.dico.find_emotion("TERRIFIÉ"),
                         (Emotion.PEUR, Intensity.FORTE))

    def test_whole_words_only(self):
        # "tristement" contient "triste" mais n'est pas dans le dictionnaire
        with self.assertRaises(UndeterminedEmotionError):
            self.dico.find_emotion("Il parlait tristement")

    def test_no_known_word_raises(self):
        with self.assertRaises(UndeterminedEmotionError):
            self.dico.find_emotion("Il fait beau et le ciel est bleu.")

    def test_empty_message_raises(self):
        for msg in ("", "   ", "!!! ..."):
            with self.subTest(msg=msg):
                with self.assertRaises(UndeterminedEmotionError):
                    self.dico.find_emotion(msg)


class TestDictionaryConstruction(unittest.TestCase):

    def test_contains(self):
        dico = Dictionary(make_data())
        self.assertIn("triste", dico)
        self.assertIn("seule", dico)
        self.assertNotIn("joyeux", dico)

    def test_unknown_emotion_rejected(self):
        data = make_data([{"formes": ["x"], "emotion": "ennui", "intensite": "faible"}])
        with self.assertRaises(ValueError):
            Dictionary(data)

    def test_unknown_intensity_rejected(self):
        data = make_data([{"formes": ["x"], "emotion": "joie", "intensite": "extreme"}])
        with self.assertRaises(ValueError):
            Dictionary(data)

    def test_same_word_in_two_entries_rejected(self):
        data = make_data([
            {"formes": ["triste"], "emotion": "tristesse", "intensite": "moyenne"},
            {"formes": ["triste"], "emotion": "joie",      "intensite": "faible"},
        ])
        with self.assertRaises(ValueError):
            Dictionary(data)

    def test_same_word_twice_in_one_entry_rejected(self):
        data = make_data([
            {"formes": ["triste", "triste"], "emotion": "tristesse", "intensite": "moyenne"},
        ])
        with self.assertRaises(ValueError):
            Dictionary(data)


if __name__ == "__main__":
    unittest.main()