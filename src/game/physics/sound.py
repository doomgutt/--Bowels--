import numpy as np
from numba import njit
from src.game import discrete_geometry as dg

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================

# keep track of all sound origins
# for every sound origin keep track of "distance from origin"
# for every sound origin update grid soundscape according to radial[distance]


class SoundTracker():
    def __init__(self, grid):
        self.sound_grid = np.zeros(grid.layers[0].shape, dtype='f8')
        self.radial = dg.rad_radial(grid.dims)
        self.sound_speed = 1
        self.dt = 0
        self.sound_rgbo = np.array([0.8, 0.8, 0.8, 1])

    def update(self, dt, grid):
        self.sound_grid[:,:] = 0
        mv_coords = self.get_movement_coords(grid)
        for xy in mv_coords:
            self.sound_grid[xy[0], xy[1]] = 1
        if self.tick(dt, self.sound_speed):
            self.move_sounds()

    def move_sounds(self):
        pass

    def get_movement_coords(self, grid):
        mv_coords = []
        for agent in grid.agents:
            if agent.moving:
                mv_coords.append(agent.xy)
        return mv_coords

    def tick(self, dt, mult):
        self.dt += dt
        if self.dt*mult > 1:
            self.dt = 0
            return True
        return False

class SoundBeam():
    def __init__(self, origin):
        self.origin = np.array(origin)
        self.b_line = None
    
    def update(object_grid):

        pass

