import numpy as np
from numba import njit
import pyglet


class LightSource:
    def __init__(self, grid, xy, batch, group):
        self.batch = batch
        self.group = group
        self.grid_ref = grid
        self.xy = np.array(xy)
        self.center = self.xy + [0.5, 0.5]

        # --- x_range ---
        dims = self.grid_ref.dims
        self.x_range = np.linspace(0, dims[0]-1, dims[0])
        self.x_range = self.x_range.astype(int)

        # --- radial setup ---
        light_density = 360
        self.radial = np.linspace(0, 2*np.pi, light_density, endpoint=False)

        # --- light setup ---
        ray_len = np.sqrt(dims[0]**2 + dims[1]**2)
        self.cell_brightness = 2
        self.refl_ray_len = ray_len*2
        self.ray_steps = 1000

        # --- make light ---
        self.rays = self.ray_array(self.radial, ray_len, self.ray_steps)
        


    # === Drawing Light ================================================
    def beams_origin_to_vertices(self, vertices, xy=None):
        if xy == None:
            xy = self.center
        else:
            xy = self.xy
        beams = []
        for v in vertices:
            beam = pyglet.shapes.Line(
                *(xy+1)*self.grid_ref.cell_size,
                *(v+1)*self.grid_ref.cell_size,
                width=1,
                batch=self.batch, group=self.group)
            beam.opacity = 60
            beams.append(beam)
        return beams

    def draw(self):
        drawn = []
        grid = self.grid_ref.layers[0] # change later to include agents
        
        # grid lighting
        light_grid = self.get_light_grid(
            self.center, self.rays, grid, self.cell_brightness)
        drawn.append(self.draw_lmap(light_grid))
        
        # beam lighting
        ray_ends = self.get_light_rays(self.center, self.rays, grid)
        drawn.append(self.beams_origin_to_vertices(ray_ends))

        return drawn
    
    def draw_lmap(self, light_grid):
        """
        draws the brightness map
        """
        active_map = np.clip(light_grid, 0, 255)
        squares = []
        for x, row in enumerate(active_map):
            for y, brightness in enumerate(row):
                if brightness == 0: continue
                square = self.grid_ref.draw_square(
                    x, y, [[200, 200, 0], brightness])
                squares.append(square)
        return squares

    # === Update Light =================================================
    @staticmethod
    @njit(nogil=True, cache=True)
    def get_light_grid(xy, rays, grid, brightness):
        light_grid = np.zeros_like(grid)
        for ii, ray in enumerate(rays):
            for jj in range(len(ray[0])):
                x = int(ray[0][jj] + xy[0])
                y = int(ray[1][jj] + xy[1])
                if grid[x, y] == 0:
                    light_grid[x, y] += brightness
                else:
                    break
        return np.clip(light_grid, 0, 255)
    
    @staticmethod
    @njit(nogil=True, cache=True)
    def get_light_rays(xy, rays, grid):
        ray_ends = np.zeros((len(rays), 2))
        for ii, ray in enumerate(rays):
            for jj in range(len(ray[0])):
                x = int(ray[0][jj] + xy[0])
                y = int(ray[1][jj] + xy[1])
                if grid[x, y] != 0:
                    ray_ends[ii][0] = ray[0][jj] + xy[0]
                    ray_ends[ii][1] = ray[1][jj] + xy[1]
                    break
        return ray_ends

    # --- experimental ------------------------------------------------
    @staticmethod
    @njit(nogil=True, cache=True)
    def get_light_rays_w_reflection(xy, rays, grid):
        ray_ends = np.zeros((len(rays), 2))
        for ii, ray in enumerate(rays):
            for jj in range(len(ray[0])):
                x = int(ray[0][jj] + xy[0])
                y = int(ray[1][jj] + xy[1])
                if grid[x, y] != 0:
                    ray_ends[ii][0] = ray[0][jj] + xy[0]
                    ray_ends[ii][1] = ray[1][jj] + xy[1]
                    break
        return ray_ends

    # === Light Setup =================================================
    @staticmethod
    @njit(nogil=True, parallel=True)
    def ray_array(radial, r, ray_steps=1000):
        rays = np.zeros((len(radial), 2, ray_steps))

        x_steps = np.sin(radial)*r
        y_steps = np.cos(radial)*r

        for ii in range(len(radial)):
            x_coords = np.linspace(0, x_steps[ii], ray_steps)
            y_coords = np.linspace(0, y_steps[ii], ray_steps)
            rays[ii][0] = x_coords
            rays[ii][1] = y_coords

        return rays