import numpy as np
from src.game import physics
from src.game import grid_rgbo
from src.game import open_gl_tools
# import pyglet
# import time

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================

class Eyes():
    pass

class Ears():
    pass

class Nose():
    pass

class Touch():
    pass


class SightGrid:
    def __init__(self, grid):
        self.GRID = grid
        self.xy_list = grid_rgbo.get_xy_list(3, 3)
        
        anchor = (0, 0)
        size_mult = 2
        self.vlist = self.GRID.mk_vlist(
            np.array(anchor), 
            self.xy_list,
            self.GRID.groups[1],
            self.GRID.cell_size*size_mult
        )
        
        # self.set_sight_density(10)
        # self.RADIAL = physics.Radial(xy, grid)
        # self.rays = self.RADIAL.rays

    def update(self, xy, grid_layers):
        xy_l = self.xy_list + xy -1
        xmin, xmax = xy_l[0, 0], xy_l[-1,0]+1
        ymin, ymax = xy_l[0, 1], xy_l[-1,1]+1
        glayers = grid_layers[:,:, xmin:xmax, ymin:ymax]
        terrain = self.GRID.terrain_rgbo[xmin:xmax, ymin:ymax, :]
        id_list = ((2, 0), (1, 1))
        settings = (glayers, self.GRID.rgbo_ref, id_list, (), terrain)
        rgbog = grid_rgbo.rgbog_mkr(*settings)
        rgbog = grid_rgbo.set_brightness(rgbog, glayers[1, 1], 0.009, 0.2)
        self.vlist.colors = open_gl_tools.grid_to_clist(self.xy_list, rgbog)

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


