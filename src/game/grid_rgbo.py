import numpy as np
from numba import njit, guvectorize

# === NUMBA SETUP ============
NOGIL_TOGGLE = False
PARALLEL_TOGGLE = False
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
    rgbo_ref[0, 1, 0] = [60,  20,  10, 255]

    # walls
    rgbo_ref[0, 2, 0] = [0,   0,   0,  0]
    rgbo_ref[0, 2, 1] = [70,  70,  90, 255]
    rgbo_ref[0, 2, 2] = [120, 120, 60, 255]

    # --- physics ---
    # light
    for n in range(256):
        rgbo_ref[1, 1, n] = [200, 200, 100, n/3]

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
@njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
def mix_2_rgbo_grids(rgbo_grid_1, rgbo_grid_2):
    r1 = rgbo_grid_1.shape[0]
    r2 = rgbo_grid_1.shape[1]
    rgbo_grid_mixed = np.zeros_like(rgbo_grid_1)
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
    return rgbo_grid_mixed

# === Make and Mix RGBO grids ================================================
@njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
def add_noise(rgbog, r_val=3, r_type='bw'):
    n = 3 if r_type == 'col' else 1
    dims = (rgbog.shape[0], rgbog.shape[1], n)
    rgbog[:,:,:3] += np.random.randint(-r_val, r_val, dims)/100
    return rgbog

@njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
def rgbog_mkr(layers, rgbo_ref, id_list, id_rnd=(), init_rgbog=None):
    """
    id_list - list of xy coords
    id_rnd - idx the id_list for which grids should
                have random noise applied
    """
    if init_rgbog == None:
        no_init_check = True
    else:
        mixed = init_rgbog
        no_init_check = False
    for i, mn in enumerate(id_list):
        rgbog = layer_to_rgbo(layers, *mn, rgbo_ref)
        if i in id_rnd:
            rgbog = add_noise(rgbog, r_val=3, r_type='bw')
        if no_init_check:
            mixed = rgbog
            no_init_check = False
        else:
            mixed = mix_2_rgbo_grids(mixed, rgbog)
    return mixed

# === Set Light Brightness ===================================================
@njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
def set_brightness(rgbog, light_grid, br_mult, br_min):
    l_grid = np.clip(br_mult*light_grid, br_min, 1)
    rgbog[:,:,-1] = l_grid
    return rgbog

# === EXTRAS =================================================================
def get_xy_list(max_x, max_y):
    x = np.arange(max_x, dtype='i8')
    y = np.arange(max_y, dtype='i8')
    return np.transpose([np.tile(x, len(y)), np.repeat(y, len(x))])


@njit
def rand_col(rgbo, type, amount=10):
    if type == 'col':
        rnd = np.random.randint(-amount, amount, 3)
    elif type == 'bw':
        rnd = np.repeat(np.random.randint(-amount, amount), 3)
    rgbo[:3] += rnd
    return rgbo
    



# ========================================================
# ========================================================
# @guvectorize("(f8[:,:,:], f8[:,:,:], f8[:,:,:])", '(i,j,x),(i,j,x)->(i,j,x)',
#              target=V_TARGET, nopython=True, cache=True)
# def mix_2_rgbo_grids(rgbo_grid_1, rgbo_grid_2, rgbo_grid_mixed):
#     r1 = rgbo_grid_1.shape[0]
#     r2 = rgbo_grid_1.shape[1]
#     for i in range(r1):
#         for j in range(r2):
#             c1 = rgbo_grid_1[i, j, :3]
#             a1 = rgbo_grid_1[i, j, -1]
#             c2 = rgbo_grid_2[i, j, :3]
#             a2 = rgbo_grid_2[i, j, -1]
#             a_out = 1 - (1 - a2) * (1 - a1)
#             c_out = c2*a2/a_out + c1*a1*(1-a2)/a_out
#             rgbo_grid_mixed[i, j, :3] = c_out
#             rgbo_grid_mixed[i, j, 3] = a_out

# @njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
# def mix_rgbo(rgbo1, rgbo2):
#     """
#     first rgbo has to have opacity = 255
#     """
#     if rgbo1[-1] == 0:
#         return rgbo1
#     new_rgbo = np.array([0, 0, 0, 255], np.float64)
#     new_rgbo[:3] = rgbo1[:3]*(1-rgbo2[-1]/255) + rgbo2[:3]*(rgbo2[-1]/255)
#     return new_rgbo