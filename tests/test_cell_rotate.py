import numpy as np

from solver import *

def test_cell_rotate():
    table = {
        (1, 1): 2, (1, 2): 4, (1, 3): 8,
        (2, 1): 4, (2, 2): 8, (2, 3): 1,
        (3, 1): 6, (3, 2): 12, (3, 3): 9,
        (4, 1): 8, (4, 2): 1, (4, 3): 2,
        (6, 1): 12, (6, 2): 9, (6, 3): 3,
        (7, 1): 14, (7, 2): 13, (7, 3): 11,
        (8, 1): 1, (8, 2): 2, (8, 3): 4,
        (9, 1): 3, (9, 2): 6, (9, 3): 12,
        (11, 1): 7, (11, 2): 14, (11, 3): 13,
        (12, 1): 9, (12, 2): 3, (12, 3): 6,
        (13, 1): 11, (13, 2): 7, (13, 3): 14,
        (14, 1): 13, (14, 2): 11, (14, 3): 7,
    }

    for cell in np.arange(16):
        for shift in np.arange(4):
            if shift == 0:
                assert left_rotate(cell, shift) == cell
            elif cell in [0, 15]:
                assert left_rotate(cell, shift) == cell
            elif cell in [5, 10]:
                if (shift % 2) == 0:
                    assert left_rotate(cell, shift) == cell
                else:
                    assert left_rotate(cell, shift) == (5 if cell == 10 else 10)
            else:
                assert left_rotate(cell, shift) == table[(cell, shift)]
