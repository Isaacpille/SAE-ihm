import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import Qt
from vue.menu import Menu
from classes.vue import Vue
from classes.Controller import controller

if __name__ == "__main__":
    app = QApplication(sys.argv)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Chargement des polices
    luckiest_guy = os.path.join(base_dir, "vue", "qss", "LuckiestGuy-Regular.ttf")
    QFontDatabase.addApplicationFont(luckiest_guy)
    technology = os.path.join(base_dir, "vue", "qss", "Technology.ttf")
    QFontDatabase.addApplicationFont(technology)

    # Menu de démarrage
    menu = Menu()
    menu.setWindowState(Qt.WindowState.WindowMaximized)
    
    # Appliquer le style du menu UNIQUEMENT sur le widget Menu
    qss_path = os.path.join(base_dir, "vue", "qss", "menu_style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            menu.setStyleSheet(f.read())
    menu.show()

    def lancer_jeu():
        menu.close()
        fenetre = Vue()
        
        # Appliquer le thème clair sur TOUTE l'app pour le jeu
        chemin_clair = os.path.join(base_dir, "classes", "theme_clair.qss")
        if os.path.exists(chemin_clair):
            with open(chemin_clair, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
        
        menu.ctrl = controller(None, fenetre)
        fenetre.setWindowState(Qt.WindowState.WindowMaximized)
        fenetre.show()

    menu.get_start().clicked.connect(lancer_jeu)
    sys.exit(app.exec())