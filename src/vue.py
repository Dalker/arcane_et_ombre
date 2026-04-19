"""Vue de l'application, utilisant flet.

Ce module exporte la classe Vue, dont les méthodes publiques sont:
    - vue.post_init(page: ft.Page,
                    elements: Sequence[Archetype],
                    gerer_choix: Callable[[int], None])
    - vue.update(etat: Etat)
"""
from typing import Callable
import flet as ft
from modele import EtatVisible, Element, Archetype


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

    def update_etat(self, etat: EtatVisible):
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

    def update_etat(self, etat: EtatVisible):
        self.question.value = etat.question
        for n in range(2):
            self.reponses.controls[n].content = etat.reponses[n]
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
                controls=[ArchetypeWidget(archetype=element)
                          for element in Archetype.elements()]
                )
        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.element_row,
                    ])

    def update_etat(self, etat: EtatVisible):
        for element_widget in self.element_row.controls:
            element_widget.update_etat(etat)
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

    def post_init(self,
                  page: ft.Page,
                  gerer_choix: Callable[[int], None]):
        self.dialogue.post_init(gerer_choix)
        page.title = "Faites votre choix..."
        page.theme_mode = ft.ThemeMode.DARK
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.add(self)
        page.update()

    def update(self, etat: EtatVisible):
        self.dialogue.update_etat(etat)
        self.archetypes.update_etat(etat)
        super().update()
