import numpy as np
from src.game.physics import physics
from src.game import grid_rgbo
from src.game import open_gl
from src.game import discrete_geometry as dg
# import pyglet
# import time

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================

# class Eyes:
#     def __init__(self, batch, group):
#         anchor = (4, 4)
#         cell_size = 10
#         self.mk_floor_vlist(anchor, cell_size, batch, group)
#         self.mk_far_vlist(anchor, cell_size, batch, group)
    
#     # --- Update colours -----------------------------------------------------
#     def see_floor(self, xy, grid):
#         rgbo_list = self.get_floor_rgbo(xy, grid)

#     def update_floor_v_list():
#         pass

#     def see_far(xy):
#         pass

#     def get_floor_rgbo(self, xy, grid):
#         # make index
#         id_indices = [(0, 0), (0, 1), (2, 0)]
        
#         # make rgbo lists
#         rgbo_lists = []
#         for id_idx in id_indices:
#             rgbo_lists.append(grid_rgbo.idx_to_rgbo(
#                 self.floor_idx+xy, id_idx, grid.layers, grid.rgbo_ref))

#         # mix rgbo lists
#         rgbo_lists = np.array(rgbo_lists)
#         mixed_rgbo = grid_rgbo.mix_rgbo_lists(rgbo_lists)
    
#     # --- Set up Vertex Lists ------------------------------------------------
#     def mk_floor_vlist(self, anchor, cell_size, batch, group):
#         self.floor_idx = dg.bresenham_circle(1)
#         self.floor_vlist = open_gl.mk_vlist(
#             anchor, cell_size, self.floor_idx, batch, group)

#     def mk_far_vlist(self, anchor, cell_size, batch, group):
#         self.far_idx = dg.bresenham_circle(2)
#         self.far_vlist = open_gl.mk_vlist(
#             anchor, cell_size, self.far_idx, batch, group)

# class Ears:
#     pass

# class Nose:
#     pass

# class Skin:
#     pass


# class SightGrid:
#     def __init__(self, grid):
#         self.GRID = grid
#         self.xy_list = grid_rgbo.get_xy_list(5, 5)
        
#         anchor = (0, 0)
#         size_mult = 2
#         self.vlist = self.GRID.mk_vlist(
#             np.array(anchor), 
#             self.xy_list,
#             self.GRID.groups[1],
#             self.GRID.cell_size*size_mult
#         )
#         self.vlist.colours = np.ones(len(self.xy_list)*6*4)
        
#         # self.set_sight_density(10)
#         # self.RADIAL = physics.Radial(xy, grid)
#         # self.rays = self.RADIAL.rays

#     def update(self, xy, grid_layers):
#         # idx = np.array([6,7,8, 11,12,13, 16,17,18])
#         xy_l = self.xy_list + xy -1
#         xmin, xmax = xy_l[0, 0], xy_l[-1,0]+1
#         ymin, ymax = xy_l[0, 1], xy_l[-1,1]+1
#         glayers = grid_layers[:,:, xmin:xmax, ymin:ymax]
#         terrain = self.GRID.terrain_rgbo[xmin:xmax, ymin:ymax, :]
#         id_list = ((2, 0), (1, 1))
#         settings = (glayers, self.GRID.rgbo_ref, id_list, (), terrain)
#         rgbog = grid_rgbo.rgbog_mkr(*settings)
#         rgbog = grid_rgbo.set_brightness(rgbog, glayers[1, 1], 0.009, 0.2)
#         self.vlist.colors = open_gl.grid_to_clist(self.xy_list, rgbog)

    # @staticmethod
    # def sight_grid(xy, light_grid, collisions_coords=()):
    #     sight_grid = np.zeros((5,5))
    #     x_list = np.arange(3)+xy[0]-1
    #     y_list = np.arange(3)+xy[1]-1
    #     sight_grid[1:4, 1:4] = light_grid[xy[0]-1:xy[0]+1, xy[1]-1:xy[1]+1]

    # def collisions_to_grid(self, xy, object_grid):
    #     coll_ii_jj, coll_ids = self.RADIAL.get_collisions(xy, self.rays, object_grid)
    #     pass

    # def set_sight_density(self, density_mult):
    #     density = 16*(density_mult*2+1)
    #     self.RADIAL.set_radial(density, roll=density_mult)


