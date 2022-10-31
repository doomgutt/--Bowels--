import numpy as np
from numba import njit, prange

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================


@njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
def coords_to_v_list(anchor, xy_list, cell_size):
    template = np.array([
        [0, 0], [0, 1], [1, 0],
        [0, 1], [1, 0], [1, 1]])
    v_list = np.zeros((len(xy_list), 12))
    for ii in prange(len(xy_list)):
        v_list[ii] = (template + xy_list[ii] + anchor + 1).flatten()
    return (v_list*cell_size).flatten().astype(np.int32)


@njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
def grid_to_clist(xy_list, rgbo_grid):
    c_list = np.zeros((len(xy_list), 6, 4), dtype='f8')
    for ii in prange(len(xy_list)):
        x, y = xy_list[ii]
        c_list[ii] = rgbo_grid[x, y]
    return c_list.flatten()