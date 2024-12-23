import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import time

from src.start import *
from src.solver import *
from display.display_grid import *

def main():
    n, m = 50, 50
    t = time.time()
    grid = initiate(n, m)
    print(f"Grille de {n}x{m} initialisée avec succès en {time.time() - t:.4f}s")

    t = time.time()
    print("Début de la résolution automatique...")
    solved_grid = solve(grid)
    print(f"Résolution automatique en {time.time() - t:.2f}s")
    
    pygame.init()
    cell_size = (MAX_SCREEN_SIZE - (MARGIN * max(grid.shape))) // max(grid.shape)
    screen = pygame.display.set_mode(((cell_size + MARGIN) * m, (cell_size + MARGIN) * n))  # Taille dynamique
    pygame.display.set_caption("Affichage de la Grille")

    tile_images = load_tile_images("display/images", cell_size)

    # Suppression des murs autour
    solved_grid = solved_grid[1:-1, 1:-1]

    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
              
        screen.fill((30, 30, 30))
        display_grid(screen, solved_grid, tile_images, cell_size)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
