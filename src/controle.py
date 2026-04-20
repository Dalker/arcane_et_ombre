"""Contrôle central de l'application.

Le contrôle met en communication le Modele et la Vue.
Il maintient aussi une mémoire des Etat pour pouvoir implémenter
l'annulation d'actions précédentes.
"""
from __future__ import annotations
from dataclasses import dataclass

import flet as ft

from modele import Etat, Decision
from vue import Vue


@dataclass
class EtatMemorisable:
    """État actuel, passé ou présent récupérable par undo/redo."""
    decisions_restantes: tuple[Decision, ...]
    etat_visible: Etat

    @classmethod
    def initial(cls) -> EtatMemorisable:
        """Fournir le premier état correctement rempli."""
        decisions = Decision.sequence()
        return EtatMemorisable(decisions[1:], Etat(decision=decisions[0]))

    def appliquer_choix(self, choix: int) -> EtatMemorisable:
        """Appliquer la réponse à la question actuelle."""
        if self.etat_visible.decision is None:
            return self
        nouveau_trait = self.etat_visible.decision.resultats[choix]
        nouvel_etat = Etat(
                traits=self.etat_visible.traits + nouveau_trait,
                decision=(self.decisions_restantes[0]
                          if self.decisions_restantes
                          else None)
                )
        return EtatMemorisable(
                decisions_restantes=self.decisions_restantes[1:],
                etat_visible=nouvel_etat,
                )


class Controle:
    etat: EtatMemorisable
    vue: Vue
    _prev_buffer: list[EtatMemorisable]
    _next_buffer: list[EtatMemorisable]

    def __init__(self, page: ft.Page):
        """Mettre en place les canaux de communication."""
        self._prev_buffer = list()
        self._next_buffer = list()
        self.etat = EtatMemorisable.initial()
        self.vue = Vue()
        self.vue.post_init(page, self.gerer_choix)
        self.vue.update(self.etat.etat_visible)

    def gerer_choix(self, choix: int):
        """Gérer un choix demandé par la vue."""
        self._prev_buffer.append(self.etat)
        if self._next_buffer:
            self._next_buffer = list()
        self.etat = self.etat.appliquer_choix(choix)
        self.vue.update(self.etat.etat_visible)

