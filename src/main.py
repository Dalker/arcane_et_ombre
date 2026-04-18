"""Contrôle central de l'application.

Le contrôle met en communication le Modele et la Vue.
Il maintient aussi une mémoire des Etat pour pouvoir implémenter
l'annulation d'actions précédentes.
"""
import flet as ft
from modele import Modele, Etat
from vue import Vue


class Controle:
    modele: Modele
    vue: Vue
    _prev_buffer: list[Etat]
    _next_buffer: list[Etat]

    def __init__(self, page: ft.Page):
        """Mettre en place les canaux de communication."""
        self._prev_buffer = list()
        self._next_buffer = list()
        self.modele = Modele()
        self.vue = Vue()
        self.vue.post_init(page, self.gerer_choix)
        self.update()

    def update(self):
        self.vue.update(self.modele.etat)

    def gerer_choix(self, choix: int):
        self._prev_buffer.append(self.modele.etat)
        if self._next_buffer:
            self._next_buffer = list()
        self.modele.appliquer_choix(choix)
        self.update()


if __name__ == "__main__":
    ft.run(Controle)
