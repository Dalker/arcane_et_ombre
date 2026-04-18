from typing import Callable, Sequence
import flet as ft
from model import Modele, Etat, Element, Archetype


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
        if etat.compatible(self.archetype):
            self.color = self.COULEUR[self.archetype.element]
        else:
            self.color = "#333333"


@ft.control
class VueDialogue(ft.Container):
    """Partie de la Vue pour les questions / réponses et texte de fin."""

    def init(self):
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
        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.question,
                    self.reponses,
                    ])

    def post_init(self, gerer_choix: Callable[[int], None]):
        self._gerer_choix = gerer_choix

    def update(self, etat: Etat):
        self.question.value = etat.question
        for n in range(2):
            self.reponses.controls[n].content = etat.choix[n]
        super().update()


@ft.control
class VueArchetypes(ft.Container):
    """Partie de la Vue pour les archétypes."""

    def init(self):
        self.alignment = ft.Alignment.CENTER
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20
        self.element_row = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
                spacing=20,
                )
        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.element_row,
                    ])

    def post_init(self, elements: Sequence[Element]):
        for element in elements:
            widget = ArchetypeWidget(archetype=element)
            self.element_row.controls.append(widget)

    def update(self, etat: Etat):
        for element_widget in self.element_row.controls:
            element_widget.update(etat)
        super().update()


@ft.control
class Vue(ft.Container):
    callback_gauche: Callable | None = None
    callback_droite: Callable | None = None

    def init(self):
        self.width = 450
        self.alignment = ft.Alignment.CENTER
        self.bgcolor = ft.Colors.GREY_800
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20

        self.dialogue = VueDialogue()
        self.archetypes = VueArchetypes()

        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.dialogue, self.archetypes])

    def post_init(self, page: ft.Page, elements: Sequence[Element],
                  gerer_choix: Callable[[int], None]):
        self.dialogue.post_init(gerer_choix)
        self.archetypes.post_init(elements)
        page.title = "Faites votre choix..."
        page.theme_mode = ft.ThemeMode.DARK
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.add(self)
        page.update()

    def update(self, etat: Etat):
        self.dialogue.update(etat)
        self.archetypes.update(etat)
        super().update()


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
        self.vue.update(self.modele.etat)

    def gerer_choix(self, choix: int):
        self.modele.appliquer_choix(choix)
        self.update()


if __name__ == "__main__":
    ft.run(Controle)
