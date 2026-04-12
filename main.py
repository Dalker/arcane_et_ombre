from dataclasses import dataclass
from enum import Enum
import flet as ft


@dataclass
class ElementMixin:
    nom: str
    fonctions: str

    def __hash__(self):
        return hash(self.nom)


class Element(ElementMixin, Enum):
    FEU = "Feu", "NT"
    AIR = "Air", "NF"
    TERRE = "Terre", "ST"
    EAU = "Eau", "SF"

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
class Question:
    fonction: str  # deux lettres pour fonctions opposées
    question: str
    choix: (str, str)


@dataclass
class Modele:
    QUESTION1 = Question("SN",
                         "Vous percevez les éléments autour de vous plutôt...",
                         ("avec vos sens", "avec votre intuition"),
                         )
    QUESTION_T = (
            "Vous prenez des décisions plutôt...",
            "avec votre sentiment",
            "avec votre réflexion")
    fonctions: str = ""


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
        self.question.value = question.question
        self.reponse1.content = question.choix[0]
        self.reponse2.content = question.choix[1]
        self.effet_reponse = question.fonction

    def choix1(self, event):
        print("choix 1 was clicked", event)
        self.exclude(self.effet_reponse[1])

    def choix2(self, event):
        print("choix 2 was clicked", event)
        self.exclude(self.effet_reponse[0])

    def exclude(self, excluded):
        for element in Element.tous():
            if excluded in element.fonctions and self.elements[element]:
                self.element_row.controls.remove(self.elements[element])
                self.elements[element] = None


def main(page: ft.Page):
    page.title = "Faites votre choix..."
    modele = Modele()
    vue = Vue()
    page.add(vue)
    vue.preparer_question(modele.QUESTION1)
    page.update()


if __name__ == "__main__":
    ft.run(main)
