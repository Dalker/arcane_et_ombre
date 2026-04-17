from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Sequence, NamedTuple
import flet as ft


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

    @classmethod
    def elements(cls):
        return (
            cls("Feu", "NT", Element.FEU),
            cls("Air", "NF", Element.AIR),
            cls("Terre", "ST", Element.TERRE),
            cls("Eau", "SF", Element.EAU),
            )

    def compatible(self, etat: Etat) -> bool:
        """Vérifier si l'archetype est compatible avec l'état fourni."""
        for fonction in etat.fonctions:
            if oppose(fonction) in self.fonctions:
                return False
        return True


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


class Etat(NamedTuple):
    """État du modèle à un moment donné."""
    fonctions: tuple = ()  # field(default_factory=tuple)
    n_question: int = 0

    def __add__(self, item: str | int):
        """Retourner un nouvel état modifié."""
        if isinstance(item, str):
            fonctions = set(self.fonctions)
            if oppose(item) in fonctions:
                fonctions.remove(oppose(item))
            fonctions.add(item)
            return Etat(set(fonctions), self.n_question)
        elif isinstance(item, int):
            return Etat(self.fonctions,
                        (self.n_question + item) % len(QUESTIONS))
        else:
            raise ValueError(f"can't add {item} to Etat")

    def __sub__(self, item: int):
        """Retourner un nouvel état modifié."""
        if isinstance(item, int):
            return Etat(self.fonctions,
                        (self.n_question - item) % len(QUESTIONS))
        else:
            raise ValueError(f"can't add {item} to Etat")


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

    def add(self, item: str | int):
        """Avancer l'état actuel en ajoutant un item (fonction ou n_quest)."""
        self.prev.append(self.etat)
        self.next = list()
        self.etat += item
        self.etat += 1

    def gerer_choix(self, choix: int):
        self.add(self.question.fonctions[choix])


class ArchetypeWidget(ft.Text):
    """Vue d'un Archetype."""
    archetype: Archetype

    COULEUR = {
        Element.FEU: ft.Colors.RED,
        Element.AIR: ft.Colors.GREEN,
        Element.TERRE: ft.Colors.BROWN,
        Element.EAU: ft.Colors.BLUE,
    }

    def __init__(self, archetype: Archetype):
        super().__init__()
        self.archetype = archetype
        self.value = self.archetype.nom

    def update(self, etat: Etat):
        if self.archetype.compatible(etat):
            self.color = self.COULEUR[self.archetype.element]
        else:
            self.color = "#333333"


@ft.control
class Vue(ft.Container):
    callback_gauche: Callable | None = None
    callback_droite: Callable | None = None

    def init(self):
        self.width = 400
        self.alignment = ft.Alignment.CENTER
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20

        self.question = ft.Text(color=ft.Colors.WHITE)
        self.reponses = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                )
        for n in range(2):
            self.reponses.controls.append(
                ft.Button(content="", on_click=lambda _, choix=n:
                          self._gerer_choix(choix)))
        self.element_row = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
                spacing=20,
                )
        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.question,
                    self.reponses,
                    self.element_row,
                    ])

    def post_init(self, page: ft.Page, elements: Sequence[Element],
                  gerer_choix: Callable[[int], None]):
        self._gerer_choix = gerer_choix
        page.title = "Faites votre choix..."
        page.theme_mode = ft.ThemeMode.DARK
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.add(self)
        for element in elements:
            widget = ArchetypeWidget(archetype=element)
            self.element_row.controls.append(widget)
        page.update()

    def update(self, question: Question, etat: Etat):
        for element_widget in self.element_row.controls:
            element_widget.update(etat)
        self.question.value = question.question
        for n in range(2):
            self.reponses.controls[n].content = question.choix[n]
        super().update()

    def finaliser(self):
        self.question.value = "FINI!"
        self.reponses.controls = []

    def exclude(self, excluded):
        for element in Archetype.elements():
            if excluded in element.fonctions and self.elements[element]:
                self.elements[element].disable()


class Controle:
    """Gérer les communications entre modèle et vue."""
    modele: Modele
    vue: Vue

    def __init__(self, page: ft.Page):
        """Mettre en place les canaux de communication."""
        self.modele = Modele()
        self.vue = Vue()
        self.vue.post_init(page, self.modele.elements, self.gerer_choix)
        self.vue.update(self.modele.question, self.modele.etat)

    def gerer_choix(self, choix: int):
        self.modele.gerer_choix(choix)
        self.vue.update(self.modele.question, self.modele.etat)


if __name__ == "__main__":
    ft.run(Controle)
