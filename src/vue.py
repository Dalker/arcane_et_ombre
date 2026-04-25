"""Vue de l'application, utilisant flet.

Ce module exporte la classe Vue, dont les méthodes publiques sont:
    - vue.post_init(page: ft.Page,
                    elements: Sequence[Archetype],
                    gerer_choix: Callable[[int], None])
    - vue.update(etat: Etat)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
from itertools import groupby
from enum import Enum, auto
import flet as ft
from modele import Etat, Element, Archetype, CarteVisible


class Commande(Enum):
    DECIDER_TRAIT = auto()
    UNDO = auto()
    REDO = auto()


class ArchetypeWidget(ft.Text):
    """Vue d'un Archetype."""
    archetype: Archetype
    inverted: bool = False

    COULEUR = {
        Element.FEU: "#b02408",  # ft.Colors.RED,
        Element.AIR: "#4e84b8",  # ft.Colors.GREEN,
        Element.TERRE: "#8d715c",  # ft.Colors.BROWN,
        Element.EAU: "#017a87",  # ft.Colors.BLUE,
    }

    def __init__(self, archetype: Archetype, inverted: bool = False):
        super().__init__()
        self.archetype = archetype
        self.inverted = inverted
        self.value = self.archetype.nom

    def update_etat(self, etat: Etat):
        if etat.compatible(self.archetype):
            self.disabled = False
            if self.inverted:
                self.color = ft.Colors.BLACK
                self.bgcolor = self.COULEUR[self.archetype.element]
            else:
                self.color = self.COULEUR[self.archetype.element]
        else:
            self.disabled = True
            if self.inverted:
                self.bgcolor = ft.Colors.BLACK
            self.color = "#333333"


class Demandeur:
    """Mixin pour insérer un moyen d'envoyer des Commandes au Controle."""
    demander: Callable[[Commande, str | None], None] | None

    def post_init(self, demander: Callable[[Commande, str | None], None]):
        self.demander = demander


@ft.control
class Frame(ft.Container):
    """Partie visuellement distincte de la Vue."""

    alignment: ft.Alignment = field(default_factory=lambda:
                                    ft.Alignment.CENTER)
    bgcolor: ft.Colors = ft.Colors.BLACK
    border_radius: ft.BorderRadius = field(default_factory=lambda:
                                           ft.BorderRadius.all(20))
    padding: int = 20


@dataclass
class VueDialogue(Frame, Demandeur):
    """Partie de la Vue pour les questions / réponses et texte de fin."""
    question: ft.Text = field(default_factory=lambda:
                              ft.Text(color=ft.Colors.WHITE))
    reponses: ft.Row = field(default_factory=lambda:
                             ft.Row(alignment=ft.MainAxisAlignment.CENTER))
    content: ft.Column = field(default_factory=lambda: ft.Column(
            horizontal_alignment=ft.MainAxisAlignment.CENTER))

    def init(self):
        self.content.controls = [self.question, self.reponses]
        for n in range(2):
            self.reponses.controls.append(
                ft.Button(content="", on_click=lambda _, choix=n:
                          self.demander(Commande.DECIDER_TRAIT, choix)))

    def update_etat(self, etat: Etat):
        self.question.value = etat.question
        for n in range(2):
            self.reponses.controls[n].content = etat.reponses[n]
        super().update()


@dataclass
class VueUndoRedo(Frame, Demandeur):
    """Conteneur de boutons undo / reset / redo."""

    def init(self):
        self.commandes = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                )
        self.undo_button = ft.Button(content="<-", on_click=
                                     lambda _: self.demander(Commande.UNDO))
        self.redo_button = ft.Button(content="->", on_click=
                                     lambda _: self.demander(Commande.REDO))
        self.commandes.controls = [self.undo_button, self.redo_button]
        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.commandes,
                    ])

    def update_state(self, undoable: bool, redoable: bool):
        self.undo_button.disabled = not undoable
        self.redo_button.disabled = not redoable


@dataclass
class VueArchetypes(Frame):
    """Partie de la Vue pour les archétypes."""

    def init(self):
        super().init()
        arcanes_by_element = groupby(Archetype.arcanes(),
                                     key=lambda a: a.element)
        element = Archetype.elements().__iter__()
        arcane_columns = [
                ft.Column(controls=[ArchetypeWidget(archetype=next(element),
                                                    inverted=True)]
                          + [ArchetypeWidget(archetype=arcane)
                             for arcane in group])
                for _, group in arcanes_by_element
                ]
        self.arcane_row = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
                wrap=True,
                spacing=20,
                controls=arcane_columns
                )

    def update_etat(self, etat: Etat):
        if etat.arcane_ou_ombre is CarteVisible.ARCANE:
            for archetype in Archetype.arcanes():
                if etat.compatible(archetype):
                    break
            self.content = ft.Image(src="arcane_{}.png".format(
                archetype.nom.lower()).replace("é", "e"))
        elif etat.arcane_ou_ombre is CarteVisible.OMBRE:
            for archetype in Archetype.arcanes():
                if etat.compatible(archetype):
                    break
            self.content = ft.Image(src="ombre_{}.png".format(
                archetype.nom.lower()).replace("é", "e"))
        else:
            self.content = self.arcane_row
            for column in self.arcane_row.controls:
                for widget in column.controls:
                    widget.update_etat(etat)
        super().update()


@ft.control
class Vue(ft.Container):
    callback_gauche: Callable | None = None
    callback_droite: Callable | None = None
    width: int = 450
    padding: int = 20
    alignment: ft.Alignment = field(default_factory=lambda: ft.Alignment.CENTER)
    bgcolor: ft.Colors = field(default_factory=lambda: ft.Colors.GREY_800)
    border_radius: ft.BorderRadius = field(default_factory=lambda:
                                           ft.BorderRadius.all(20))

    def init(self):

        self.dialogue = VueDialogue()
        self.archetypes = VueArchetypes()
        self.undo_redo = VueUndoRedo()

        self.content = ft.Column(
                horizontal_alignment=ft.MainAxisAlignment.CENTER,
                )

    def add_all_content(self):
        self.content.controls = [self.dialogue, self.archetypes, self.undo_redo]

    def post_init(self,
                  page: ft.Page,
                  demande: Callable[[Commande, str | None], None]):
        self.add_all_content()
        page.add(self)
        for widget in (self.dialogue, self.undo_redo):
            widget.post_init(demande)
        page.title = "Faites votre choix..."
        page.theme_mode = ft.ThemeMode.DARK
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def update(self, etat: Etat,
               undoable: bool = True, redoable: bool = False):
        self.undo_redo.update_state(undoable, redoable)
        for widget in (self.dialogue, self.archetypes):
            widget.update_etat(etat)
        super().update()
