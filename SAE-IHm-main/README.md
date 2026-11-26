# SAE IHM
Travail du groupe 5 :
- Isaac PILLE-YARD (Isaacpille)
- Youenn DEZITTER (Eryoumayt)
- Arthur LECLERC (Nitchitos)

https://github.com/Eryoumayt/SAE-IHm

---

L'ensemble du travail a été réalisé en Python à l'aide de la biblitohèque PyQt6.
Le style du projet a été réalisé à l'aide de QtGui.

ATTENTION !!!

(petite précision, pour la verification d'une grille, le code fait en sorte que la vérification fonctionne uniquement si la grille est remplie par le joueur lui-même, si le joeuur appuie sur le bouton puis résoudre alors la résolution est bonne mais la verification dira "la grille n'est pas valide" car le code ne certifie qu'une grille remplie manuellement par l'utilisateur)


```python
from PyQt6.QtGui import QFontDatabase, QFont
# - QFontDatabase permet de stocker le chemin des polices d'écritures
# - QFont permet d'appliquer les fonts
```

Il y a 3 Modèles principaux :
- Case.py
- Grille.py
- Motif.py

## Case.py

L'objet de type Case() possède :
- Une liste de deux entiers permettant de stocker la position (x , y) d'une case
- La valeur de la case
  
```python
class Case():
    def __init__(self, position: list ,valeur: int):
        self.__position = position # position de la case
        self.__valeur = valeur # valeur de la case
```

La classe Case contient plusieurs méthodes :

- Un getter et un setter valeur() pour obtenir et changer la veleur de la case :

```python
# Modification et récupération de la valeur
@property
def valeur(self):
    # Renvoie la valeur de la case
    return self.__valeur
    
@valeur.setter
def valeur(self, new_val: int):
    # Change la valeur de la case
    self.__valeur = new_val  
```

- Deux getters get_x() et get_y() pour obtenir les coordonnées de la case :

```python
# Coordonnées du point
def get_x(self):
    # Renvoie la position x de la case
    return self.__position[0]
    
def get_y(self):
    # Renvoie la position y de la case
    return self.__position[1]
```

- Des comparateurs pour comparer deux cases entre elles en fonction de leur valeur et de leur position :

```python
# Comparateurs
def compare_valeur(self, v: int) -> bool:
    '''
    Compare la valeur de la case à celle d'un entier.
    Si la valeur de la case est égale à l'entier, alors True est renvoyé.
    Sinon on renvoie False.
    '''
    if self.valeur == v:
        return True
    else:
        return False
        
def compare_pos(self, pos_x, pos_y):
    '''
    Compare les coordonnées de la case à celle insérés dans la fonction.
    Si les coordonnées sont les mêmes, alors on renvoie True
    Sinon False.
    '''
    if self.get_x() == pos_x and self.get_y() == pos_y:
        return True
    else:
        return False
```


## Motif.py

L'objet de type Motif() possède :
- Une liste d'objet de type Case()

```python
class Motif():
    def __init__(self, cases: list):
        # Liste d'objets Case appartenant à ce motif
        self.__cases = []
        for c in cases:
            self.__cases.append(Case([c[0], c[1]], c[2]))
```

La classe Motif contient plusieurs méthodes :
- des getters qui renvoient une liste de cases ou une case en fonction de ses coordonnées

```python
def get_cases(self) -> list:
    # Renvoie la liste des cases du motif
    return self.__cases
    
def get_cases_by_pos(self, x: int, y: int):
    # Renvoie une case en fonction de ses coordonnées
    for i in self.__cases:
        if i.get_x() == x and i.get_y() == y:
            return i
        
    print("Aucune case ayant pour coordonnées (x = ",x,", y =", y,")")
    return None
```

- Un getter qui renvoie la taille du motif :

```python
def get_taille(self) -> int:
    # Renvoie le nombre de cases du motif
    return len(self.__cases)
```

- Un getter qui renvoie les valeurs des cases du motif :

```python
def get_valeurs(self) -> list:
    # Renvoie la liste des valeurs actuelles des cases
    valeurs = []
    for case in self.__cases:
        valeurs.append(case.valeur)
    return valeurs
```

- Un getter qui renvoie les valeurs qui ne sont pas encore placées dans le motif :

```python
def get_valeurs_manquantes(self) -> list:
    # Renvoie les valeurs de 1 à N qui ne sont pas encore placées
    manquantes = []
    for v in range(1, self.get_taille() + 1):
        if v not in self.get_valeurs():
            manquantes.append(v)
    return manquantes
```

- Deux méthodes de vérification :
Une méthode multiples() qui vérifie si certaines cases du motifs ont la même valeur
Une méthode is_valid() qui vérifie si un motif est valide (valeurs possibles, pas de multiples...)

```python
    def multiples(self) -> bool:
        '''
        Fonction qui vérifie si une valeur est présente 
        plusieurs fois dans un même motif
        
        Si c'est le cas, alors la fonction renvoie True
        False sinon 
        '''
        liste_valeurs: list = []
        for i in self.get_cases():
            if i.valeur != 0: # On ignore les cases vides
                if i.valeur not in liste_valeurs:
                    # On ajoute les valeurs dans une liste et si elle est déjà dans la liste
                    # Alors c'est un doublon (donc on renvoie True)
                    liste_valeurs.append(i.valeur)
                else:
                    return True
            
        return False
    
    def is_valid(self) -> bool:
        '''
        vérifie si la grille est valide :
        -> Pas de doublons
        -> Valeurs comprisent entre 1 et la taille de la grille
        Renvoie True si la grille est valide
        False sinon
        '''
        
        if self.multiples() == True:
            return False
        
        else:
            for i in self.get_cases():
                if i.valeur < 0 or i.valeur > self.get_taille():
                    return False
        
        return True
```

## Grille.py

L'objet de type Grille() possède :
- Une chaîne de caractères indiquant le chemin vers un fichier JSON contenant une grille

```python
class Grille():
    def __init__(self, path: str):
        self.__path = path
        self.__dico_brut = self.from_json(self.__path)

        self.__grille: dict = {}
        for i in self.__dico_brut:
            self.__grille[i] = Motif(self.__dico_brut[i])
```

Afin de lire les fichiers JSON, Grille.py contient une méthode from_json() :

```python
def from_json(self, file_path: str) -> dict:
        # Transforme les fichiers json en dictionnaires python
        with open(file_path) as f:
            return json.load(f)
```

La classe Grille possède plusieurs méthodes :
- Une méthode is_full() qui permet de savoir si toutes les cases sont remplies ou non :

```python
    def is_full(self):
        '''
        Verifie si une grille est complete ou non
        Si la grille est remplie, la fonction renvoie True
        False sinon
        '''
        nb_cases: int = 0
        nb_cases_remplies: int = 0

        for i in self.__grille.values():
            for j in i.get_cases():
                nb_cases += 1
                if j.valeur != 0:
                    nb_cases_remplies += 1

        if nb_cases == nb_cases_remplies:
            return True
        else:
            return False
```

- Une méthode get_motif() qui renvoie un motif en fonction des coordonnées d'un point :

```python
    def get_motif(self, x: int, y: int) -> Motif:
        '''
        Fonction qui permet de savoir le motif auquel appartient une case
        en fonction de ses coordonnees (x, y)
        Renvoie un motif si elle trouve un point avec ces coordonnees
        None sinon
        '''
        for i in self.__grille.values():
            for j in i.get_cases():
                if j.get_x() == x and j.get_y() == y:
                    return i
        return None
```

- Une méthode is_valid() qui permet de savoir si une grille est valide ou non :

```python
    def is_valid(self) -> bool:
        '''
        Fonction qui permet de savoir si la grille
        est valide ou non
        Si elle est valide, la fonction renvoie True
        False sinon
        '''
        if self.is_full() == False:
            return False

        for i in self.__grille.values():
            if i.multiples() == True:
                return False

        # Verification du voisinage : deux cases adjacentes (8 voisins)
        # ne doivent pas avoir la meme valeur
        if self.__verif_voisinage() == False:
            return False

        return True
```

- Une méthode verif_voisinage() qui permet de vérifier si une case à une valeur égale à l'un de ses voisins ou non :

```python
    def __verif_voisinage(self) -> bool:
        '''
        Verifie que deux cases adjacentes (8 voisins)
        n'ont pas la meme valeur.
        Renvoie True si le voisinage est valide, False sinon.
        '''
        decalages = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        for motif in self.__grille.values():
            for case in motif.get_cases():
                for dr, dc in decalages:
                    voisin = self.__get_case(case.get_x() + dr, case.get_y() + dc)
                    if voisin is not None and voisin.valeur == case.valeur:
                        return False
        return True
```

- Une méthode get_case() qui renvoie une case si elle existe :

```python
    def __get_case(self, x: int, y: int):
        '''
        Retourne la case aux coordonnees (x, y) si elle existe, None sinon.
        '''
        for motif in self.__grille.values():
            for case in motif.get_cases():
                if case.get_x() == x and case.get_y() == y:
                    return case
        return None
```

