from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import NamedTuple


def oppose(trait: str):
    """Donner la trait opposée."""
    match trait:
        case "I": return "E"
        case "N": return "S"
        case "T": return "F"
        case "P": return "J"
        case "E": return "I"
        case "S": return "N"
        case "F": return "T"
        case "J": return "P"
        case _:
            raise ValueError(f"La trait {trait} n'existe pas.")


class Element(Enum):
    FEU = auto()
    AIR = auto()
    TERRE = auto()
    EAU = auto()


@dataclass(frozen=True)
class Archetype:
    """Un aspect de personalité déterminé par une ou plusieurs traits."""
    nom: str
    traits: str
    element: Element

    @classmethod
    def elements(cls):
        return (
            cls("Feu", "NT", Element.FEU),
            cls("Air", "NF", Element.AIR),
            cls("Terre", "ST", Element.TERRE),
            cls("Eau", "SF", Element.EAU),
            )


class Question(NamedTuple):
    """Une question qui déterminera une trait parmi deux opposées."""
    traits: (str, str)
    question: str
    choix: (str, str)


QUESTIONS = (
    Question(traits=tuple("SN"),
             question="Vous percevez les éléments autour de vous plutôt...",
             choix=("avec vos sens", "avec votre intuition")),
    Question(traits=("F", "T"),
             question="Vous prenez des décisions plutôt...",
             choix=("avec votre sentiment", "avec votre réflexion")),
    )


class Etat(NamedTuple):
    """État du modèle à un moment donné."""
    traits: tuple[str] = ()
    n_question: int = 0

    def compatible(self, archetype: Archetype) -> bool:
        """Vérifier si l'archetype est compatible."""
        for trait in archetype.traits:
            if oppose(trait) in self.traits:
                return False
        return True


@dataclass
class Modele:
    """État actuel, passé et présent des traits établies."""
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
        new_trait = self.question.traits[choix]
        traits, n_question = self.etat
        self.etat = Etat(
                set(traits).union({new_trait}).difference({oppose(new_trait)}),
                (n_question + 1) % len(QUESTIONS)
                )
        return
        self.etat = self.etat \
            .ajouter_trait(self.question.traits[choix]) \
            .avancer_question()
