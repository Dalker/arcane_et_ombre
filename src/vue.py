"""Vue de l'application, utilisant flet.

Ce module exporte la classe Vue, dont les méthodes publiques sont:
    - vue.post_init(page: ft.Page,
                    elements: Sequence[Archetype],
                    gerer_choix: Callable[[int], None])
    - vue.update(etat: Etat)
"""
from __future__ import annotations
from typing import Callable
from enum import Enum, auto
import flet as ft
from modele import Etat, Element, Archetype


class Commande(Enum):
    DECIDER_TRAIT = auto()
    UNDO = auto()
    REDO = auto()


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

    def update_etat(self, etat: Etat):
        if etat.compatible(self.archetype):
            self.color = self.COULEUR[self.archetype.element]
        else:
            self.color = "#333333"


class Demandeur:
    """Mixin pour insérer un moyen d'envoyer des Commandes au Controle."""
    demander: Callable[[Commande, str | None], None] | None

    def post_init(self, demander: Callable[[Commande, str | None], None]):
        self.demander = demander


class Frame(ft.Container):
    """Partie visuellement distincte de la Vue."""

    def init(self):
        self.alignment = ft.Alignment.CENTER
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20


@ft.control
class VueDialogue(Frame, Demandeur):
    """Partie de la Vue pour les questions / réponses et texte de fin."""

    def init(self):
        super().init()
        self.question = ft.Text(color=ft.Colors.WHITE)
        self.reponses = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                )
        for n in range(2):
            self.reponses.controls.append(
                ft.Button(content="", on_click=lambda _, choix=n:
                          self.demander(Commande.DECIDER_TRAIT, choix)))
        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.question,
                    self.reponses,
                    ])

    def update_etat(self, etat: Etat):
        self.question.value = etat.question
        for n in range(2):
            self.reponses.controls[n].content = etat.reponses[n]
        super().update()


@ft.control
class VueUndoRedo(Frame, Demandeur):
    """Conteneur de boutons undo / reset / redo."""

    def init(self):
        super().init()
        self.commandes = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                )
        self.commandes.controls = [
            ft.Button(content="<-", on_click=lambda _:
                      self.demander(Commande.UNDO)),
            ft.Button(content="->", on_click=lambda _:
                      self.demander(Commande.REDO)),
            ]
        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.commandes,
                    ])


@ft.control
class VueArchetypes(Frame):
    """Partie de la Vue pour les archétypes."""

    def init(self):
        super().init()
        self.element_row = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
                spacing=20,
                controls=[ArchetypeWidget(archetype=element)
                          for element in Archetype.elements()]
                )
        self.arcane_row = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
                wrap=True,
                spacing=20,
                controls=[ArchetypeWidget(archetype=arcane)
                          for arcane in Archetype.arcanes()]
                )
        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.element_row,
                    self.arcane_row,
                    ])

    def update_etat(self, etat: Etat):
        for element_widget in self.element_row.controls:
            element_widget.update_etat(etat)
        for element_widget in self.arcane_row.controls:
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
        self.undo_redo = VueUndoRedo()

        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.dialogue, self.archetypes, self.undo_redo]
                )

    def post_init(self,
                  page: ft.Page,
                  demande: Callable[[Commande, str | None], None]):
        for widget in (self.dialogue, self.undo_redo):
            widget.post_init(demande)
        page.title = "Faites votre choix..."
        page.theme_mode = ft.ThemeMode.DARK
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.add(self)
        page.update()

    def update(self, etat: Etat):
        if etat.decision is None:
            self.content.controls = [self.archetypes]
        for widget in (self.dialogue, self.archetypes):
            widget.update_etat(etat)
        super().update()
