"""Contrôle central de l'application.

Le contrôle met en communication le Modele et la Vue.
Il maintient aussi une mémoire des Etat pour pouvoir implémenter
l'annulation d'actions précédentes.
"""
from __future__ import annotations
from dataclasses import dataclass

import flet as ft

from modele import Etat, Decision
from vue import Vue, Commande


@dataclass
class EtatMemorisable:
    """État actuel, passé ou présent récupérable par undo/redo."""
    etat_visible: Etat
    decisions_restantes: tuple[Decision, ...] = ()

    @classmethod
    def initial(cls) -> EtatMemorisable:
        """Fournir le premier état correctement rempli."""
        decisions = Decision.sequence()
        return EtatMemorisable(
                decisions_restantes=decisions[1:],
                etat_visible=Etat(
                    decision=decisions[0],
                    ))

    def appliquer_choix(self, n_choix: int) -> EtatMemorisable:
        """Appliquer la réponse à la question actuelle."""
        choix = self.etat_visible.decision.resultats[n_choix]
        if not self.decisions_restantes:
            return EtatMemorisable(
                    etat_visible=Etat(
                        traits=self.etat_visible.traits,
                        decision=self.etat_visible.decision,
                        arcane_ou_ombre=choix,
                        ))
        return EtatMemorisable(
            decisions_restantes=self.decisions_restantes[1:],
            etat_visible=Etat(
                traits=self.etat_visible.traits + choix,
                decision=(self.decisions_restantes[0]
                          if self.decisions_restantes
                          else None),
                ))


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
        self.vue.post_init(page, self.demande)
        self.vue.update(self.etat.etat_visible, undoable=False)

    def demande(self, commande: Commande, argument: int | None = None):
        match commande:
            case Commande.DECIDER_TRAIT:
                self._prev_buffer.append(self.etat)
                if self._next_buffer:
                    self._next_buffer = list()
                self.etat = self.etat.appliquer_choix(argument)
            case Commande.UNDO:
                self._next_buffer.append(self.etat)
                self.etat = self._prev_buffer.pop()
            case Commande.REDO:
                self._prev_buffer.append(self.etat)
                self.etat = self._next_buffer.pop()
        self.vue.update(self.etat.etat_visible,
                        undoable=bool(self._prev_buffer),
                        redoable=bool(self._next_buffer))
