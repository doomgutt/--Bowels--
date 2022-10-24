import numpy as np
from src.game import physics
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
    def __init__(self, xy, grid):
        self.xy = xy
        self.RADIAL = physics.Radial(xy, grid)
        self.set_sight_density(10)
        self.rays = self.RADIAL.rays

    def update(self, xy, grid):
        self.xy = xy

        # floor
        grid.layers[0, 1]
        # walls
        grid.layers[0, 2]
        # agents
        grid.layers[2, 0]
        # light
        grid.layers[1, 1]

    @staticmethod
    def sight_grid(xy, light_grid, collisions_coords):
        sight_grid = np.zeros((5,5))
        sight_grid[1:4, 1:4] = light_grid[xy[0]-1:xy[0]+1, xy[1]-1:xy[1]+1]

    def collisions_to_grid(self, xy, object_grid):
        coll_ii_jj, coll_ids = self.RADIAL.get_collisions(xy, self.rays, object_grid)
        pass

    def set_sight_density(self, density_mult):
        density = 16*(density_mult*2+1)
        self.RADIAL.set_radial(density, roll=density_mult)