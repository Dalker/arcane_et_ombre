from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import NamedTuple


def oppose(fonction: str):
    """Donner la fonction opposée."""
    match fonction:
        case "I": return "E"
        case "N": return "S"
        case "T": return "F"
        case "P": return "J"
        case "E": return "I"
        case "S": return "N"
        case "F": return "T"
        case "J": return "P"
        case _:
            raise ValueError(f"La fonction {fonction} n'existe pas.")


class Element(Enum):
    FEU = auto()
    AIR = auto()
    TERRE = auto()
    EAU = auto()


@dataclass(frozen=True)
class Archetype:
    """Un aspect de personalité déterminé par une ou plusieurs fonctions."""
    nom: str
    fonctions: str
    element: Element

    def compatible(self, etat: Etat) -> bool:
        """Vérifier si l'archetype est compatible avec l'état fourni."""
        for fonction in etat.fonctions:
            if oppose(fonction) in self.fonctions:
                return False
        return True

    @classmethod
    def elements(cls):
        return (
            cls("Feu", "NT", Element.FEU),
            cls("Air", "NF", Element.AIR),
            cls("Terre", "ST", Element.TERRE),
            cls("Eau", "SF", Element.EAU),
            )


class Question(NamedTuple):
    """Une question qui déterminera une fonction parmi deux opposées."""
    fonctions: (str, str)
    question: str
    choix: (str, str)


QUESTIONS = (
    Question(fonctions=tuple("SN"),
             question="Vous percevez les éléments autour de vous plutôt...",
             choix=("avec vos sens", "avec votre intuition")),
    Question(fonctions=("F", "T"),
             question="Vous prenez des décisions plutôt...",
             choix=("avec votre sentiment", "avec votre réflexion")),
    )


@dataclass(frozen=True)
class Etat:
    """État du modèle à un moment donné."""
    fonctions: tuple[str] = field(default_factory=tuple)
    n_question: int = 0

    def ajouter_trait(self, trait: str) -> Etat:
        """Retourner un Etat avec une un trait en plus.

        Enlever le trait opposé sil était présent.
        """
        fonctions = set(self.fonctions)
        if oppose(trait) in fonctions:
            fonctions.remove(oppose(trait))
        fonctions.add(trait)
        return Etat(set(fonctions), self.n_question)

    def avancer_question(self) -> Etat:
        return Etat(self.fonctions, (self.n_question + 1) % len(QUESTIONS))


@dataclass
class Modele:
    """État actuel, passé et présent des fonctions établies."""
    etat: Etat = field(default_factory=Etat)
    prev: list[Etat] = field(default_factory=list)
    next: list[Etat] = field(default_factory=list)
    elements: tuple[Archetype] = field(default_factory=Archetype.elements)

    @property
    def question(self):
        return QUESTIONS[self.etat.n_question]

    def appliquer_choix(self, choix: int):
        """Appliquer la réponse à la question actuelle."""
        self.prev.append(self.etat)
        self.next = list()
        self.etat = self.etat \
            .ajouter_trait(self.question.fonctions[choix]) \
            .avancer_question()
