import pygame

# Dimensions de la grille
MAX_SCREEN_SIZE = 800
MARGIN = 1

BACKGROUND_COLOR = (30, 30, 30)

def load_tile_images(image_folder, cell_size):

    images = {
        "empty": pygame.image.load(f"{image_folder}/empty.png"),
        "mid": pygame.image.load(f"{image_folder}/mid.png"),
        "line": pygame.image.load(f"{image_folder}/line.png"),
        "angle": pygame.image.load(f"{image_folder}/angle.png"),
        "te": pygame.image.load(f"{image_folder}/te.png"),
        "cross": pygame.image.load(f"{image_folder}/cross.png"),
    }

    # Mise à l'échelle des images à la taille des cellules
    for key in images:
        images[key] = pygame.transform.scale(images[key], (cell_size, cell_size))
    
    return images

def get_tile_image(images, tile_value):
    """
    Mappe une valeur décimale à une image, avec la rotation appropriée.
    """
    rotations = {
        0b0000: (0, "empty"),   # Aucun bit activé : tuile vide
        0b0001: (270, "mid"),   # Une seule ouverture à gauche
        0b0010: (0, "mid"),     # Une seule ouverture en bas
        0b0100: (90, "mid"),    # Une seule ouverture à droite
        0b1000: (180, "mid"),   # Une seule ouverture en haut
        0b0011: (180, "angle"), # Angle (gauche-bas)
        0b0110: (270, "angle"),   # Angle (bas-droite)
        0b1100: (0, "angle"),  # Angle (droite-haut)
        0b1001: (90, "angle"), # Angle (haut-gauche)
        0b0101: (90, "line"),   # Ligne (gauche-droite)
        0b1010: (0, "line"),    # Ligne (haut-bas)
        0b0111: (180, "te"),    # Té (bas-droite-gauche)
        0b1011: (90, "te"),    # Té (haut-gauche-bas)
        0b1101: (0, "te"),      # Té (droite-haut-gauche)
        0b1110: (270, "te"),     # Té (haut-droite-bas)
        0b1111: (0, "cross"),   # Croix (quatre ouvertures)
    }


    rotation, tile_type = rotations.get(tile_value, (0, "empty"))
    
    # Récupérer l'image correspondante et appliquer la rotation
    image = images.get(tile_type)
    return pygame.transform.rotate(image, rotation)

def display_grid(screen, grid, images, cell_size):
    """
    Affiche la grille sur l'écran avec les images.
    """
    
    for row in range(grid.shape[0]):
        for col in range(grid.shape[1]):
            tile_value = grid[row, col] 
            x = col * (cell_size + MARGIN)
            y = row * (cell_size + MARGIN)

            tile_image = get_tile_image(images, tile_value)
            
            screen.blit(tile_image, (x, y))
