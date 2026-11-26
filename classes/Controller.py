import json
import random
import glob
import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QObject, QEvent
from PyQt6.QtGui import QShortcut, QKeySequence
from .solver import solver
from .Grille import Grille
from PyQt6.QtCore import QThread, pyqtSignal


class SolverWorker(QThread):
    """Execute le solveur dans un thread separe pour ne pas bloquer l'interface.

    Args:
        chemin (str): Le chemin vers le fichier JSON de la grille a resoudre.
    Attributes:
        chemin (str): Le chemin vers le fichier JSON de la grille a resoudre.
    """
    termine = pyqtSignal(bool, object)

    def __init__(self, chemin):
        super().__init__()
        self.chemin = chemin

    def run(self):
        """Execute le solveur et emet le signal termine avec le resultat et la grille."""
        s = solver(self.chemin)
        resultat = s.resolver()
        self.termine.emit(resultat, s.grille)


class controller(QObject):
    """Le controlleur pour gerer les interactions entre le modele (Grille) et la vue (Vue).
    Il connecte les actions de la vue a des methodes qui manipulent le modele et mettent a jour la vue en consequence.

    Args:
        model (Grille): L'instance du modele representant la grille de jeu.
        view (Vue): L'instance de la vue representant l'interface utilisateur.
    Attributes:
        model (Grille): L'instance du modele representant la grille de jeu.
        view (Vue): L'instance de la vue representant l'interface utilisateur.
    """

    def __init__(self, model, view):
        """Initialise le controlleur avec une instance du modele et de la vue, et connecte les actions de la vue a des methodes du controlleur.

        Args:
            model (Grille): L'instance du modele representant la grille de jeu.
            view (Vue): L'instance de la vue representant l'interface utilisateur.
        """
        super().__init__()

        self.model = model
        self.view = view
        self.case_selectionnee = None
        self.donnees_brutes = None
        self.chemin_grille = None
        self.__difficulte_facile = True

        # ---- Connexions page difficulte ---- #
        self.view.get_selection_difficulte().get_btn_facile().clicked.connect(self.__on_difficulte_facile)
        self.view.get_selection_difficulte().get_btn_difficile().clicked.connect(self.__on_difficulte_difficile)

        # ---- Connexions page selection grille ---- #
        self.view.get_selection_grille().grille_choisie.connect(self.__on_grille_choisie)
        self.view.get_selection_grille().retour_demande.connect(self.__on_retour_menu)

        # ---- Connexions sidebar ---- #
        self.view.get_menu_gauche().get_btn_verifier().clicked.connect(self.on_check)
        self.view.get_menu_gauche().get_btn_resoudre().clicked.connect(self.on_solver)
        self.view.get_menu_gauche().get_btn_nouvelle().clicked.connect(self.new_game)
        self.view.get_menu_gauche().get_btn_sauvegarder().clicked.connect(self.on_save)
        self.view.get_menu_gauche().get_btn_back().clicked.connect(self.__on_retour_menu)

        # ---- Connexions menu bar ---- #
        self.view.get_action_charger().triggered.connect(self.on_open)
        self.view.get_action_sauvegarder().triggered.connect(self.on_save)
        self.view.get_action_quitter().triggered.connect(self.view.close)
        self.view.get_action_regles().triggered.connect(self.on_regles)
        self.view.get_action_verifier().triggered.connect(self.on_check)

        # ---- Raccourcis clavier ---- #
        self.view.get_action_resoudre().triggered.connect(self.on_solver)
        self.view.get_action_nouvelle().triggered.connect(self.new_game)
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self.view).activated.connect(self.on_delete)

        # ---- Theme change -> reconnecter signaux ---- #
        self.view.theme_change.connect(self.__reconnecter_signaux)

    # ======================== Navigation ======================== #

    def __on_difficulte_facile(self):
        """Active le mode facile et affiche la page de selection de grille."""
        self.__difficulte_facile = True
        self.view.set_difficulte_facile(True)
        self.view.afficher_selection_grille()

    def __on_difficulte_difficile(self):
        """Active le mode difficile et affiche la page de selection de grille."""
        self.__difficulte_facile = False
        self.view.set_difficulte_facile(False)
        self.view.afficher_selection_grille()

    def __on_grille_choisie(self, chemin):
        """Charge la grille selectionnee par l'utilisateur.

        Args:
            chemin (str): Le chemin vers le fichier JSON de la grille choisie.
        """
        self.__charger_grille(chemin)

    def __on_retour_menu(self):
        """Arrete le chronometre et retourne a la page de selection de difficulte."""
        self.view.arreter_chrono()
        self.view.afficher_difficulte()

    # ======================== Chargement ======================== #

    def __reconnecter_signaux(self):
        """Reconnecte les signaux des QLineEdit de la grille apres un changement de theme.
        Necessaire car le changement de QSS peut detruire les connexions existantes.
        """
        entries = self.view.get_grille_widget().get_entries()
        for (row, col), entry in entries.items():
            entry.installEventFilter(self)
            try:
                entry.textChanged.disconnect()
            except (RuntimeError, TypeError):
                pass
            entry.textChanged.connect(lambda texte, r=row, c=col: self.on_value_enter(r, c))

    def __charger_grille(self, chemin):
        """Charge une grille depuis un fichier JSON et met a jour la vue.

        Args:
            chemin (str): Le chemin vers le fichier JSON contenant la grille a charger.
        Attributes:
            model (Grille): L'instance du modele mise a jour avec la nouvelle grille.
            donnees_brutes (dict): Les donnees brutes de la grille chargee.
            chemin_grille (str): Le chemin vers le fichier JSON de la grille actuelle.
        """
        self.model = Grille(chemin)
        with open(chemin, 'r', encoding='utf-8') as f:
            self.donnees_brutes = json.load(f)
        self.chemin_grille = chemin

        self.view.set_grille_data(self.donnees_brutes)
        self.view.get_grille_widget().afficher(self.donnees_brutes, self.view.get_theme_sombre())
        self.view.afficher_grille_centree()
        self.__reconnecter_signaux()

        self.view.reinitialiser_chrono()
        self.view.demarrer_chrono()
        self.view.get_menu_gauche().get_btn_resoudre().setEnabled(True)

    # ======================== Actions ======================== #

    def on_open(self):
        """Ouvre une boite de dialogue pour selectionner un fichier JSON contenant une grille."""
        chemin, _ = QFileDialog.getOpenFileName(self.view, "Charger une grille", "", "JSON (*.json)")
        if not chemin:
            return
        self.__charger_grille(chemin)

    def new_game(self):
        """Reinitialise la grille et le chrono pour commencer une nouvelle partie.
        Charge une grille aleatoire parmi les fichiers JSON du dossier Grille.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dossier_grilles = os.path.join(base_dir, "..", "Grille")
        grilles = glob.glob(os.path.join(dossier_grilles, "*.json"))
        if grilles:
            grille_choisie = random.choice(grilles)
            self.__charger_grille(grille_choisie)

    def on_save(self):
        """Ouvre une boite de dialogue pour sauvegarder la grille actuelle dans un fichier JSON.
        Les cases editables sont sauvegardees avec leur valeur initiale (0) et la valeur du joueur.
        """
        if self.donnees_brutes is None:
            QMessageBox.warning(self.view, "Attention", "Aucune grille chargee.")
            return

        entries = self.view.get_grille_widget().get_entries()
        grille_sauvegarde = {}

        for nom_motif, cases in self.donnees_brutes.items():
            nouvelle_liste = []
            for case in cases:
                row = case[0]
                col = case[1]
                valeur_init = case[2]
                entry = entries.get((row, col))
                if entry is not None:
                    texte = entry.text()
                    valeur_joueur = int(texte) if texte.isdigit() else 0
                    nouvelle_liste.append([row, col, 0, valeur_joueur])
                else:
                    nouvelle_liste.append([row, col, valeur_init, 0])
            grille_sauvegarde[nom_motif] = nouvelle_liste

        chemin, _ = QFileDialog.getSaveFileName(self.view, "Sauvegarder la grille", "", "Fichiers JSON (*.json)")
        if chemin:
            with open(chemin, 'w', encoding='utf-8') as f:
                json.dump(grille_sauvegarde, f, indent=4)
            QMessageBox.information(self.view, "Succes", "Grille sauvegardee.")

    def on_check(self):
        """Verifie si la grille actuelle est valide en comparant les valeurs saisies par l'utilisateur avec les regles du jeu.
        Affiche un message indiquant si la grille est valide ou non.
        """
        if self.donnees_brutes is None:
            return

        entries = self.view.get_grille_widget().get_entries()
        for (row, col), entry in entries.items():
            texte = entry.text()
            nouvelle_valeur = int(texte) if texte.isdigit() else 0
            motif = self.model.get_motif(row, col)
            if motif is not None:
                case = motif.get_cases_by_pos(row, col)
                if case is not None:
                    case.valeur = nouvelle_valeur

        valide = self.model.is_valid()
        if valide:
            QMessageBox.information(self.view, "Verification", "La grille est valide !")
            self.view.arreter_chrono()
        else:
            QMessageBox.warning(self.view, "Verification", "La grille n'est pas valide.")

    def on_solver(self):
        """Lance le solveur pour trouver une solution a la grille actuelle.
        Desactive le bouton Resoudre pendant le calcul pour eviter les lancements multiples.
        """
        if self.donnees_brutes is None:
            return

        with open("temp_grille.json", 'w', encoding='utf-8') as f:
            json.dump(self.donnees_brutes, f)

        self.view.get_menu_gauche().get_btn_resoudre().setEnabled(False)
        self.worker = SolverWorker("temp_grille.json")
        self.worker.termine.connect(self.__on_solver_fini)
        self.worker.start()

    def __on_solver_fini(self, resultat, grille):
        """Callback appele lorsque le solveur a termine. Met a jour la vue avec la solution trouvee,
        ou affiche un message d'erreur si aucune solution n'a ete trouvee. Reactive le bouton de resolution.

        Args:
            resultat (bool): Indique si une solution a ete trouvee ou non.
            grille (dict): La grille solution trouvee par le solveur.
        """
        self.view.get_menu_gauche().get_btn_resoudre().setEnabled(True)

        if resultat:
            self.view.get_grille_widget().afficher(grille, self.view.get_theme_sombre())
            # Mettre a jour donnees_brutes avec la solution
            all_vals = self.view.get_grille_widget().get_all_values()
            for nom_motif, cases in self.donnees_brutes.items():
                for i, case_data in enumerate(cases):
                    row, col = case_data[0], case_data[1]
                    val = all_vals.get((row, col), 0)
                    self.donnees_brutes[nom_motif][i] = [row, col, val]
            self.__reconnecter_signaux()
            self.view.arreter_chrono()
            QMessageBox.information(self.view, "Resolution", "Solution trouvee !")
        else:
            QMessageBox.warning(self.view, "Resolution echouee", "Aucune solution n'a ete trouvee.")
        self.worker.quit()
        self.worker.wait()

    def on_regles(self):
        """Affiche une boite de dialogue avec les regles du Néonaure et les raccourcis clavier."""
        QMessageBox.information(self.view, "Regles du Neonature",
            "Le Neonature est un puzzle similaire au Suguru.\n\n"
            "3 regles :\n"
            "1. Chaque case doit contenir un chiffre.\n"
            "2. Les 8 voisins d'une case doivent avoir des valeurs differentes.\n"
            "3. Chaque motif de taille N doit contenir une permutation de 1 a N.\n\n"
            "Raccourcis :\n"
            "Ctrl+O : Charger une grille\n"
            "Ctrl+S : Sauvegarder\n"
            "Ctrl+R : Resoudre\n"
            "Ctrl+N : Nouvelle partie\n"
            "Suppr : Effacer la case\n"
            "Fleches : Naviguer entre les cases"
        )

    # ======================== Verification temps reel ======================== #

    def on_verifier_voisinage(self):
        """Detecte les conflits de voisinage ET de motifs et surligne les cases en rouge.
        Parcourt toutes les cases remplies et verifie :
        - Que les 8 voisins d'une case ont des valeurs differentes.
        - Qu'il n'y a pas de doublons dans chaque motif.
        - Que les valeurs sont dans les limites du motif (1 a taille_motif).
        """
        if self.donnees_brutes is None:
            return

        entries = self.view.get_grille_widget().get_entries()

        toutes_valeurs = {}
        for nom_motif, cases in self.donnees_brutes.items():
            for case in cases:
                row, col = case[0], case[1]
                valeur_init = case[2]
                entry = entries.get((row, col))
                if entry is not None:
                    texte = entry.text()
                    val = int(texte) if texte.isdigit() and int(texte) != 0 else 0
                else:
                    val = valeur_init
                if val != 0:
                    toutes_valeurs[(row, col)] = val

        conflits = set()

        # Conflits voisinage
        for (row, col), val in toutes_valeurs.items():
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    voisin_val = toutes_valeurs.get((row + dr, col + dc))
                    if voisin_val is not None and voisin_val == val:
                        if (row, col) in entries:
                            conflits.add((row, col))
                        if (row + dr, col + dc) in entries:
                            conflits.add((row + dr, col + dc))

        # Conflits motifs (doublons + valeurs hors limites)
        for nom_motif, cases in self.donnees_brutes.items():
            taille_motif = len(cases)
            valeurs_motif = {}
            for case in cases:
                row, col = case[0], case[1]
                val = toutes_valeurs.get((row, col), 0)
                if val == 0:
                    continue
                if val < 1 or val > taille_motif:
                    if (row, col) in entries:
                        conflits.add((row, col))
                if val not in valeurs_motif:
                    valeurs_motif[val] = []
                valeurs_motif[val].append((row, col))

            for val, positions in valeurs_motif.items():
                if len(positions) > 1:
                    for (r, c) in positions:
                        if (r, c) in entries:
                            conflits.add((r, c))

        self.view.get_grille_widget().surligner_conflits(conflits)

    # ======================== Evenements ======================== #

    def eventFilter(self, obj, event):
        """Filtre les evenements clavier et de focus sur les cases de la grille.
        Gere la selection de case, la navigation avec les fleches et la touche Suppr.
        """
        if event.type() == QEvent.Type.FocusIn:
            entries = self.view.get_grille_widget().get_entries()
            for (row, col), entry in entries.items():
                if entry is obj:
                    self.case_selectionnee = (row, col)
                    self.view.get_grille_widget().surligner_selection(row, col)
                    break

        elif event.type() == QEvent.Type.KeyPress:
            entries = self.view.get_grille_widget().get_entries()
            if event.key() == Qt.Key.Key_Delete:
                self.on_delete()
                return True
            if self.case_selectionnee is not None:
                row, col = self.case_selectionnee
                if event.key() == Qt.Key.Key_Up and (row - 1, col) in entries:
                    entries[(row - 1, col)].setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Down and (row + 1, col) in entries:
                    entries[(row + 1, col)].setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Left and (row, col - 1) in entries:
                    entries[(row, col - 1)].setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Right and (row, col + 1) in entries:
                    entries[(row, col + 1)].setFocus()
                    return True

        return False

    def on_value_enter(self, row, col):
        """Gere la saisie d'une valeur dans une case et valide en temps reel.
        Deplace le focus vers la prochaine case vide et verifie le voisinage en mode facile.

        Args:
            row (int): Ligne de la case modifiee.
            col (int): Colonne de la case modifiee.
        """
        entries = self.view.get_grille_widget().get_entries()
        entry = entries.get((row, col))
        texte = entry.text()
        if not texte:
            return
        if texte.isdigit() and (int(texte) > 5 or int(texte) == 0):
            entry.clear()
            return

        if entry is not None and entry.text().isdigit() and int(entry.text()) != 0:
            positions = sorted(entries.keys())
            idx = positions.index((row, col))
            for i in range(idx + 1, len(positions)):
                prochaine = entries[positions[i]]
                if not prochaine.text().isdigit() or int(prochaine.text()) == 0:
                    prochaine.setFocus()
                    if self.__difficulte_facile:
                        self.on_verifier_voisinage()
                    return
            for i in range(0, idx):
                prochaine = entries[positions[i]]
                if not prochaine.text().isdigit() or int(prochaine.text()) == 0:
                    prochaine.setFocus()
                    if self.__difficulte_facile:
                        self.on_verifier_voisinage()
                    return
        if self.__difficulte_facile:
            self.on_verifier_voisinage()

    def on_delete(self):
        """Efface la valeur de la case actuellement selectionnee.
        Si une case est selectionnee, son contenu est efface et le focus est maintenu.

        Attributes:
            case_selectionnee (tuple): Les coordonnees (row, col) de la case actuellement selectionnee.
        """
        if self.case_selectionnee is not None:
            entries = self.view.get_grille_widget().get_entries()
            entry = entries.get(self.case_selectionnee)
            if entry is not None:
                entry.clear()
