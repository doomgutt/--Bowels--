import numpy as np
from src.game import physics
from src.game import grid_rgbo
from src.game import open_gl
from src.game import discrete_geometry as dg

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================


class Eyes:
    def __init__(self, grid):
        anchor = (4, 4)
        grid_info = (grid.cell_size, grid.batch, grid.groups[2])
        self.mk_floor_vlist(anchor, *grid_info)
        self.mk_far_vlist(anchor, *grid_info)

    # --- Floor --------------------------------------------------------------
    def mk_floor_vlist(self, anchor, cell_size, batch, group):
        self.floor_idx = np.array(dg.bresenham_circle_tweaked(1))
        self.floor_vlist = open_gl.mk_vlist(
            anchor, cell_size, self.floor_idx, batch, group)
    
    def see_floor(self, xy, grid):
        xy_list = self.floor_idx + xy
        clist = grid_rgbo.grid_to_clist(xy_list, (0, 1, 2), grid)
        self.floor_vlist.colors = clist

    # --- Far ----------------------------------------------------------------
    def mk_far_vlist(self, anchor, cell_size, batch, group):
        self.far_idx = np.array(dg.bresenham_circle_tweaked(2))
        self.far_vlist = open_gl.mk_vlist(
            anchor, cell_size, self.far_idx, batch, group)
    
    def see_far(xy):
        pass



