import numpy as np
from functools import lru_cache
from scipy.ndimage import label, find_objects, generate_binary_structure, binary_dilation


# Fonction pour effectuer une rotation de bits vers la gauche (par soucis de performances)
@lru_cache(maxsize=None)
def left_rotate(value: bytes, shift: int) -> bytes:
    # Masquage à la fin de l'opération pour nettoyer les bits décalés sur la gauche lors de l'opération
    return ((value << shift) | (value >> (4 - shift))) & 0b00001111


# Fonction pour vérifier si une connection est sûre entre respectivement c1 (à gauche) et c2 (à droite) 
@lru_cache(maxsize=None)
def is_horizontal_connection_safe(c1: bytes, c2: bytes) -> bool:
    # Isolation du bit droite de la première cellule
    # Isolation du bit gauche de la deuxième cellule
    # On retourne le résultat du ET logique entre les deux bits
    return ((c1 & 0b0100) >> 2) == (c2 & 0b0001)


# Fonction pour vérifier si une connection est sûre entre respectivement c1 (en haut) et c2 (en bas) 
# Note : La vérification horizontale demandant moins d'opération, elle sera systématiquement prioritaire
@lru_cache(maxsize=None)
def is_vertical_connection_safe(c1: bytes, c2: bytes) -> bool:
    # Isolation du bit bas de la première cellule
    # Isolation du bit haut de la deuxième cellule
    # On retourne le résultat du ET logique entre les deux bits
    return ((c1 & 0b0010) >> 1) == ((c2 & 0b1000) >> 3)


# Fonction pour vérifier si la grille est dans un état sûr ou non
def is_grid_safe(grid: np.ndarray) -> bool:
    for y in np.arange(grid.shape[0] - 1):
        for x in np.arange(grid.shape[1] - 1):
            if not (is_horizontal_connection_safe(grid[y, x], grid[y, x + 1]) and
                    is_vertical_connection_safe(grid[y, x], grid[y + 1, x])):
                return False

    return True


# Fonction pour créer des sous-grilles du problème à partir d'une grille fournie
def create_clusters(grid: np.ndarray, immutable_grid: np.ndarray, rotations_dict: dict) -> list[tuple[np.ndarray | tuple | dict]]:
    # Inverser la grille pour scipy (identifier les clusters de True et non False)
    inversed_cluster = ~immutable_grid

    # Identification des clusters
    labeled_array, _ = label(inversed_cluster)

    # Trouver les tranches des composantes connexes
    slices = find_objects(labeled_array)

    cluster_list = []

    for i, slice_ in enumerate(slices):
        # Coordonnées du cluster enfant dans le cluster parent
        coords = (slice_[0].start - 1, slice_[1].start - 1)
        labels_sliced = labeled_array[slice_]

        # Grille booléenne qui ne garde en False que les cases du cluster non résolut ACTUEL (ignore les autre clusters qui dépassent)
        ajusted_immutable_grid = np.ones((labels_sliced.shape[0] + 2, labels_sliced.shape[1] + 2), dtype=np.bool)
        ajusted_immutable_grid[1:-1, 1:-1] = np.where(labels_sliced == i+1, False, True)

        ajusted_rotations_dict = {}

        for i, j in np.ndindex(ajusted_immutable_grid.shape):
            if not ajusted_immutable_grid[i, j]:
                ajusted_rotations_dict[(i, j)] = rotations_dict[(coords[0] + i, coords[1] + j)]

        ajusted_grid = np.where(ajusted_immutable_grid == False, grid[
            coords[0]:coords[0] + ajusted_immutable_grid.shape[0],
            coords[1]:coords[1] + ajusted_immutable_grid.shape[1]
        ], 0b0000)

        neighbor_grid = binary_dilation(~ajusted_immutable_grid, structure=generate_binary_structure(2, 1))
        neighbor_cells = np.bitwise_xor(~ajusted_immutable_grid, neighbor_grid)
        
        for i, j in zip(*np.where(neighbor_cells)):
            for nid, neighbor in enumerate([(i, j-1), (i+1, j), (i, j+1), (i-1, j)]):
                if (not (0 <= neighbor[0] < ajusted_grid.shape[0]) or
                    not (0 <= neighbor[1] < ajusted_grid.shape[1])):
                    continue

                if not ajusted_immutable_grid[neighbor]:
                    connection_value = (grid[i + coords[0], j + coords[1]] >> nid) & 1
                    ajusted_grid[i, j] = (ajusted_grid[i, j] & (0b1111 ^ (1 << nid))) | (connection_value << nid)

        cluster_list.append((
            ajusted_grid,
            ajusted_immutable_grid,
            ajusted_rotations_dict,
            coords
        ))

    return cluster_list


# Fonction pour éliminer les cellules dont nous pouvons déduire logiquement la position
def trivial_cells(grid: np.ndarray, immutable_grid: np.ndarray, rotations_dict: dict) -> tuple[np.ndarray | dict]:

    cells_pile = set()

    # Nous ajoutons au début toutes les cellules à vérifier
    for i, row in enumerate(immutable_grid):
        for j in np.where(row == False)[0]:
            if len(rotations_dict[(i, j)]) == 1:
                cells_pile.add((i, j))
                
    # Nous allons retirer triviallement les cellules qui n'ont qu'une seule configuration possible
    while len(cells_pile) > 0:
        i, j = cells_pile.pop()

        # Si les voisins sûrs ne permettent qu'une seule rotation, la rotation devient définitive
        if len(rotations_dict[(i, j)]) == 1:
            rotation = rotations_dict[(i, j)].pop()

            if rotation != 0:
                grid[i, j] = left_rotate(grid[i, j], rotation)

            del rotations_dict[(i, j)]
            immutable_grid[i, j] = True

            for nid, neighbor in enumerate([(i, j-1), (i, j+1), (i-1, j), (i+1, j)]):
                if (not (0 <= neighbor[0] < grid.shape[0]) or
                    not (0 <= neighbor[1] < grid.shape[1])):
                    continue

                if immutable_grid[neighbor]:
                    continue

                rotations_to_remove = set()

                for rotation in rotations_dict[neighbor]:
                    test_rotation = left_rotate(grid[neighbor], rotation)
                    
                    # Vérifications des configurations
                    match nid:
                        case 0:
                            safe = is_horizontal_connection_safe(test_rotation, grid[i, j])
                        case 1:
                            safe = is_horizontal_connection_safe(grid[i, j], test_rotation)
                        case 2:
                            safe = is_vertical_connection_safe(test_rotation, grid[i, j])
                        case 3:
                            safe = is_vertical_connection_safe(grid[i, j], test_rotation)
                    
                    if not safe:
                        rotations_to_remove.add(rotation)

                for rotation in rotations_to_remove:
                    rotations_dict[neighbor].discard(rotation)

                if len(rotations_dict[neighbor]) == 0:
                    raise Exception("La grille est dans un état invalide !")
                
                cells_pile.add(neighbor)
    
    # Nous retournons la grille modifié, et sa jumelle avec des booléens indiquant les cellules fixées
    return grid, immutable_grid, rotations_dict


def dfs(grid: np.ndarray, immutable_grid: np.ndarray, rotations_dict: dict) -> np.ndarray:
    # Sélection de la cellule à tester
    cell = min(rotations_dict.keys(), key=lambda coords:len(rotations_dict[coords]))

    for rotation in rotations_dict[cell]:
        test_grid = grid.copy()
        test_immutable_grid = immutable_grid.copy()
        test_rotations_dict = {k: s.copy() for k, s in rotations_dict.items()}

        test_rotations_dict[cell] = {rotation}

        try:
            test_grid, test_immutable_grid, test_rotations_dict = trivial_cells(
                test_grid, test_immutable_grid, test_rotations_dict
            )
        except Exception:
            continue

        if is_grid_safe(test_grid):
            return test_grid

        try:
            test_grid = dfs(test_grid, test_immutable_grid, test_rotations_dict)
        except Exception:
            continue

        if is_grid_safe(test_grid):
            return test_grid
        
    raise Exception("Grille non-solvable")

def solve(grid: np.ndarray) -> np.ndarray :

    immutable_grid = np.zeros(grid.shape, dtype=np.bool)
    rotations_dict = {}

    for i, j in np.ndindex(grid.shape):
        if grid[i, j] == 0b1111 or grid[i, j] == 0b0000:
            rotations_dict[(i, j)] = {0}
        elif grid[i, j] == 0b1010 or grid[i, j] == 0b0101:
            rotations_dict[(i, j)] = {0, 1}
        else:
            rotations_dict[(i, j)] = {0, 1, 2, 3}

    rotations_dict[(1, 0)] = {0}
    rotations_dict[(grid.shape[0] - 2, grid.shape[1] - 1)] = {0}

    print("Premier nettoyage des cellules triviales...")

    grid, immutable_grid, rotations_dict = trivial_cells(grid, immutable_grid, rotations_dict)

    amount_removed = (np.sum(immutable_grid[1:-1,1:-1])/grid[1:-1,1:-1].size)*100

    print(f"{amount_removed:.2f}% des cellules supprimées !")

    if is_grid_safe(grid):
        return grid
    
    print("Séparation du problème en clusters...")
    
    clusters = create_clusters(grid, immutable_grid, rotations_dict)

    print("Nombre de clusters à résoudre :", len(clusters))

    for cluster in clusters:
        solved_grid = dfs(cluster[0], cluster[1].copy(), cluster[2])

        for i, row in enumerate(cluster[1]):
            for j in np.where(row == False)[0]:
                grid[cluster[3][0] + i, cluster[3][1] + j] = solved_grid[i, j]

    return grid