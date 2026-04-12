from dataclasses import dataclass
from enum import Enum
import flet as ft


@dataclass
class ElementMixin:
    nom: str
    attribut_N: bool
    attribut_T: bool

    def __hash__(self):
        return hash(self.nom)


class Element(ElementMixin, Enum):
    FEU = "Feu", True, True
    AIR = "Air", True, False
    TERRE = "Terre", False, True
    EAU = "Eau", False, False

    @classmethod
    def tous(cls):
        return cls.FEU, cls.AIR, cls.TERRE, cls.EAU


@ft.control
class ElementText(ft.Text):
    element: Element | None = None

    def init(self):
        self.color = ft.Colors.WHITE
        self.value = self.element.nom


@dataclass
class Modele:
    QUESTION_N = (
            "Vous percevez les éléments autour de vous plutôt...",
            "avec vos sens",
            "avec votre intuition")
    QUESTION_T = (
            "Vous prenez des décisions plutôt...",
            "avec votre sentiment",
            "avec votre réflexion")
    attribut_N: bool | None = None
    attribut_T: bool | None = None


@ft.control
class Vue(ft.Container):

    def init(self):
        self.width = 400
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20

        self.question = ft.Text(color=ft.Colors.WHITE)
        self.reponse1 = ft.Button(content="", on_click=self.choix1)
        self.reponse2 = ft.Button(content="", on_click=self.choix2)

        self.element_row = ft.Row()
        self.elements = {}
        for element in Element.tous():
            etext = ElementText(element=element)
            self.element_row.controls.append(etext)
            self.elements[element] = etext

        self.content = ft.Column(controls=[
                    self.question,
                    ft.Row(controls=[
                        self.reponse1,
                        self.reponse2,
                        ]),
                    self.element_row,
                    ])

    def preparer_question(self, question: tuple[str]):
        self.question.value = question[0]
        self.reponse1.content = question[1]
        self.reponse2.content = question[2]

    def choix1(self, event):
        print("choix 1 was clicked", event)
        for element in Element.tous():
            if element.attribut_N and self.elements[element]:
                self.element_row.controls.remove(self.elements[element])
                self.elements[element] = None

    def choix2(self, event):
        print("choix 2 was clicked", event)


def main(page: ft.Page):
    page.title = "Faites votre choix..."
    modele = Modele()
    vue = Vue()
    page.add(vue)
    vue.preparer_question(modele.QUESTION_N)
    page.update()


if __name__ == "__main__":
    ft.run(main)
