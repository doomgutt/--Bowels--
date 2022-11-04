import numpy as np
from numba import njit, prange

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================


@njit(nogil=NOGIL_TOGGLE, cache=True)
def bresenham_lines(start, end, max_iter):
    """
    - Normalizing Slope
        - dxdy: calculate slopes: ends-starts
        - scale: get furthest x/y distance for every dxdy
            - set 0 slope entries to 1's (when two points are the same)
        - nslope: normalized slope
    - Calculate lines
        - npts, dims: number of points and point dimensions
        - max_iter: get furthest distance for any two points
    """

    # Normalizing slope
    dxdy = (end - start)
    abs_dxdy = np.abs(dxdy)
    scale = np.zeros((len(abs_dxdy), 1), dtype='i8')
    for ii, xy in enumerate(abs_dxdy):
        sc = max(xy)
        scale[ii] = sc if sc != 0 else 1
    nslope = dxdy.astype('f8') / scale

    # Steps to iterate on
    npts, dim = start.shape
    if max_iter == -1: max_iter = np.max(scale)
    stepseq = np.arange(1, max_iter + 1)
    stepmat = stepseq.repeat(dim).reshape((-1, dim))

    # Calculate lines
    bline = np.zeros((len(start), *stepmat.shape), dtype='f8')
    for ii, start_xy in enumerate(start):
        bline[ii] = start_xy + nslope[ii] * stepmat

    return np.rint(bline)


class Radial:
    def __init__(self, xy, grid, density=360, ray_steps=1000):
        self.grid_ref = grid
        self.xy = np.array(xy)
        # self.center = self.xy + [0.5, 0.5]
        self.all_xy = grid.all_xy

        # --- x_range ---
        dims = self.grid_ref.dims
        self.x_range = np.linspace(0, dims[0]-1, dims[0], dtype=int)

        # --- radial setup ---
        self.ray_steps = ray_steps
        self.set_radial(density, roll=0)

    def set_radial(self, density, roll):
        radial = np.linspace(0, 2*np.pi, density, endpoint=False)
        self.radial = np.roll(radial, roll)
        dims = self.grid_ref.dims
        ray_len = np.sqrt(dims[0]**2 + dims[1]**2)
        self.rays = self.ray_array(self.radial, ray_len, self.ray_steps)

    @staticmethod
    @njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
    def ray_array(radial, r, ray_steps):
        rays = np.zeros((len(radial), 2, ray_steps))
        x_steps = np.sin(radial)*r
        y_steps = np.cos(radial)*r
        for ii in range(len(radial)):
            x_coords = np.linspace(0, x_steps[ii], ray_steps)
            y_coords = np.linspace(0, y_steps[ii], ray_steps)
            rays[ii][0] = x_coords
            rays[ii][1] = y_coords
        return rays
    
    @staticmethod
    @njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
    def get_collisions(xy, rays, object_grid):
        ctr = xy + 0.5
        coll_ii_jj = np.zeros((len(rays), 1))
        coll_ids = np.zeros((len(rays), 1))
        for ii in prange(len(rays)):
            for jj in prange(len(rays[ii][0])):
                x = np.int64(rays[ii][0][jj] + ctr[0])
                y = np.int64(rays[ii][1][jj] + ctr[1])
                if object_grid[x,y] != 0:
                    coll_ii_jj[ii] == jj
                    coll_ids[ii] = object_grid[x,y]
        return coll_ii_jj, coll_ids

    def get_collisions_w_reflection():
        pass

    # def get_light_grid(xy, rays, object_grid, brightness):
    #     ctr = xy + 0.5
    #     light_grid = np.zeros_like(object_grid)
    #     for ii in prange(len(rays)):
    #         for jj in prange(len(rays[ii][0])):
    #             x = np.int64(rays[ii][0][jj] + ctr[0])
    #             y = np.int64(rays[ii][1][jj] + ctr[1])
    #             if object_grid[x, y] in (0, 2):
    #                 light_grid[x, y] += brightness*0.8
    #             else:
    #                 light_grid[x, y] += 30
    #                 break
    #     # self_pos = np.round(ctr)
    #     light_grid[int(ctr[0]), int(ctr[1])] = 10
    #     return light_grid



    # --- Update Light -------------------------------------------------
    # @staticmethod
    # @njit(nogil=NOGIL_TOGGLE, cache=True)
    # def get_light_grid(xy, rays, object_grid, brightness):
    #     light_grid = np.zeros_like(object_grid)
    #     for ii in prange(len(rays)):
    #         for jj in prange(len(rays[ii][0])):
    #             x = np.int64(rays[ii][0][jj] + xy[0])
    #             y = np.int64(rays[ii][1][jj] + xy[1])
    #             if object_grid[x, y] in (0, 2):
    #                 light_grid[x, y] += brightness*0.8
    #             else:
    #                 light_grid[x, y] += 30
    #                 break
    #     # self_pos = np.round(xy)
    #     light_grid[int(xy[0]), int(xy[1])] = 10
    #     return light_grid
