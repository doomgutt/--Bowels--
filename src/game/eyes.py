import numpy as np
from numba import njit
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
        ui_size_mult = 2
        grid_info = (grid.cell_size*ui_size_mult, grid.batch, grid.groups[2])
        self.mk_self_vlist(anchor, *grid_info)
        self.mk_floor_vlist(anchor, *grid_info)
        self.mk_far_vlist(anchor, *grid_info)

    def see(self, xy, grid):
        self.see_self(xy, grid)
        self.see_floor(xy, grid)
        self.see_far(xy, grid)

    # --- Self ---------------------------------------------------------------
    def see_self(self, xy, grid):
        xy_list = xy[None]
        clist = grid_rgbo.grid_to_clist(xy_list, (0, 1, 2), grid)
        self.self_vlist.colors = clist

    def mk_self_vlist(self, anchor, cell_size, batch, group):
        self.self_idx = dg.bresenham_circle_tweaked(0)
        self.self_vlist = open_gl.mk_vlist(
            anchor, cell_size, self.self_idx, batch, group)

    # --- Floor --------------------------------------------------------------
    def see_floor(self, xy, grid):
        xy_list = self.floor_idx + xy
        clist = grid_rgbo.grid_to_clist(xy_list, (0, 1, 2), grid)
        self.floor_vlist.colors = clist

    def mk_floor_vlist(self, anchor, cell_size, batch, group):
        self.floor_idx = dg.bresenham_circle_tweaked(1)
        self.floor_vlist = open_gl.mk_vlist(
            anchor, cell_size, self.floor_idx, batch, group)
    
    # --- Far ----------------------------------------------------------------
    def see_far(self, xy, grid):
        rgbo_list = self.hit_lights(
            xy, self.far_idx, grid.light_colls, grid.rgbo_ref)
        clist = grid_rgbo.rgbo_list_to_clist(rgbo_list)
        self.far_vlist.colors = clist

    def mk_far_vlist(self, anchor, cell_size, batch, group):
        self.far_idx = dg.bresenham_circle_tweaked(2)
        self.far_vlist = open_gl.mk_vlist(
            anchor, cell_size, self.far_idx, batch, group)
    
    # --- collision stuff
    @staticmethod
    @njit(nogil=True, cache=True)
    def hit_lights(xy, xy_list, light_colls, rgbo_ref, br_mod=1):
        rgbo_list = np.zeros((len(xy_list), 4), dtype='f8')
        for coll in light_colls:
            end_xy = coll[1]
            if (end_xy==xy).all():
                g_id, br = coll[2]
                rgbo = rgbo_ref[g_id].copy()
                closest_idx = colls_to_fsight(xy, xy_list, coll[0], 5)
                for i, idx in enumerate(closest_idx):
                    rgbo[-1] = (br/1000)*br_mod*focus_adjust(i)
                    mixed = grid_rgbo.mix_2_rgbo_vals(rgbo_list[idx], rgbo)
                    rgbo_list[idx] = mixed
        return np.clip(rgbo_list, 0, 1)

@njit(nogil=True, cache=True)
def colls_to_fsight(xy, xy_list, coll_xy, n=3):
    a_xy_list = xy_list+xy
    d = (coll_xy - a_xy_list).T
    dists = np.sqrt(d[0]**2 + d[1]**2)
    return np.argsort(dists)[:n]

@njit(nogil=True, cache=True)
def focus_adjust(i):
    adjust = 0
    if i == 0:
        adjust = 1
    elif 0 < i <= 2:
        adjust = 0.2
    elif 2 < i:
        adjust = 0.05
    return adjust 
