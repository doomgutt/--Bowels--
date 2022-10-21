import numpy as np
import pyglet
import time
from numba import njit, prange
from src.game import discrete_space as ds


class LightSource:
    def __init__(self, xy, grid, group, density=360, ray_steps=1000):
        self.batch = grid.batch
        self.group = group
        self.grid_ref = grid
        self.xy = np.array(xy)
        self.center = self.xy + [0.5, 0.5]
        self.all_xy = grid.all_xy

        # --- x_range ---
        dims = self.grid_ref.dims
        self.x_range = np.linspace(0, dims[0]-1, dims[0])
        self.x_range = self.x_range.astype(int)

        # --- radial setup ---
        self.radial = np.linspace(0, 2*np.pi, density, endpoint=False)

        # --- light setup ---
        ray_len = np.sqrt(dims[0]**2 + dims[1]**2)
        self.cell_brightness = 2
        self.refl_ray_len = ray_len*2
        self.ray_steps = ray_steps
        self.rgbo = np.array([200, 200, 100, 0])

        # --- make light ---
        self.rays = self.ray_array(self.radial, ray_len, self.ray_steps)

    def mk_light_grid(self, object_grid):
        return self.get_light_grid(self.center, self.rays, object_grid, self.cell_brightness)

    @staticmethod
    @njit(nogil=True, parallel=True, cache=True)
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
    
    # --- Update Light -------------------------------------------------
    @staticmethod
    @njit(nogil=True, cache=True)
    def get_light_grid(xy, rays, object_grid, brightness):
        light_grid = np.zeros_like(object_grid)
        for ii in prange(len(rays)):
            for jj in prange(len(rays[ii][0])):
                x = np.int64(rays[ii][0][jj] + xy[0])
                y = np.int64(rays[ii][1][jj] + xy[1])
                if object_grid[x, y] in (0, 2):
                    light_grid[x, y] += brightness
                else:
                    break
        return light_grid

    # @staticmethod
    # @njit(nogil=True, parallel=True, cache=True)
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
    # @njit(nogil=True, cache=True)
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
    # @njit(nogil=True, cache=True)
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


