import sys
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtGui import QFontDatabase, QFont, QColor, QPainter


class MenuGauche(QWidget):
    def __init__(self):
        super().__init__()
        self.__bg_color = QColor("#16213e")
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(10, 20, 10, 20)
        self.__layout.setSpacing(18)

        # Chargement des polices (Luckiest Guy + fallback Arial)
        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            font_id = QFontDatabase.addApplicationFont(chemin_luckiest)
            self.__police_titre = QFont("Luckiest Guy", 36) if font_id != -1 else QFont("Arial", 36, QFont.Weight.Bold)
            self.__police_bouton = QFont("Luckiest Guy", 22) if font_id != -1 else QFont("Arial", 22, QFont.Weight.Bold)
        else:
            self.__police_titre = QFont("Arial", 36, QFont.Weight.Bold)
            self.__police_bouton = QFont("Arial", 22, QFont.Weight.Bold)

        # --- Titre "MENU" ---
        self.__title = QLabel("MENU")
        self.__title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__title.setFont(self.__police_titre)
        self.__title.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # --- Separateur blanc horizontal ---
        self.__separateur = QFrame()
        self.__separateur.setFrameShape(QFrame.Shape.HLine)
        self.__separateur.setStyleSheet("color: white; background-color: white; max-height: 2px;")

        # --- Boutons d'action ---
        self.__btn_verifier = QPushButton("Vérifier")
        self.__btn_resoudre = QPushButton("Résoudre")
        self.__btn_nouvelle = QPushButton("Nouvelle Partie")
        self.__btn_sauvegarder = QPushButton("Sauvegarder")
        self.__btn_back = QPushButton("Retour Menu")

        boutons = [self.__btn_verifier, self.__btn_resoudre,
                   self.__btn_nouvelle, self.__btn_sauvegarder, self.__btn_back]
        for btn in boutons:
            btn.setFont(self.__police_bouton)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFF00;
                    color: black;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    min-height: 35px;
                }
                QPushButton:hover {
                    background-color: #ffe066;
                }
                QPushButton:pressed {
                    background-color: #ff8c00;
                }
            """)

        # --- Ajout des elements au layout ---
        self.__layout.addWidget(self.__title)
        self.__layout.addSpacing(8)
        self.__layout.addWidget(self.__separateur)
        self.__layout.addSpacing(12)
        self.__layout.addWidget(self.__btn_verifier)
        self.__layout.addWidget(self.__btn_resoudre)
        self.__layout.addWidget(self.__btn_nouvelle)
        self.__layout.addWidget(self.__btn_sauvegarder)
        self.__layout.addWidget(self.__btn_back)
        self.__layout.addStretch()

        self.setLayout(self.__layout)

    def paintEvent(self, event):
        """Peint le fond du menu."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.__bg_color)

    def set_bg_color(self, color: str):
        """Change la couleur de fond du menu (utilise par paintEvent)."""
        self.__bg_color = QColor(color)
        self.update()

    def appliquer_theme(self, sombre: bool):
        """Re-applique les styles apres un changement de theme."""
        self.__title.setStyleSheet("color: #FFFF00; background-color: transparent;")
        self.__separateur.setStyleSheet("color: white; background-color: white; max-height: 2px;")
        boutons = [self.__btn_verifier, self.__btn_resoudre,
                   self.__btn_nouvelle, self.__btn_sauvegarder, self.__btn_back]
        for btn in boutons:
            btn.setFont(self.__police_bouton)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFF00;
                    color: black;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    min-height: 35px;
                }
                QPushButton:hover {
                    background-color: #ffe066;
                }
                QPushButton:pressed {
                    background-color: #ff8c00;
                }
            """)

    # --- Getters ---
    def get_btn_verifier(self):
        return self.__btn_verifier

    def get_btn_resoudre(self):
        return self.__btn_resoudre

    def get_btn_nouvelle(self):
        return self.__btn_nouvelle

    def get_btn_sauvegarder(self):
        return self.__btn_sauvegarder

    def get_btn_back(self):
        return self.__btn_back
