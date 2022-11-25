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
        self.radial = dg.rad_radial(grid.dims)
        self.sound_speed = 1
        self.dt = 0

    def update(self, dt, grid):
        # mv_coords = self.get_movement_coords(grid)
        if self.tick(dt, self.m_speed):
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

    # def add_light(self, object_grid, light_grid):
    #     return self._add_light(
    #         self.xy, self.radial, object_grid, light_grid)

    # @staticmethod
    # @njit(nogil=NOGIL_TOGGLE, cache=True)
    # def _add_light(start_xy, radial, object_grid, light_grid, brightness=0.1):
    #     pass