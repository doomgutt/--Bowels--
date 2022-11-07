import numpy as np
import pyglet
from numba import njit
from PIL import Image
from src.game import senses
from src.game import light
from src.game import creatures
from src.game import open_gl
from src.game import grid_rgbo

"""
Grid layers:
0, 0       = technical stuff
0, 1       = floor
0, 2       = walls
1, [1 -10] = light
1, [11-20] = smell
1, [21-30] = sound
2, 0       = agents
"""

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================


# === GRID STUFF =============
class Grid:
    def __init__(self, cell_size, clock, batch, groups, floor_file=None):
        """
        Dimensions
        ----------
        max_dims: maximum fitting grid space
        dims:     without outer rows

        Layers
        ------
        layer 1: world
        layer 2: characters

        Variables:
        ----------
        self.cell_size
        self.anchor
        self.dims
        self.layers
        self.all_xy

        self.agents
        self.light_sources
        self.sight_grids
        self.g_vlist
        """
        # Init pyglet stuff
        self.batch = batch
        self.groups = groups
        self.clock = clock
        clock.schedule_interval(self.update, 1/30.0)

        # Init grid
        self.cell_size = cell_size
        self.anchor = np.array((0, 30))
        self.rgbo_ref = grid_rgbo.mk_rgbo_ref()
        self.init_grid(floor_file)

        # Init vertex list
        self.g_vlist = open_gl.mk_vlist(
            self.anchor, cell_size, self.all_xy, batch, groups[0])

        # Init Entities
        self.init_terrain()
        self.init_agents()
        self.init_light()

        # Init RGBO maps
        self.mk_terrain_rgbo()

    # ==== Initialising Objects ==============================================
    def init_terrain(self):
        self.layers[0, 2] = self.imported_image

    def init_agents(self):
        self.agents = []
        self.add_agent(creatures.Toe((30, 30), self, self.groups[2]))

    def init_light(self):
        self.light_sources = []
        self.sight_grids = []

        # xy_list = [(25, 25), (10, 40), (60, 30)]
        for _ in range(1):
            # self.add_light_source(self.rnd_non_wall_space(self.layers[0, 2]))
            self.add_light_source((25, 25))

    # ==== Updates ===========================================================
    def update(self, dt):
        self.update_lights()
        self.update_agents(dt)
        self.draw_map()

    def update_agents(self, dt):
        self.layers[2, 0] = 0
        for agent in self.agents:
            self.layers[2, 0, agent.xy[0], agent.xy[1]] = agent.id
            agent.glayers = self.layers
            agent.update(dt)

    def update_lights(self):
        object_grid = self.layers[0, 2] + self.layers[2, 0]
        self.layers[1, 1] = 0
        for l_source in self.light_sources:
            self.layers[1, 1] += l_source.mk_light_grid(object_grid)
            # workign w rays
            self.rayz = l_source.RAYZ(object_grid, self.anchor,
                                      self.batch, self.groups[2])
        self.layers[1, 1] = np.clip(self.layers[1, 1], 0, 255)

    # ==== Drawing ===========================================================
    def draw_map(self):
        # customise to parts of the grid
        id_list = ((2, 0), (1, 1))
        settings = (self.layers, self.rgbo_ref, id_list, (), self.terrain_rgbo)
        rgbog = grid_rgbo.rgbog_mkr(*settings)
        rgbog = grid_rgbo.set_brightness(rgbog, self.layers[1, 1], 0.009, 0.1)
        self.light_rgbog = rgbog
        self.g_vlist.colors = open_gl.grid_to_clist(self.all_xy, rgbog)

    # ==== Adding Stuff =====================================================
    def add_agent(self, agent):
        self.agents.append(agent)

    def add_light_source(self, xy, density=360):
        self.light_sources.append(light.LightSource(xy, self, density))
        self.layers[0, 2, xy[0], xy[1]] = 2

    def add_sight_grid(self):
        self.sight_grids.append(senses.Sight_Grid(self))

    # --- utility ---
    @staticmethod
    @njit(nogil=NOGIL_TOGGLE, cache=True)
    def rnd_non_wall_space(wall_grid):
        shift = 3
        wall_check = True
        while wall_check:
            x = np.random.randint(shift, len(wall_grid)    - shift)
            y = np.random.randint(shift, len(wall_grid[1]) - shift)
            wall_check = (wall_grid[x, y] != 0)
        return (x, y)

    # ==== SETUP =============================================================
    # --- Making the grid ---
    def import_map_image(self, filename):
        dir_str = "./assets/maps/floors/"
        filepath = dir_str + filename
        img = Image.open(filepath)
        img_arr = np.delete(np.asarray(img), np.s_[1:], 2)
        img_arr = np.squeeze(img_arr) // 255
        print(f"Imported: {filename}")
        return img_arr.T.astype(np.int64)

    def init_grid(self, floor_file=None, layer_dims=(3, 4)):
        assert floor_file is not None, "Import a map image"
        self.imported_image = self.import_map_image(floor_file)
        self.dims = self.imported_image.shape
        self.layers = np.zeros((*layer_dims, *self.dims), dtype='i8')
        self.all_xy = grid_rgbo.get_xy_list(self.dims[0], self.dims[1])

    # ---- Vertex Lists ----
    def mk_vlist(self, anchor, xy_list, group, cell_size,
                 v_mode="v2i/static", c_mode="c4f/stream"):
        vlist = self.batch.add(
            len(xy_list)*6, pyglet.gl.GL_TRIANGLES, group, v_mode, c_mode)
        vlist_vertices = open_gl.coords_to_v_list(
            anchor, xy_list, cell_size)
        vlist.vertices = vlist_vertices
        return vlist

    # ---- RGBO ----
    def mk_terrain_rgbo(self):
        id_list = ((0, 1), (0, 2))
        rnd_idx = (0, 1)
        settings = (self.layers, self.rgbo_ref, id_list, rnd_idx)
        self.terrain_rgbo = grid_rgbo.rgbog_mkr(*settings)

# % % UTILS % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % %

# #### OLD CODE ##############################################################
# === Pyglet drawing ======================================
    # def draw_square(self, xy, rgbo, group):
    #     sprite = pyglet.shapes.Rectangle(
    #         (xy[0] + 1 + self.anchor[0]) * self.cell_size,
    #         (xy[1] + 1 + self.anchor[1]) * self.cell_size,
    #         self.cell_size,
    #         self.cell_size,
    #         color=rgbo[:3], batch=self.batch, group=group)
    #     sprite.opacity = rgbo[-1]
    #     return sprite

    # def make_floor(self, rand_col=None):
    #     l = 0
    #     self.squares = np.zeros(self.layers.shape, dtype='object')
    #     for x, row in enumerate(self.layers[l]):
    #         for y, val in enumerate(row):
    #             if rand_col:
    #                 rgbo = graphics.randomize_color(
    #                           self.color_map['env'][val], rand_col)
    #             else:
    #                 rgbo = self.color_map['env'][val]
    #             self.squares[l, x, y] = self.draw_square(x, y, rgbo)

    # def draw_circle(self, x, y, rgbo, batch):
    #     """draws the square of appropriate size, color and offset"""
    #     circle = pyglet.shapes.Circle(
    #         (x+1.5)*self.cell_size, (y+1.5)*self.cell_size,
    #         (self.cell_size/2), color=rgbo[0], batch=batch, group=self.group)
    #     circle.opacity = rgbo[1]
    #     return circle

    # ==== SURFACES ==========================================================
    # def draw_surfaces(self):
    #     beams = []
    #     for edge in self.wall_surfaces:
    #         beam = pyglet.shapes.Line(
    #             *(edge[:2]+1)*self.cell_size,
    #             *(edge[2:]+1)*self.cell_size,
    #             width=2,
    #             batch=self.batch, group=self.group)
    #         beam.opacity = 200
    #         beams.append(beam)
    #     return beams

    # def calculate_surfaces(self):
    #     wall_coords = np.transpose(np.nonzero(self.layers[0]))
    #     all_edges = np.concatenate(self.anchors_to_edges(wall_coords))
    #     surfaces = self.surfaces_from_edges(all_edges)
    #     return surfaces

    # def connect_surfaces(self):
    #     self.surface_list = []
    #     new_surface = []
    #     for edge in self.wall_surfaces:
    #         pass

    # def surfaces_from_edges(self, all_edges):
    #     uniq, counts = np.unique(all_edges, return_counts=True, axis=0)
    #     repeat_idx = np.nonzero(counts-1)[0]
    #     external_only = np.delete(uniq, repeat_idx, axis=0)
    #     return external_only

    # def anchors_to_edges(self, anchors):
    #     """ edges must be done like this to be able to remove duplicates
    #     [0, 0, 0, 1] ^
    #     [0, 1, 1, 1] ->
    #     [1, 0, 1, 1] ^
    #     [0, 0, 1, 0] ->
    #     """
    #     edge_by_anchor = np.zeros((len(anchors), 4, 4))
    #     for i, a in enumerate(anchors):
    #         edge_by_anchor[i] = np.array([
    #             [a[0],   a[1],   a[0],   a[1]+1],
    #             [a[0],   a[1]+1, a[0]+1, a[1]+1],
    #             [a[0]+1, a[1],   a[0]+1, a[1]+1],
    #             [a[0],   a[1],   a[0]+1, a[1]]])
    #     return edge_by_anchor
# ==== AGENTS ============================================================
    # def update_agents(self, dt):
    #     for agent in self.agents:
    #         agent.update(dt, self)
    #         self.layers[1, agent.xy[0], agent.xy[1]] = agent.id

    # def draw_agents(self):
    #     """drawing agents"""
    #     agent_draws = []
    #     for agent in self.agents:
    #         # a_draw = self.draw_circle(*agent.xy, agent.rgbo)
    #         a_draw = self.draw_square(*agent.xy, agent.rgbo)
    #         agent_draws.append(a_draw)
    #     return agent_draws

    # def running_square(self, counter):
    #     y = counter // self.dims[0] % self.dims[1]
    #     x = counter % self.dims[0]
    #     return (x, y), 1
