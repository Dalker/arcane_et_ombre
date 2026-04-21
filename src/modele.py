"""Modèle de l'application.

Ce module exporte les Modele, Etat, Archetype, Element et la fonction oppose.

 - Element: Enum des éléments FEU, AIR, TERRE, EAU
 - Archetype(nom: str, traits: str, element: Element)
 - Etat(traits: tuple[str], n_question: int)
 
 Toutes les classes définies dans ce module ont des instances immuables.
"""
from __future__ import annotations
from enum import StrEnum
from dataclasses import dataclass, field
from typing import NamedTuple


class Element(StrEnum):
    FEU = "feu"
    AIR = "air"
    TERRE = "terre"
    EAU = "eau"


class Archetype(NamedTuple):
    """Un aspect de personalité déterminé par une ou plusieurs traits."""
    traits: str
    nom: str

    ELEMENTS = {
            "NT": Element.FEU,
            "NF": Element.AIR,
            "ST": Element.TERRE,
            "SF": Element.EAU,
            }

    ARCANES = {
            "ENTJ": "Fou",
            "INTJ": "Roue",
            "ENTP": "Ermite",
            "INTP": "Soleil",
            "ENFJ": "Empereur",
            "INFJ": "Tempérance",
            "ENFP": "Pape",
            "INFP": "Diable",
            "ESTJ": "Papesse",
            "ISTJ": "Pendu",
            "ESTP": "Chariot",
            "ISTP": "Étoile",
            "ESFJ": "Magicien",
            "ISFJ": "Justice",
            "ESFP": "Force",
            "ISFP": "Lune",
            }

    @property
    def element(self) -> Element:
        """Retourner l'élément correspondant aux traits."""
        for element in self.ELEMENTS:
            if len(set(element).intersection(self.traits)) == 2:
                return self.ELEMENTS[element]
        raise ValueError(
                "Un élément nécessite une perception et un jugement")

    @classmethod
    def elements(cls) -> tuple[Archetype, ...]:
        return tuple(cls(traits, nom=element.value)
                     for traits, element in cls.ELEMENTS.items())

    @classmethod
    def arcanes(cls) -> tuple[Archetype, ...]:
        return tuple(cls(traits, nom)
                     for traits, nom in cls.ARCANES.items())


class Decision(NamedTuple):
    """Question/réponses qui détermineront un trait parmi deux opposées."""
    question: str
    reponses: tuple[str, str]
    resultats: tuple[str, str]

    @classmethod
    def sequence(cls) -> tuple[Decision, ...]:
        """Retourner la séquence des décisions à prendre, dans l'ordre."""
        return (
            Decision(
                 question="Vous percevez les éléments autour de vous plutôt...",
                 reponses=("avec vos sens", "avec votre intuition"),
                 resultats=("S", "N"),
                 ),
            Decision(
                 question="Vous prenez des décisions plutôt...",
                 reponses=("avec votre sentiment", "avec votre réflexion"),
                 resultats=("F", "T"),
                 ),
        )


@dataclass(frozen=True)
class Traits:
    """Ensemble de traits de personnalité déjà déterminés."""
    _traits: set[str] = field(default_factory=set)

    @staticmethod
    def oppose(trait: str):
        """Donner la trait opposé."""
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

    def __add__(self, new_trait: str) -> Traits:
        return Traits(self._traits
                      .union({new_trait})
                      .difference({self.oppose(new_trait)}))

    def compatibles(self, archetype: Archetype) -> bool:
        """Vérifier si l'archetype est compatible avec les traits connus."""
        for trait in archetype.traits:
            if self.oppose(trait) in self._traits:
                return False
        return True


@dataclass(frozen=True)
class Etat:
    """État du modèle à un moment donné, accessible par la Vue."""
    decision: Decision | None
    traits: Traits = field(default_factory=Traits)

    @property
    def question(self):
        return self.decision.question if self.decision else "FINI!"

    @property
    def reponses(self):
        return self.decision.reponses if self.decision else ("", "")

    def compatible(self, archetype: Archetype) -> bool:
        return self.traits.compatibles(archetype)
