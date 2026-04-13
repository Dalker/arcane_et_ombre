from dataclasses import dataclass, field
from enum import Enum
import flet as ft


@dataclass
class Question:
    fonction: str  # deux lettres pour fonctions opposées
    question: str
    choix: (str, str)

    @classmethod
    def get_questions(cls):
        return list(reversed((
                Question("SN",
                         "Vous percevez les éléments autour de vous plutôt...",
                         ("avec vos sens", "avec votre intuition")),
                Question("FT",
                         "Vous prenez des décisions plutôt...",
                         ("avec votre sentiment", "avec votre réflexion")),
                )))


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
class ModeleAncien:
    QUESTION1 = Question("SN",
                         "Vous percevez les éléments autour de vous plutôt...",
                         ("avec vos sens", "avec votre intuition"),
                         )
    QUESTION_T = (
            "Vous prenez des décisions plutôt...",
            "avec votre sentiment",
            "avec votre réflexion")
    fonctions: str = ""


@dataclass
class Modele:
    questions: list[Question] = field(default_factory=Question.get_questions)

    def get_question(self) -> Question:
        try:
            question = self.questions.pop()
        except IndexError:
            return None
        return question


@ft.control
class App(ft.Container):
    modele: Modele = field(default_factory=Modele)

    def init(self):
        self.width = 400
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20

        self.question = ft.Text(color=ft.Colors.WHITE)
        self.reponses = ft.Row()
        for n in range(2):
            self.reponses.controls.append(
                ft.Button(content="", on_click=lambda _, choix=n:
                          self.gerer_choix(choix)))

        self.element_row = ft.Row()
        self.elements = {}
        for element in Element.tous():
            etext = ElementText(element=element)
            self.element_row.controls.append(etext)
            self.elements[element] = etext

        self.content = ft.Column(controls=[
                    self.question,
                    self.reponses,
                    self.element_row,
                    ])

        self.preparer_question(self.modele.get_question())

    def preparer_question(self, question: Question):
        self.question.value = question.question
        for n in range(2):
            self.reponses.controls[n].content = question.choix[n]
        self.effet_reponse = question.fonction

    def finaliser(self):
        self.question.value = "FINI!"
        self.reponses.controls = []

    def gerer_choix(self, choix):
        print(f"choix {choix} was clicked")
        self.exclude(self.effet_reponse[1-choix])
        prochaine_question = self.modele.get_question()
        if prochaine_question:
            self.preparer_question(prochaine_question)
        else:
            self.finaliser()

    def exclude(self, excluded):
        for element in Element.tous():
            if excluded in element.fonctions and self.elements[element]:
                self.element_row.controls.remove(self.elements[element])
                self.elements[element] = None


def main(page: ft.Page):
    page.title = "Faites votre choix..."
    vue = App()
    page.add(vue)
    # vue.preparer_question(modele.QUESTION1)
    page.update()


if __name__ == "__main__":
    ft.run(main)
