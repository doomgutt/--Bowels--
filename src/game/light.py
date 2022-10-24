import numpy as np
from numba import njit, prange
from src.game import physics

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================

class LightSource(physics.Radial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rgbo = np.array([200, 200, 100, 0])
        self.brightness = 0.8

    def mk_light_grid(self, object_grid):
        return self.get_light_grid(self.xy, self.rays, object_grid, self.brightness)
    
    # --- Update Light -------------------------------------------------
    @staticmethod
    @njit(nogil=NOGIL_TOGGLE, cache=True)
    def get_light_grid(xy, rays, object_grid, brightness):
        ctr = xy + 0.5
        light_grid = np.zeros(object_grid.shape, dtype=np.float64)
        for ii in prange(len(rays)):
            for jj in prange(len(rays[ii][0])):
                x = np.int64(rays[ii][0][jj] + ctr[0])
                y = np.int64(rays[ii][1][jj] + ctr[1])
                if object_grid[x, y] in (0, 2):
                    light_grid[x, y] += brightness
                else:
                    light_grid[x, y] += brightness*20
                    break
        # light_grid[int(ctr[0]), int(ctr[1])] = 10
        return light_grid.astype(np.int64)

    # @staticmethod
    # @njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
    # def get_light_cols(all_xy, light_grid, rgbo):
    #     rgbo_map = np.zeros((len(all_xy), 6, 4))
    #     for ii in prange(len(all_xy)):
    #         x, y = all_xy[ii]
    #         brightness = light_grid[x, y]
    #         col = rgbo.copy()
    #         col[3] = brightness
    #         rgbo_map[ii] = col
    #     return rgbo_map.flatten().astype(np.int32)

    # === Ray Stuff =================================================

    # @staticmethod
    # @njit(nogil=NOGIL_TOGGLE, cache=True)
    # def get_light_rays(xy, rays, grid):
    #     ray_ends = np.zeros((len(rays), 2))
    #     for ii, ray in enumerate(rays):
    #         for jj in range(len(ray[0])):
    #             x = int(ray[0][jj] + xy[0])
    #             y = int(ray[1][jj] + xy[1])
    #             if grid[x, y] != 0:
    #                 ray_ends[ii][0] = ray[0][jj] + xy[0]
    #                 ray_ends[ii][1] = ray[1][jj] + xy[1]
    #                 break
    #     return ray_ends

    # # --- experimental ------------------------------------------------
    # @staticmethod
    # @njit(nogil=NOGIL_TOGGLE, cache=True)
    # def get_light_rays_w_reflection(xy, rays, grid):
    #     ray_ends = np.zeros((len(rays), 2))
    #     for ii, ray in enumerate(rays):
    #         for jj in range(len(ray[0])):
    #             x = int(ray[0][jj] + xy[0])
    #             y = int(ray[1][jj] + xy[1])
    #             if grid[x, y] != 0:
    #                 ray_ends[ii][0] = ray[0][jj] + xy[0]
    #                 ray_ends[ii][1] = ray[1][jj] + xy[1]
    #                 break
    #     return ray_ends

    # # === extras =======================================================
    # def beams_origin_to_vertices(self, vertices, xy=None):
    #     if xy == None:
    #         xy = self.center
    #     else:
    #         xy = self.xy
    #     beams = []
    #     for v in vertices:
    #         beam = pyglet.shapes.Line(
    #             *(xy+1)*self.grid_ref.cell_size,
    #             *(v+1)*self.grid_ref.cell_size,
    #             width=1,
    #             batch=self.batch, group=self.group)
    #         beam.opacity = 60
    #         beams.append(beam)
    #     return beams
    
    # def draw_lmap(self, light_grid):
    #     """
    #     draws the brightness map
    #     """
    #     active_map = np.clip(light_grid, 0, 255)
    #     squares = []
    #     for x, row in enumerate(active_map):
    #         for y, brightness in enumerate(row):
    #             if brightness == 0: continue
    #             square = self.grid_ref.draw_square(
    #                 x, y, [[200, 200, 0], brightness])
    #             squares.append(square)
    #     return squares


