import numpy as np

from solver import *

def test_horizontal():
    for c1 in np.arange(16).tobytes():
        for c2 in np.arange(16).tobytes():
            if (
                (c1 in [0, 1, 2, 3, 8, 9, 10, 11] and c2 in [0, 2, 4, 6, 8, 10, 12, 14]) or 
                (c1 in [4, 5, 6, 7, 12, 13, 14, 15] and c2 in [1, 3, 5, 7, 9, 11, 13, 15])
            ):
                assert is_horizontal_connection_safe(c1, c2)
            else:
                assert not is_horizontal_connection_safe(c1, c2)


def test_vertical():
    for c1 in np.arange(16).tobytes():
        for c2 in np.arange(16).tobytes():
            if (
                (c1 in [0, 1, 4, 5, 8, 9, 12, 13] and c2 in [0, 1, 2, 3, 4, 5, 6, 7]) or 
                (c1 in [2, 3, 6, 7, 10, 11, 14, 15] and c2 in [8, 9, 10, 11, 12, 13, 14, 15])
            ):
                assert is_vertical_connection_safe(c1, c2)
            else:
                assert not is_vertical_connection_safe(c1, c2)
