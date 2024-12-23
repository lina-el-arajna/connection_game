import src.solver as solve

import numpy as np

# Pourcentage des connexions effectives entre les sommets
# Exemple : 0.8 génèrera une grille avec beaucoup plus de "connexions entre cases" que 0.1
FILLED_RATIO = 0.5

# Fonction pour générer un problème
# n: Hauteur
# m: Largeur
def initiate(n: int, m: int) -> np.ndarray:
    if n <= 1 or m <= 1:
        raise Exception("La grille doit avoir une taille positive d'au moins 2x2")

    # Ajout d'une ligne tout autour de la grille pour représenter un mur
    grid = np.full((n+2, m+2), fill_value=0b1111, dtype=np.uint8)

    # Création des murs vides haut/bas
    grid[0, :] = 0b0000
    grid[-1, :] = 0b0000

    # Création des murs vides gauche/droite sauf pour l'entrée/sortie
    grid[2:-1, 0] = 0b0000
    grid[1:-2, -1] = 0b0000

    # Initialisation des entrées/sorties en tuyaux monodirectionnels vers la grille
    grid[1, 0] = 0b0100
    grid[-2, -1] = 0b0001

    # Suppression les connections entre la grille et les murs (sauf l'entrée/sortie)
    # Via un XOR appliqué sur toutes les brodures
    grid[1, 1:-1] = np.bitwise_xor(grid[1, 1:-1], np.full((m,), fill_value=0b1000, dtype=np.uint8))
    grid[-2, 1:-1] = np.bitwise_xor(grid[-2, 1:-1], np.full((m,), fill_value=0b0010, dtype=np.uint8))

    # On ignore l'entrée
    grid[2:-1, 1] = np.bitwise_xor(grid[2:-1, 1], np.full((n-1,), fill_value=0b0001, dtype=np.uint8))
    # On ignore la sortie
    grid[1:-2, -2] = np.bitwise_xor(grid[1:-2, -2], np.full((n-1,), fill_value=0b0100, dtype=np.uint8))

    # Sélection des connexions à supprimer
    nb_delete = round((1 - FILLED_RATIO) * (m - 1) * n)

    # Nous faisons - 1 car les tuiles les plus à droites n'ont pas de voisin à droite, et de même pour le bas
    # Une case et son voisin de droite
    horizontal_delete = np.random.choice((m - 1) * n, size=nb_delete, replace=False)
    # Une case et son voisin du bas
    vertical_delete = np.random.choice((n - 1) * m, size=nb_delete, replace=False)

    # Extraction des coordonnées dans la grille
    horizontal_rows, horizontal_cols = np.unravel_index(horizontal_delete, (n, m - 1))
    vertical_rows, vertical_cols = np.unravel_index(vertical_delete, (n - 1, m))

    # Nous ajoutons 1 aux index pour prendre en compte les murs
    horizontal_rows += 1
    horizontal_cols += 1
    vertical_rows += 1
    vertical_cols += 1

    # On supprime la connexion de droite des cellules sélectionnées
    grid[horizontal_rows, horizontal_cols] = np.bitwise_xor(
        grid[horizontal_rows, horizontal_cols],
        np.full((nb_delete,), fill_value=0b0100)
    )

    # On supprime la connexion de gauche des voisins de droite des cellules sélectionnées 
    grid[horizontal_rows, horizontal_cols + 1] = np.bitwise_xor(
        grid[horizontal_rows, horizontal_cols + 1],
        np.full((nb_delete,), fill_value=0b0001)
    )

    # On supprime la connexion du bas des cellules sélectionnées
    grid[vertical_rows, vertical_cols] = np.bitwise_xor(
        grid[vertical_rows, vertical_cols],
        np.full((nb_delete,), fill_value=0b0010)
    )

    # On supprime la connexion du haut des voisins en dessous des cellules sélectionnées 
    grid[vertical_rows + 1, vertical_cols] = np.bitwise_xor(
        grid[vertical_rows + 1, vertical_cols],
        np.full((nb_delete,), fill_value=0b1000)
    )
    
    # On pivote aléatoirement les tuiles
    grid[1:-1, 1:-1] = np.vectorize(solve.left_rotate)(grid[1:-1, 1:-1],np.reshape(np.random.choice(4, size=n*m), (n, m)))

    return grid