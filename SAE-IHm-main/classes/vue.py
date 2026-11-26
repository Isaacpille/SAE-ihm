import os
import json
import glob
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QMainWindow, QLabel,
    QWidget, QGridLayout, QLineEdit,
    QPushButton, QFrame, QGraphicsDropShadowEffect,
    QStackedWidget, QScrollArea
)
from PyQt6.QtGui import QAction, QFont, QFontDatabase, QIntValidator, QColor, QPainter, QRadialGradient, QBrush
from PyQt6.QtCore import QPointF
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from .MenuGauche import MenuGauche

TAILLE_CASE = 60


# ============================================================ #
#                     GRILLE DU JEU                            #
# ============================================================ #


class GrilleWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.__layout = QGridLayout()
        self.__layout.setSpacing(0)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.__layout)
        self.__entries = {}
        self.__labels = {}

        chemin_police = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_police):
            font_id = QFontDatabase.addApplicationFont(chemin_police)
            self.__police_case = QFont("Luckiest Guy", 18) if font_id != -1 else QFont("Arial", 18, QFont.Weight.Bold)
        else:
            self.__police_case = QFont("Arial", 18, QFont.Weight.Bold)

    def afficher(self, grille_data: dict, sombre: bool = False):
        self.__vider()
        self.__entries = {}
        self.__labels = {}

        fond = "#ffffff" if sombre else "white"
        texte = "black" if sombre else "black"
        bordure_fine = "1px solid gray"
        bordure_epaisse = "3px solid black"

        carte_motifs = {}
        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                carte_motifs[(case[0], case[1])] = idx

        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                row = case[0]
                col = case[1]
                valeur = case[2]

                top    = bordure_epaisse if carte_motifs.get((row-1, col), -1) != idx else bordure_fine
                bottom = bordure_epaisse if carte_motifs.get((row+1, col), -1) != idx else bordure_fine
                left   = bordure_epaisse if carte_motifs.get((row, col-1), -1) != idx else bordure_fine
                right  = bordure_epaisse if carte_motifs.get((row, col+1), -1) != idx else bordure_fine

                style = (
                    f"background-color: {fond};"
                    f"color: {texte};"
                    f"border-top: {top}; border-bottom: {bottom};"
                    f"border-left: {left}; border-right: {right};"
                )

                if valeur != 0:
                    label = QLabel(str(valeur))
                    label.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setFont(self.__police_case)
                    label.setStyleSheet(style)
                    self.__layout.addWidget(label, row, col)
                    self.__labels[(row, col)] = label
                else:
                    entry = QLineEdit()
                    entry.setFixedSize(TAILLE_CASE, TAILLE_CASE)
                    entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    entry.setFont(self.__police_case)
                    entry.setMaxLength(1)
                    entry.setValidator(QIntValidator(1, 5))
                    entry.setStyleSheet(style)
                    self.__layout.addWidget(entry, row, col)
                    self.__entries[(row, col)] = entry

    def surligner_selection(self, row: int, col: int):
        for (r, c), entry in self.__entries.items():
            entry.setStyleSheet(entry.styleSheet().replace("background-color: #cce5ff;", "").replace("background-color: #ff9999;", ""))
            if r == row and c == col:
                entry.setStyleSheet(entry.styleSheet() + "background-color: #cce5ff;")

    def surligner_conflits(self, conflits: set):
        for (row, col) in conflits:
            entry = self.__entries.get((row, col))
            if entry is not None:
                style = entry.styleSheet().replace("background-color: #cce5ff;", "")
                entry.setStyleSheet(style + "background-color: #ff9999;")

    def __vider(self):
        while self.__layout.count():
            item = self.__layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def get_all_values(self) -> dict:
        values = {}
        for (row, col), entry in self.__entries.items():
            texte = entry.text()
            values[(row, col)] = int(texte) if texte.isdigit() else 0
        for (row, col), label in self.__labels.items():
            texte = label.text()
            values[(row, col)] = int(texte) if texte.isdigit() else 0
        return values

    def get_entries(self) -> dict:
        return self.__entries


# ============================================================ #
#             SELECTION DE DIFFICULTE                           #
# ============================================================ #


class SelectionDifficulte(QWidget):
    def __init__(self):
        super().__init__()
        self.__bg_color = QColor("#00a6ff")

        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            QFontDatabase.addApplicationFont(chemin_luckiest)

        police_titre = QFont("Luckiest Guy")
        police_titre.setPixelSize(110)
        police_texte = QFont("Luckiest Guy")
        police_texte.setPixelSize(20)
        police_bouton = QFont("Luckiest Guy")
        police_bouton.setPixelSize(28)

        layout_principal = QVBoxLayout()
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.setSpacing(40)
        layout_principal.setContentsMargins(50, 30, 50, 50)

        # Titre
        self.__label_titre = QLabel("NEONAURE!")
        self.__label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titre.setFont(police_titre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        effet_neon = QGraphicsDropShadowEffect()
        effet_neon.setBlurRadius(40)
        effet_neon.setColor(QColor(255, 255, 0))
        effet_neon.setOffset(0, 0)
        self.__label_titre.setGraphicsEffect(effet_neon)

        # Description
        self.__label_description = QLabel(
            "choisissez le niveau de difficulte\n"
            "(facile: indices + verification en temps reel des voisins)\n"
            "(difficile: pas d'indice + pas de verification des voisins des cases)"
        )
        self.__label_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_description.setFont(police_texte)
        self.__label_description.setStyleSheet("color: #ffffff; background-color: transparent;")
        self.__label_description.setWordWrap(True)

        # Boutons Facile / Difficile
        layout_boutons = QHBoxLayout()
        layout_boutons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_boutons.setSpacing(60)

        bouton_style = """
            QPushButton {
                background-color: #ffff00;
                color: black;
                border: none;
                border-radius: 12px;
                padding: 15px 40px;
            }
            QPushButton:hover { background-color: #ffe066; }
            QPushButton:pressed { background-color: #ff8c00; }
        """

        self.__btn_facile = QPushButton("Facile")
        self.__btn_facile.setFont(police_bouton)
        self.__btn_facile.setMinimumSize(220, 80)
        self.__btn_facile.setStyleSheet(bouton_style)
        ombre_facile = QGraphicsDropShadowEffect()
        ombre_facile.setBlurRadius(20)
        ombre_facile.setColor(QColor(0, 0, 0))
        ombre_facile.setOffset(9, 12)
        self.__btn_facile.setGraphicsEffect(ombre_facile)

        self.__btn_difficile = QPushButton("Difficile")
        self.__btn_difficile.setFont(police_bouton)
        self.__btn_difficile.setMinimumSize(220, 80)
        self.__btn_difficile.setStyleSheet(bouton_style)
        ombre_difficile = QGraphicsDropShadowEffect()
        ombre_difficile.setBlurRadius(20)
        ombre_difficile.setColor(QColor(0, 0, 0))
        ombre_difficile.setOffset(9, 12)
        self.__btn_difficile.setGraphicsEffect(ombre_difficile)

        layout_boutons.addWidget(self.__btn_facile)
        layout_boutons.addWidget(self.__btn_difficile)

        layout_principal.addWidget(self.__label_titre)
        layout_principal.addWidget(self.__label_description)
        layout_principal.addLayout(layout_boutons)
        self.setLayout(layout_principal)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.__bg_color)
        centre = QPointF(self.width() / 2, self.height() / 2)
        rayon = max(self.width(), self.height()) * 0.65
        gradient = QRadialGradient(centre, rayon)
        gradient.setColorAt(0.0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.4, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.7, QColor(0, 58, 122, 150))
        gradient.setColorAt(0.85, QColor(0, 58, 122, 210))
        gradient.setColorAt(1.0, QColor(0, 58, 122, 255))
        painter.fillRect(self.rect(), QBrush(gradient))

    def get_btn_facile(self):
        return self.__btn_facile

    def get_btn_difficile(self):
        return self.__btn_difficile


# ============================================================ #
#           MINI PREVIEW D'UNE GRILLE                          #
# ============================================================ #


class MiniGrillePreview(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, chemin_grille: str, numero: int):
        super().__init__()
        self.__chemin = chemin_grille
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("MiniGrillePreview { background-color: transparent; }")

        with open(chemin_grille, 'r', encoding='utf-8') as f:
            grille_data = json.load(f)

        chemin_police = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_police):
            police_mini = QFont("Luckiest Guy", 7)
            police_nom = QFont("Luckiest Guy", 13)
        else:
            police_mini = QFont("Arial", 7, QFont.Weight.Bold)
            police_nom = QFont("Arial", 13, QFont.Weight.Bold)

        TAILLE_MINI = 22

        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(3)
        layout_principal.setContentsMargins(5, 5, 5, 5)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)

        carte_motifs = {}
        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                carte_motifs[(case[0], case[1])] = idx

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background-color: transparent;")
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        bordure_fine = "1px solid black"
        bordure_epaisse = "2px solid black"

        for idx, cases in enumerate(grille_data.values()):
            for case in cases:
                row, col, valeur = case[0], case[1], case[2]
                top = bordure_epaisse if carte_motifs.get((row-1, col), -1) != idx else bordure_fine
                bottom = bordure_epaisse if carte_motifs.get((row+1, col), -1) != idx else bordure_fine
                left = bordure_epaisse if carte_motifs.get((row, col-1), -1) != idx else bordure_fine
                right = bordure_epaisse if carte_motifs.get((row, col+1), -1) != idx else bordure_fine
                style = (
                    f"background-color: white; color: black;"
                    f"border-top: {top}; border-bottom: {bottom};"
                    f"border-left: {left}; border-right: {right};"
                )
                cell = QLabel(str(valeur) if valeur != 0 else "")
                cell.setFixedSize(TAILLE_MINI, TAILLE_MINI)
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFont(police_mini)
                cell.setStyleSheet(style)
                grid_layout.addWidget(cell, row, col)

        self.__frame_grille = QFrame()
        self.__frame_grille.setStyleSheet("QFrame { border: 3px solid #ffff00; background-color: transparent; }")
        frame_layout = QVBoxLayout(self.__frame_grille)
        frame_layout.setContentsMargins(2, 2, 2, 2)
        frame_layout.addWidget(grid_widget)
        layout_principal.addWidget(self.__frame_grille, alignment=Qt.AlignmentFlag.AlignCenter)

        label_nom = QLabel(f"grille{numero}")
        label_nom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_nom.setFont(police_nom)
        label_nom.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout_principal.addWidget(label_nom)

    def mousePressEvent(self, event):
        self.clicked.emit(self.__chemin)

    def enterEvent(self, event):
        self.__frame_grille.setStyleSheet("QFrame { border: 4px solid #ffe066; background-color: transparent; }")

    def leaveEvent(self, event):
        self.__frame_grille.setStyleSheet("QFrame { border: 3px solid #ffff00; background-color: transparent; }")


# ============================================================ #
#             SELECTION DE GRILLE                              #
# ============================================================ #


class SelectionGrille(QWidget):
    grille_choisie = pyqtSignal(str)
    retour_demande = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__bg_color = QColor("#00a6ff")
        self.__previews = []

        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            QFontDatabase.addApplicationFont(chemin_luckiest)

        police_titre = QFont("Luckiest Guy")
        police_titre.setPixelSize(90)
        police_texte = QFont("Luckiest Guy")
        police_texte.setPixelSize(20)
        police_bouton = QFont("Luckiest Guy")
        police_bouton.setPixelSize(22)

        layout_principal = QVBoxLayout()
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.setSpacing(20)
        layout_principal.setContentsMargins(30, 20, 30, 20)

        # Titre
        self.__label_titre = QLabel("NEONAURE!")
        self.__label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titre.setFont(police_titre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        effet_neon = QGraphicsDropShadowEffect()
        effet_neon.setBlurRadius(40)
        effet_neon.setColor(QColor(255, 255, 0))
        effet_neon.setOffset(0, 0)
        self.__label_titre.setGraphicsEffect(effet_neon)
        layout_principal.addWidget(self.__label_titre)

        # Description
        self.__label_description = QLabel("Fais le choix de ta grille ....")
        self.__label_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_description.setFont(police_texte)
        self.__label_description.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout_principal.addWidget(self.__label_description)

        # Zone scrollable
        self.__grille_container = QWidget()
        self.__grille_container.setStyleSheet("background-color: transparent;")
        self.__grille_layout = QGridLayout()
        self.__grille_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__grille_layout.setSpacing(15)
        self.__grille_layout.setContentsMargins(10, 10, 10, 10)
        self.__grille_container.setLayout(self.__grille_layout)

        scroll = QScrollArea()
        scroll.setWidget(self.__grille_container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { background-color: transparent; border: none; }
            QScrollBar:vertical { background: transparent; width: 10px; }
            QScrollBar::handle:vertical { background: rgba(255, 255, 255, 80); border-radius: 5px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        layout_principal.addWidget(scroll, stretch=1)

        # Bouton Retour
        layout_bas = QHBoxLayout()
        layout_bas.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.__btn_retour = QPushButton("Retour")
        self.__btn_retour.setFont(police_bouton)
        self.__btn_retour.setMinimumSize(160, 55)
        self.__btn_retour.setStyleSheet("""
            QPushButton {
                background-color: #ffff00; color: black;
                border: none; border-radius: 12px; padding: 10px 30px;
            }
            QPushButton:hover { background-color: #ffe066; }
            QPushButton:pressed { background-color: #ff8c00; }
        """)
        self.__btn_retour.clicked.connect(self.retour_demande.emit)
        layout_bas.addWidget(self.__btn_retour)
        layout_principal.addLayout(layout_bas)

        self.setLayout(layout_principal)
        self.charger_grilles()

    def charger_grilles(self):
        for preview in self.__previews:
            preview.clicked.disconnect()
            self.__grille_layout.removeWidget(preview)
            preview.deleteLater()
        self.__previews = []

        base_dir = os.path.dirname(os.path.abspath(__file__))
        dossier_grilles = os.path.join(base_dir, "..", "Grille")
        fichiers = sorted(glob.glob(os.path.join(dossier_grilles, "grille*.json")))
        fichiers = [f for f in fichiers if "grilleTest" not in os.path.basename(f)]

        nb_premiere_ligne = 6
        for i, chemin in enumerate(fichiers):
            nom_fichier = os.path.basename(chemin)
            numero = i + 1
            try:
                nom_sans_ext = os.path.splitext(nom_fichier)[0]
                numero_str = nom_sans_ext.replace("grille", "")
                if numero_str.isdigit():
                    numero = int(numero_str)
            except (ValueError, AttributeError):
                pass

            preview = MiniGrillePreview(chemin, numero)
            preview.clicked.connect(self.grille_choisie.emit)
            self.__previews.append(preview)

            if i < nb_premiere_ligne:
                self.__grille_layout.addWidget(preview, 0, i)
            else:
                offset = (nb_premiere_ligne - (len(fichiers) - nb_premiere_ligne)) // 2
                self.__grille_layout.addWidget(preview, 1, offset + (i - nb_premiere_ligne))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.__bg_color)
        centre = QPointF(self.width() / 2, self.height() / 2)
        rayon = max(self.width(), self.height()) * 0.65
        gradient = QRadialGradient(centre, rayon)
        gradient.setColorAt(0.0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.4, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.7, QColor(0, 58, 122, 150))
        gradient.setColorAt(0.85, QColor(0, 58, 122, 210))
        gradient.setColorAt(1.0, QColor(0, 58, 122, 255))
        painter.fillRect(self.rect(), QBrush(gradient))

    def rafraichir(self):
        self.charger_grilles()


# ============================================================ #
#                     VUE PRINCIPALE                            #
# ============================================================ #


class Vue(QMainWindow):
    theme_change = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neonaure")

        self.__grille_data = None
        self.__theme_sombre = False
        self.__difficulte_facile = True

        # Polices
        chemin_luckiest = os.path.join(os.path.dirname(__file__), "fonts", "LuckiestGuy-Regular.ttf")
        if os.path.exists(chemin_luckiest):
            font_id_luck = QFontDatabase.addApplicationFont(chemin_luckiest)
            self.__police_titre = QFont("Luckiest Guy", 48) if font_id_luck != -1 else QFont("Arial", 48, QFont.Weight.Bold)
        else:
            self.__police_titre = QFont("Arial", 48, QFont.Weight.Bold)

        chemin_techno = os.path.join(os.path.dirname(__file__), "fonts", "Technology.ttf")
        if os.path.exists(chemin_techno):
            font_id_techno = QFontDatabase.addApplicationFont(chemin_techno)
            self.__police_chrono = QFont("TECHNOLOGY", 28) if font_id_techno != -1 else QFont("Arial", 28, QFont.Weight.Bold)
        else:
            self.__police_chrono = QFont("Arial", 28, QFont.Weight.Bold)

        # Chemins des themes
        self.__chemin_clair = os.path.join(os.path.dirname(__file__), "theme_clair.qss")
        self.__chemin_sombre = os.path.join(os.path.dirname(__file__), "theme_sombre.qss")

        # ====== PAGES ======

        # Page 0 : selection difficulte
        self.__selection_difficulte = SelectionDifficulte()

        # Page 1 : selection grille
        self.__selection_grille = SelectionGrille()

        # Page 2 : jeu
        self.__menu_gauche = MenuGauche()
        self.__grille_widget = GrilleWidget()

        # Titre
        self.__label_titre = QLabel("NEONAURE!")
        self.__label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_titre.setFont(self.__police_titre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        effet_neon = QGraphicsDropShadowEffect()
        effet_neon.setBlurRadius(30)
        effet_neon.setColor(QColor(255, 255, 0))
        effet_neon.setOffset(0, 0)
        self.__label_titre.setGraphicsEffect(effet_neon)

        # Chrono
        self.__temps = 0
        self.__chrono = QTimer(self)
        self.__chrono.timeout.connect(self.__incrementer)
        self.__label_chrono = QLabel("00:00")
        self.__label_chrono.setFont(self.__police_chrono)
        self.__label_chrono.setFixedSize(150, 50)
        self.__label_chrono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # ====== CONSTRUCTION PAGE JEU ======

        layout_principal = QHBoxLayout()

        zone_centrale = QVBoxLayout()
        zone_centrale.setContentsMargins(0, 15, 0, 15)
        zone_centrale.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        zone_centrale.addWidget(self.__label_titre, alignment=Qt.AlignmentFlag.AlignCenter)
        zone_centrale.addSpacing(15)
        zone_centrale.addWidget(self.__grille_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        zone_centrale.addSpacing(10)
        zone_centrale.addWidget(self.__label_chrono, alignment=Qt.AlignmentFlag.AlignCenter)
        zone_centrale.addStretch()

        self.__conteneur_centre = QWidget()
        self.__conteneur_centre.setObjectName("conteneurCentre")
        self.__conteneur_centre.setLayout(zone_centrale)

        layout_principal.addWidget(self.__menu_gauche, 1)
        layout_principal.addWidget(self.__conteneur_centre, 3)

        self.__widget_jeu = QWidget()
        self.__widget_jeu.setLayout(layout_principal)

        # ====== QSTACKEDWIDGET ======

        self.__pages = QStackedWidget()
        self.__pages.addWidget(self.__selection_difficulte)
        self.__pages.addWidget(self.__selection_grille)
        self.__pages.addWidget(self.__widget_jeu)
        self.setCentralWidget(self.__pages)

        self.__pages.setCurrentIndex(0)
        self.menuBar().hide()
        self.__creer_menu()

    # ==================== NAVIGATION ==================== #

    def afficher_difficulte(self):
        self.__pages.setCurrentIndex(0)
        self.setStyleSheet("")
        self.menuBar().hide()

    def afficher_selection_grille(self):
        self.__selection_grille.rafraichir()
        self.__pages.setCurrentIndex(1)
        self.setStyleSheet("")
        self.menuBar().hide()

    def afficher_grille_centree(self):
        self.__pages.setCurrentIndex(2)
        self.menuBar().show()
        # Appliquer le theme QSS
        chemin = self.__chemin_sombre if self.__theme_sombre else self.__chemin_clair
        self.__appliquer_theme(chemin)

    # ==================== MENU BAR ==================== #

    def __creer_menu(self):
        menubar = self.menuBar()

        menu_fichier = menubar.addMenu("Fichier")
        self.__action_charger = QAction("Charger une grille", self)
        self.__action_charger.setShortcut("Ctrl+O")
        menu_fichier.addAction(self.__action_charger)

        self.__action_sauvegarder = QAction("Sauvegarder", self)
        self.__action_sauvegarder.setShortcut("Ctrl+S")
        menu_fichier.addAction(self.__action_sauvegarder)

        menu_fichier.addSeparator()
        self.__action_quitter = QAction("Quitter", self)
        self.__action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(self.__action_quitter)

        menu_jeu = menubar.addMenu("Jeu")
        self.__action_verifier = QAction("Verifier", self)
        menu_jeu.addAction(self.__action_verifier)

        self.__action_resoudre = QAction("Resoudre", self)
        self.__action_resoudre.setShortcut("Ctrl+R")
        self.__action_resoudre.setVisible(False)
        menu_jeu.addAction(self.__action_resoudre)

        self.__action_nouvelle = QAction("Nouvelle partie", self)
        self.__action_nouvelle.setShortcut("Ctrl+N")
        self.__action_nouvelle.setVisible(False)
        menu_jeu.addAction(self.__action_nouvelle)

        menu_jeu.addSeparator()
        self.__action_regles = QAction("Regles", self)
        menu_jeu.addAction(self.__action_regles)

        menu_apparence = menubar.addMenu("Apparence")
        self.__action_theme_clair = QAction("Theme clair", self)
        self.__action_theme_clair.triggered.connect(lambda: self.__appliquer_theme(self.__chemin_clair))
        menu_apparence.addAction(self.__action_theme_clair)

        self.__action_theme_sombre = QAction("Theme sombre", self)
        self.__action_theme_sombre.triggered.connect(lambda: self.__appliquer_theme(self.__chemin_sombre))
        menu_apparence.addAction(self.__action_theme_sombre)

    # ==================== THEME ==================== #

    def __appliquer_theme(self, chemin_qss: str):
        with open(chemin_qss, 'r', encoding='utf-8') as f:
            qss = f.read()
        self.setStyleSheet(qss)

        self.__theme_sombre = "sombre" in chemin_qss
        self.__menu_gauche.appliquer_theme(self.__theme_sombre)
        self.__label_titre.setStyleSheet("color: #FFFF00; background-color: transparent;")
        self.__label_chrono.setStyleSheet("color: #FFFF00; background-color: transparent;")

        # Re-afficher la grille avec les bonnes couleurs si on a des donnees
        if self.__grille_data is not None:
            valeurs_actuelles = self.__grille_widget.get_all_values()
            self.__grille_widget.afficher(self.__grille_data, self.__theme_sombre)
            entries = self.__grille_widget.get_entries()
            for (row, col), valeur in valeurs_actuelles.items():
                if (row, col) in entries and valeur != 0:
                    entries[(row, col)].setText(str(valeur))

        # Prevenir le Controller qu'il faut reconnecter les signaux
        self.theme_change.emit()

    # ==================== CHRONO ==================== #

    def __incrementer(self):
        self.__temps += 1
        minutes = self.__temps // 60
        secondes = self.__temps % 60
        self.__label_chrono.setText(f"{minutes:02d}:{secondes:02d}")

    def demarrer_chrono(self):
        self.__temps = 0
        self.__label_chrono.setText("00:00")
        self.__chrono.start(1000)

    def arreter_chrono(self):
        self.__chrono.stop()

    def reinitialiser_chrono(self):
        self.__chrono.stop()
        self.__temps = 0
        self.__label_chrono.setText("00:00")

    def get_temps(self) -> tuple:
        return (self.__temps // 60, self.__temps % 60)

    # ==================== SETTERS ==================== #

    def set_grille_data(self, data):
        self.__grille_data = data

    def set_difficulte_facile(self, valeur: bool):
        self.__difficulte_facile = valeur

    # ==================== GETTERS ==================== #

    def get_grille_widget(self) -> GrilleWidget:
        return self.__grille_widget

    def get_menu_gauche(self) -> MenuGauche:
        return self.__menu_gauche

    def get_selection_difficulte(self) -> SelectionDifficulte:
        return self.__selection_difficulte

    def get_selection_grille(self) -> SelectionGrille:
        return self.__selection_grille

    def get_action_charger(self):
        return self.__action_charger

    def get_action_sauvegarder(self):
        return self.__action_sauvegarder

    def get_action_quitter(self):
        return self.__action_quitter

    def get_action_verifier(self):
        return self.__action_verifier

    def get_action_regles(self):
        return self.__action_regles

    def get_action_resoudre(self):
        return self.__action_resoudre

    def get_action_nouvelle(self):
        return self.__action_nouvelle

    def get_action_theme_clair(self):
        return self.__action_theme_clair

    def get_action_theme_sombre(self):
        return self.__action_theme_sombre

    def get_theme_sombre(self) -> bool:
        return self.__theme_sombre
