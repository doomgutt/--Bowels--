import numpy as np
import pyglet
from numba import njit, prange, guvectorize
import time

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================

@njit
def rand_col(rgbo, type, amount=10):
    if type == 'col':
        rnd = np.random.randint(-amount, amount, 3)
    elif type == 'bw':
        rnd = np.repeat(np.random.randint(-amount, amount), 3)
    rgbo[:3] += rnd
    return rgbo


# def printFPS(dt):
#     print(pyglet.clock.get_fps())

def fps_custom_display(window):
    fps_display = pyglet.window.FPSDisplay(window=window)
    fps_display.label.font_name = 'Verdana'
    fps_display.label.font_size = 8
    fps_display.label.x = 10
    fps_display.label.y = 10
    fps_display.label.color = (255, 255, 255, 255)
    fps_display.update_period = 1
    return fps_display


@njit(nogil=True, cache=True)
def discrete_line(xy1, xy2):
    dxdy = xy2 - xy1
    N = np.max(np.abs(dxdy))
    xy_inc = dxdy/N

    xy_list = np.zeros((N, 2), dtype='f8')
    xy = xy1.astype('f8')
    xy_list[0] = np.floor(xy)
    for ii in range(1, N):
        xy += xy_inc
        xy_list[ii] = np.floor(xy)
    return xy_list


# class RGBOmap:
#     """
#     Grid layers:
#     0, 0       = floor
#     0, 1       = walls
#     1, [1 -10] = light
#     1, [11-20] = smell
#     1, [21-30] = sound
#     2, 0       = agents
#     --------------------
#     [x, y, x]:
#         x: type of 'object'
#         y: subtype of 'object'
#         z: value representing existence/status
#     --------------------
#     0: terrain
#         0,0: floors
#         0,1: walls
#     1: physics
#         1,(0-9):  light
#         1,(10-19): smell
#         1,(20-29): sound
#     2: agents
#         2,0: _agent
#         2,1: eye
#         2,2: ear
#         2,3: nose

#     """
    
#     def __init__(self, grid):
#         self.grid_ref = grid
#         self.rgbo_empty = [0, 0, 0, 0]
#         self.all_xy = grid.all_xy
#         # self.dims = grid.dims
        
#         l_dims = grid.layers.shape
#         self.empty_rgbo = np.zeros((*l_dims, 4), dtype=np.int64)
#         self.lmap = np.zeros((*l_dims[:2], 4), dtype=np.int64)

#         # --- terrain ------------------------------------------
#         self.lmap[0,0] = [20, 20, 20, 255]
#         self.lmap[0,1] = [100, 100, 100, 255]
#         # --- physics ------------------------------------------
#         self.lmap[1,0] = [245, 183, 39, 1]
#         # --- agents -------------------------------------------
#         self.lmap[2,0] = [200, 200, 200, 255]
#         self.lmap[2,1] = [0, 0, 0, 0]
#         self.lmap[2,2] = [0, 0, 0, 0]
#         self.lmap[2,3] = [0, 0, 0, 0]
#         # ------------------------------------------------------

#     def update(self, layers):
#         self.rgbo_grid = make_rgbo_grid(self.all_xy, layers, self.lmap)

# # -------------------------------
# @njit(nogil=NOGIL_TOGGLE, cache=True)
# def make_rgbo_grid(all_xy, layers, lmap):
#     # t0 = time.time()
#     mixed_grid = mk_rgbo_list(all_xy, layers, lmap)
#     # t1 = time.time()
#     # mixed_grid = mix_rgbo_grids(all_xy, rgbo_list)
#     final_grid = to_vlist_rgbo(all_xy, mixed_grid)
#     # t2 = time.time()
#     # print(t1-t0)
#     # print(t2-t1)
#     return final_grid

# @njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
# def to_vlist_rgbo(all_xy, mixed_grid):
#     sh = mixed_grid.shape
#     expanded_grid = np.zeros((sh[0], sh[1], 6, 4))
#     for ii in prange(len(all_xy)):
#         x, y = all_xy[ii]
#         expanded_grid[x,y] = mixed_grid[x,y]
#     return expanded_grid.astype(np.int64).flatten()

# @njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
# def mk_rgbo_list(all_xy, l, lmap):
#     sh = l.shape
#     rgbo = np.zeros((sh[2], sh[3], 4))
#     # print(rgbo.shape)
#     rgbo_list = np.zeros((sh[0]*sh[1], 4))
#     for ii in prange(len(all_xy)):
#         x, y = all_xy[ii]
#         rgbo_list[0] = floor_rgbo(l[0,0,x,y], lmap[0,0])
#         rgbo_list[1] = walls_rgbo(l[0,1,x,y], lmap[0,1])
#         # rgbo_list[2,x,y] = light_rgbo(l[1,0,x,y], lmap[1,0])
#         # rgbo_list[3,x,y] = agent_rgbo(l[2,0,x,y], lmap[2,0])
#         rgbo[x, y] = mix_rgbo_list(rgbo_list)
#     return np.clip(rgbo, 0, 255)

# # @njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
# # def mk_rgbo_list(all_xy, l, lmap):
# #     sh = l.shape
# #     rgbo_list = np.zeros((sh[0]*sh[1], sh[2], sh[3], 4))
# #     rgbo = np.zeros(rgbo_list.shape[1:])
# #     for ii in prange(len(all_xy)):
# #         x, y = all_xy[ii]
# #         rgbo_list[0,x,y] = floor_rgbo(l[0,0,x,y], lmap[0,0])
# #         rgbo_list[1,x,y] = walls_rgbo(l[0,1,x,y], lmap[0,1])
# #         # rgbo_list[2,x,y] = light_rgbo(l[1,0,x,y], lmap[1,0])
# #         # rgbo_list[3,x,y] = agent_rgbo(l[2,0,x,y], lmap[2,0])
# #         rgbo[x, y] = mix_rgbo_list(rgbo_list[:, x, y])
# #     return np.clip(rgbo, 0, 255)

# # -------------------------------
# @njit(nogil=NOGIL_TOGGLE, cache=True)
# def floor_rgbo(val, rgbo):
#     return rgbo

# @njit(nogil=NOGIL_TOGGLE, cache=True)
# def walls_rgbo(val, rgbo):
#     return val*rgbo

# @njit(nogil=NOGIL_TOGGLE, cache=True)
# def light_rgbo(val, rgbo):
#     col = rgbo.copy()
#     col[3] = val
#     return col

# @njit(nogil=NOGIL_TOGGLE, cache=True)
# def agent_rgbo(val, rgbo):
#     return rgbo


# # @njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
# # def mix_rgbo_grids(all_xy, rgbo_list):
# #     rgbo = np.zeros(rgbo_list.shape[1:])
# #     for ii in prange(len(all_xy)):
# #         x, y = all_xy[ii]
# #         rgbo[x, y] = mix_rgbo_list(rgbo_list[:, x, y])
# #     return rgbo


# @njit(nogil=NOGIL_TOGGLE, cache=True)
# def mix_rgbo_list(rgbo_list):
#     # find strongest opacity
#     rgbo_list = rgbo_list.astype(np.float64)
#     start_idx = 0
#     for ii, rgbo in enumerate(rgbo_list):
#         if rgbo[-1] == 255:
#             start_idx = ii

#     # recursively calculate new_rgbo
#     new_rgbo_list = rgbo_list[start_idx:]
#     new_rgbo = new_rgbo_list[0]
#     for rgbo in new_rgbo_list[1:]:
#         new_rgbo = mix_rgbo(new_rgbo, rgbo)

#     return new_rgbo.astype(np.int64)






# # ==================================
# def test_v_lists():
#     vlist_list = []
#     rgbo1 = [0,   0,   0, 255]
#     rgbo2 = [255, 0,   0, 200]
#     rgbo3 = [0,   100,   0, 130]
#     rgbo4 = [66,   2,   51, 20  ]

#     # ==== mixed ======
#     rgbo_mix = mix_rgbo_list(np.array([rgbo1, rgbo2, rgbo3, rgbo4])).tolist()
#     coords_mix = (100, 100, 100, 200, 200, 200, 200, 200, 100, 100, 200, 100)
#     vlist_mix = pyglet.graphics.vertex_list(6, ('v2i', coords_mix), ('c4B', rgbo_mix * 6))

#     # ==== natural ====
#     coords1 = (200, 100, 200, 200, 300, 200, 300, 200, 200, 100, 300, 100)
#     vlist1 = pyglet.graphics.vertex_list(6, ('v2i', coords1), ('c4B', rgbo1 * 6))
#     vlist2 = pyglet.graphics.vertex_list(6, ('v2i', coords1), ('c4B', rgbo2 * 6))
#     vlist3 = pyglet.graphics.vertex_list(6, ('v2i', coords1), ('c4B', rgbo3 * 6))
#     vlist4 = pyglet.graphics.vertex_list(6, ('v2i', coords1), ('c4B', rgbo4 * 6))

#     # === add stuff ====
#     vlist_list.append(vlist_mix)
#     vlist_list.append(vlist1)
#     vlist_list.append(vlist2)
#     vlist_list.append(vlist3)
#     vlist_list.append(vlist4)
#     return vlist_list