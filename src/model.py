"""Modèle de l'application.

Ce module exporte les Modele, Etat, Archetype, Element et la fonction oppose.

 - Element: Enum des éléments FEU, AIR, TERRE, EAU
 - Archetype(nom: str, traits: str, element: Element)
 - Etat(traits: tuple[str], n_question: int)
"""
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
    def elements(cls) -> tuple[Archetype]:
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
    """État du modèle à un moment donné, accessible par la Vue.

    Les données sont délibérément simples pour pouvoir facilement stocker
    plusieurs Etat dans une mémoire de type "<- prev, next ->".
    """
    traits: tuple[str] = ()
    n_question: int = 0

    @property
    def question(self):
        return QUESTIONS[self.n_question].question

    @property
    def choix(self):
        return QUESTIONS[self.n_question].choix

    def compatible(self, archetype: Archetype) -> bool:
        """Vérifier si l'archetype est compatible."""
        for trait in archetype.traits:
            if oppose(trait) in self.traits:
                return False
        return True

    def avec_prochaine_question(self) -> Etat:
        return Etat(self.traits, (self.n_question + 1) % len(QUESTIONS))

    def avec_trait(self, new_trait: str) -> Etat:
        return Etat(set(self.traits)
                    .union({new_trait})
                    .difference({oppose(new_trait)}),
                    self.n_question)


@dataclass
class Modele:
    """État actuel, passé et présent des traits établies."""
    etat: Etat = field(default_factory=Etat)
    elements: tuple[Archetype] = field(default_factory=Archetype.elements)

    def appliquer_choix(self, n_choix: int):
        """Appliquer la réponse à la question actuelle."""
        new_trait = QUESTIONS[self.etat.n_question].traits[n_choix]
        self.etat = self.etat \
            .avec_trait(new_trait) \
            .avec_prochaine_question()
