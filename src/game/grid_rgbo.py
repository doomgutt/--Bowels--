import numpy as np
from numba import njit, guvectorize

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
V_TARGET = 'cpu'
# ============================


# === RGBO REF ===============================================================
def mk_rgbo_ref():
    rgbo_ref = np.zeros((3, 5, 256, 4), dtype='f8')
    rgbo_ref[:, :, :] = [0, 0, 0, 0]

    # --- basics ---
    rgbo_ref[0, 0, 0] = [0,   0,   0,   255]
    rgbo_ref[0, 0, 1] = [255, 0,   0,   255]
    rgbo_ref[0, 0, 2] = [0,   255, 0,   255]
    rgbo_ref[0, 0, 3] = [0,   0,   255, 255]
    rgbo_ref[0, 0, 4] = [255, 255, 255, 255]

    # --- terrain ---
    # floor
    rgbo_ref[0, 1, 0] = [30,  30,  30, 255]

    # walls
    rgbo_ref[0, 2, 0] = [0,   0,   0,  0]
    rgbo_ref[0, 2, 1] = [90,  90,  90, 255]
    rgbo_ref[0, 2, 2] = [120, 120, 80, 255]

    # --- physics ---
    # light
    for n in range(256):
        rgbo_ref[1, 1, n] = [200, 200, 100, n/4]

    # --- agents ---
    rgbo_ref[2, 0, 0] = [0,   0,   0,  0  ]
    rgbo_ref[2, 0, 1] = [100, 200, 0,  255]
    rgbo_ref[2, 0, 2] = [255, 0,   0,  255]
    rgbo_ref[2, 0, 3] = [0,   255, 0,  255]
    

    return rgbo_ref/255

# === Layers to RGBO =========================================================
@njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
def layer_to_rgbo(layers, cat_i, typ_i, rgbo_ref):
    l = layers[cat_i, typ_i]
    r1 = l.shape[0]
    r2 = l.shape[1]
    rgbo_grid = np.zeros((l.shape[0], l.shape[1], 4), dtype="f8")
    for x in range(r1):
        for y in range(r2):
            a = rgbo_ref[cat_i, typ_i, l[x, y]].copy()
            rgbo_grid[x, y] = a
    return np.clip(rgbo_grid, 0, 255)



# === Mix 2 rgbo grids =======================================================
@guvectorize("(f8[:,:,:], f8[:,:,:], f8[:,:,:])", '(i,j,x),(i,j,x)->(i,j,x)',
             target=V_TARGET, nopython=True, cache=True)
def mix_2_rgbo_grids(rgbo_grid_1, rgbo_grid_2, rgbo_grid_mixed):
    r1 = rgbo_grid_1.shape[0]
    r2 = rgbo_grid_1.shape[1]
    for i in range(r1):
        for j in range(r2):
            c1 = rgbo_grid_1[i, j, :3]
            a1 = rgbo_grid_1[i, j, -1]
            c2 = rgbo_grid_2[i, j, :3]
            a2 = rgbo_grid_2[i, j, -1]
            a_out = 1 - (1 - a2) * (1 - a1)
            c_out = c2*a2/a_out + c1*a1*(1-a2)/a_out
            rgbo_grid_mixed[i, j, :3] = c_out
            rgbo_grid_mixed[i, j, 3] = a_out




# === TODO ===================================================================
# chosen layers rgbo mix
# chosen coords rgbo mix




# === EXTRAS =================================================================
@njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
def mix_rgbo(rgbo1, rgbo2):
    """
    first rgbo has to have opacity = 255
    """
    if rgbo1[-1] == 0:
        return rgbo1
    new_rgbo = np.array([0, 0, 0, 255], np.float64)
    new_rgbo[:3] = rgbo1[:3]*(1-rgbo2[-1]/255) + rgbo2[:3]*(rgbo2[-1]/255)
    return new_rgbo