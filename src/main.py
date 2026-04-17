from typing import Callable, Sequence
import flet as ft
from model import Modele, Etat, Question, Element, Archetype


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
        self.update()

    def update(self):
        self.vue.update(self.modele.question, self.modele.etat)

    def gerer_choix(self, choix: int):
        self.modele.gerer_choix(choix)
        self.update()


if __name__ == "__main__":
    ft.run(Controle)
