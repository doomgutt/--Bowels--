import numpy as np
# import pyglet


class LightSource:
    def __init__(self, grid, xy, batch, group):
        self.batch = batch
        self.group = group
        self.grid_ref = grid
        self.xy = np.array(xy)
        self.center = self.xy + [0.5, 0.5]

        self.mk_light_map()

    # ==== Draw =================================================
    def draw(self):
        return self.lights_v02()

    # ==== SETUP =========================================
    def mk_light_map(self):
        """
        px: positive x
        nx: negative x

        the idea is
        1. have a pre-made grid of ALL potential tiles
        2. shift that grid around and check light_beams for where they should end
        """

        # --- x_range setup ---
        dims = self.grid_ref.dims
        self.x_range = np.linspace(0, dims[0], dims[0], endpoint=False).astype(int)

        # --- radial setup ---
        self.light_density = 90  # half-circle density, 180 for total 360
        self.radial = np.linspace(0.001, np.pi, self.light_density, endpoint=False)

        # --- light map 2 ---
        self.make_light_map()
    

    # ==== Light Stuff v0.3 =====================================

        
    # def lmap_to_rays(self):
    #     self.rays = []
    #     for i, _ in self.p_lmap:
    #         p_ray = [[], []]
    #         n_ray = [[], []]
    #         for x, y_chunk in enumerate(ray):
    #             chunk = y_chunk[~np.isnan(y_chunk)]
    #             for y in chunk:
    #                 p_ray[0].append(x)
    #                 p_ray[1].append(y)
    #                 n_ray[0].append(x)
    #                 n_ray[1].append(self.n_lmap[i])
    #         self.rays.append(np.array(p_ray))


    #     for ray in self.n_lmap:
    #         pass


    # ==== Light Stuff v0.2 =====================================

    def lights_v02(self):
        drawn = []
        self.update_lmap()
        drawn.append(self.draw_lmap())
        return drawn

    def draw_lmap(self):
        """
        draws the brightness map
        """
        active_map = np.clip(self.active_lmap, 0, 255)
        squares = []
        for x, row in enumerate(active_map):
            for y, brightness in enumerate(row):
                if brightness == 0: continue
                square = self.grid_ref.draw_square(
                    x, y, [[200, 200, 0], brightness])
                squares.append(square)
        return squares

    def update_lmap(self):
        """
        run to update the light map and break off the rays depending on
        current xy
        """

        self.active_lmap = np.zeros(self.grid_ref.dims)
        plmap = self.xy[1] + self.p_lmap
        nlmap = self.xy[1] + self.n_lmap
        xp = self.xy[0] + self.x_range
        xn = self.xy[0] - self.x_range

        brightness = 15
        # brightness = 100

        for ray in plmap:
            for i, y_chunk in enumerate(ray):
                check = False
                for y in y_chunk:
                    if np.isnan(y) or (y > self.grid_ref.dims[1]):
                        break
                    py = int(y)
                    try:
                        check = (self.grid_ref.layers[0, xp[i], py] == 1)
                    except IndexError:
                        break
                    if check:
                        break
                    self.active_lmap[xp[i], py] += brightness
                if check:
                    break
        
        for ray in nlmap:
            for i, y_chunk in enumerate(ray):
                check = False
                for y in y_chunk:
                    if np.isnan(y) or (y > self.grid_ref.dims[1]):
                        break
                    py = int(y)
                    try:
                        check = (self.grid_ref.layers[0, xn[i], py] == 1)
                    except IndexError:
                        break
                    if check:
                        break
                    self.active_lmap[xn[i], py] += brightness
                if check:
                    break


    def make_light_map(self):
        """
        makes the light map for all rays
        """
        dims = self.grid_ref.dims
        self.p_lmap = np.empty((self.light_density, dims[0]+1, dims[1]+1))
        self.p_lmap[:] = np.nan
        for i in range(self.light_density):
            self.get_ray(i)
        self.n_lmap = -self.p_lmap.copy()
        
        # alt version
        self.lmap_to_rays()

    def get_ray(self, radial_idx):
        """
        - gets a "ray" of "y_chunks" from radial index.
        - has to be done with a custom "off-grid" because it's projected
          from the center of the tile.
        """
        ray_angle = self.radial[radial_idx]
        slope = np.cos(ray_angle)/np.sin(ray_angle)

        y_lim = self.grid_ref.dims[1]-0.5
        self.x_range_center = np.concatenate((np.array([0]), self.x_range+0.5))
        y = self.x_range_center*slope
        off_grid = np.linspace(-0.5, y_lim, int(y_lim+0.5)+1)

        # pos slope
        if y[0] <= y[-1]:
            for i in range(len(y)-1):
                cond = (y[i]-1 <= off_grid) & (off_grid <= y[i+1])
                y_range = (off_grid[cond]+0.5).astype(int)
                self.p_lmap[radial_idx][i][0:len(y_range)] = y_range

        # neg slope
        elif y[0] > y[-1]:
            off_grid = -off_grid
            y_lim = - y_lim
            for i in range(len(y)-1):
                cond = (y[i] >= off_grid) & (off_grid >= y[i+1]-1)
                y_range = (off_grid[cond]+0.5).astype(int)
                self.p_lmap[radial_idx][i][0:len(y_range)] = y_range



    # ==== LIGHT STUFF ==========================================
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
    
    # def triangles_origin_to_edges(self, edges):
    #     triangles = []
    #     for edge in edges:
    #         tri = pyglet.shapes.Triangle(
    #             *(self.center+1)*self.grid_ref.cell_size,
    #             *(edge[2:]+1)*self.grid_ref.cell_size,
    #             *(edge[:2]+1)*self.grid_ref.cell_size, 
    #             color=(255, 255, 255), 
    #             batch=self.batch, group=self.group)
    #         tri.opacity = 40
    #         triangles.append(tri)
    #     return triangles