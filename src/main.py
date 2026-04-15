from dataclasses import dataclass, field
from enum import Enum
import flet as ft


class Couleur(Enum):
    FEU = ft.Colors.RED
    AIR = ft.Colors.GREEN
    TERRE = ft.Colors.BROWN
    EAU = ft.Colors.BLUE


@dataclass
class Question:
    """Une question qui déterminera une fonction parmi deux opposées."""

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
class Archetype:
    """Un type de personalité déterminé par un ou plusieurs archetypes."""
    nom: str
    fonctions: str
    color: ft.Colors = ft.Colors.WHITE

    def __hash__(self):
        return hash(self.nom)

    @classmethod
    def elements(cls):
        return (
            cls("Feu", "NT", Couleur.FEU),
            cls("Air", "NF", Couleur.AIR),
            cls("Terre", "ST", Couleur.TERRE),
            cls("Eau", "SF", Couleur.EAU),
            )


@ft.control
class ArchetypeWidget(ft.Text):
    """Vue d'un Archetype."""
    archetype: Archetype | None = None

    def init(self):
        self.color = self.archetype.color.value
        self.value = self.archetype.nom

    def disable(self):
        self.color = "#333333"


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
                          self.gerer_choix(choix)))

        self.element_row = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
                spacing=20,
                )
        self.elements = {}
        for element in Archetype.elements():
            widget = ArchetypeWidget(archetype=element)
            self.element_row.controls.append(widget)
            self.elements[element] = widget

        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
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
        self.exclude(self.effet_reponse[1-choix])
        prochaine_question = self.modele.get_question()
        if prochaine_question:
            self.preparer_question(prochaine_question)
        else:
            self.finaliser()

    def exclude(self, excluded):
        for element in Archetype.elements():
            if excluded in element.fonctions and self.elements[element]:
                self.elements[element].disable()


def main(page: ft.Page):
    page.title = "Faites votre choix..."
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    vue = App()
    page.add(vue)
    page.update()


if __name__ == "__main__":
    # ft.app(target=main, assets_dir="assets", view=ft.WEB_BROWSER)
    ft.run(main)
