import flet as ft
from model import Modele
from vue import Vue


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
