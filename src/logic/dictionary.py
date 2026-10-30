import unicodedata
from typing import Any, List, Tuple

from shared.Emotion import Emotion
from shared.Intensity import Intensity


class UndeterminedEmotionError(Exception):
    """No word of the message is in the dictionary"""
    def __init__(self, message: str = ""):
        super().__init__(f"Emotion indeterminee: no known word in message {message!r}")
        self.message = message


class Dictionary:

    def __init__(self, data: dict[str, Any]):
        self._name: str = data["nom"]
        self._words: dict[str, Tuple[Emotion, Intensity]] = {}

        for entry in data["entrees"]:
            try:
                value = (Emotion[entry["emotion"].upper()],
                         Intensity[entry["intensite"].upper()])
            except KeyError:
                raise ValueError(
                    f"unknown emotion or intensity in dictionary entry: "
                    f"{entry['emotion']!r} / {entry['intensite']!r}"
                ) from None
            for form in entry["formes"]:
                if form in self._words:
                    raise ValueError(f"word {form!r} appears in two dictionary entries")
                self._words[form] = value

    def __contains__(self, word: str) -> bool:
        return word in self._words

    def normaliser(texte: str) -> List[str]:
        """Decoupe un message en mots comparables au dictionnaire.

        Minuscules, accents retires, decoupage sur tout ce qui n'est pas une
        lettre. C'est exactement la regle de l'enonce, section 6.1 ;
        reimplementez-la vous-meme si vous travaillez dans un autre langage.

            >>> normaliser("Je suis TERRIFIEE, vraiment !")
            ['je', 'suis', 'terrifiee', 'vraiment']
        """
        decompose = unicodedata.normalize("NFD", texte.lower())
        sans_accents = "".join(
            c for c in decompose if unicodedata.category(c) != "Mn"
        )
        mots: List[str] = []
        courant: List[str] = []
        for caractere in sans_accents:
            if caractere.isalpha():
                courant.append(caractere)
            elif courant:
                mots.append("".join(courant))
                courant = []
        if courant:
            mots.append("".join(courant))
        return mots

    def find_emotion(self, message: str) -> Tuple[Emotion, Intensity]:
        for word in self.normaliser(message):
            result = self._words.get(word)
            if result is not None:
                return result
        raise UndeterminedEmotionError(message)
