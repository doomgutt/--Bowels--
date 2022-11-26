import numpy as np
from numba import njit
from PIL import Image
from src.game import grid_rgbo
from src.game import open_gl
from src.game import creatures
from src.game.physics import light
from src.game.physics import sound
import main

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
        0: terrain
        1: walls
        2: characters
        """

        # Init pyglet stuff
        self.batch = batch
        self.groups = groups
        self.clock = clock
        fps = 60
        clock.schedule_interval(self.update, 1/fps)

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
        self.init_sound()

        # Init RGBO maps
        self.make_terrain_rgbo()

    # ==== Initialising Objects ==============================================
    def init_terrain(self):
        self.layers[0][:] = 1
        self.layers[1] = self.imported_image*100

    def init_agents(self):
        self.agents = []
        self.add_agent(creatures.Eye((30, 30), self))
        self.add_agent(creatures.Ear((40, 40), self))

    def init_light(self):
        self.light_tracker = light.LightTracker(self)
        xy_list = [(25, 25), (10, 40), (60, 30)]
        for xy in xy_list:
            # self.add_light_source(self.rnd_non_wall_space(self.layers[1]))
            self.light_tracker.add_light_source(xy, self)

    def init_sound(self):
        self.sound = sound.SoundTracker(self)

    # ==== Updates ===========================================================
    def update(self, dt):
        self.object_grid = self.mk_object_grid(self.layers, (1, 2))
        self.light_tracker.update(self)
        self.sound.update(dt, self)
        self.update_agents(dt)
        self.draw_map()

    def update_agents(self, dt):
        self.layers[2] = 0
        for agent in self.agents:
            self.layers[2, agent.xy[0], agent.xy[1]] = agent.id
            agent.glayers = self.layers
            agent.update(dt, self)

    # ==== Adding Stuff =====================================================
    def add_agent(self, agent):
        self.agents.append(agent)

    def add_light_source(self, xy):
        self.light_sources.append(light.LightSource(xy, self))
        self.layers[1, xy[0], xy[1]] = 101

    # ==== Utility ===========================================================
    @staticmethod
    @njit(nogil=NOGIL_TOGGLE, cache=True)
    def mk_object_grid(layers, layer_idxs):
        object_grid = np.zeros_like(layers[0])
        for idx in layer_idxs:
            for x, row in enumerate(layers[idx]):
                for y, entry in enumerate(row):
                    if entry != 0:
                        object_grid[x, y] = entry
        return object_grid
    
    @staticmethod
    @njit(nogil=NOGIL_TOGGLE, cache=True)
    def rnd_non_wall_space(wall_grid):
        shift = 3
        wall_check = True
        while wall_check:
            x = np.random.randint(shift, len(wall_grid)    - shift)
            y = np.random.randint(shift, len(wall_grid[1]) - shift)
            wall_check = (wall_grid[x, y] < 100)
        return (x, y)

    # ==== Drawing ===========================================================
    def draw_map(self):
        # get agents
        l2_rgbo = grid_rgbo.idx_to_rgbo(
            self.all_xy, 2, self.layers, self.rgbo_ref)
        
        # mix with terrain
        rgbo_lists = np.array([self.terrain_rgbo_l, l2_rgbo])
        mixed = grid_rgbo.mix_rgbo_lists(rgbo_lists)

        # adjust brightness
        grid_rgbo.set_list_brightness(
            self.all_xy, mixed, self.light_tracker.light_grid)
        
        # send to Vertex List
        self.clist = grid_rgbo.rgbo_list_to_clist(mixed)
        self.g_vlist.colors = self.clist


    # ==== SETUP =============================================================
    def import_map_image(self, filename):
        dir_str = "./assets/maps/floors/"
        filepath = dir_str + filename
        img = Image.open(filepath)
        img_arr = np.delete(np.asarray(img), np.s_[1:], 2)
        img_arr = np.squeeze(img_arr) // 255
        print(f"Imported: {filename}")
        return img_arr.T.astype(np.int64)

    def init_grid(self, floor_file=None, layer_dims=3):
        assert floor_file is not None, "Import a map image"
        self.imported_image = self.import_map_image(floor_file)
        self.dims = self.imported_image.shape
        self.layers = np.zeros((layer_dims, *self.dims), dtype='i2')
        self.all_xy = grid_rgbo.get_xy_list(self.dims[0], self.dims[1])

    def make_terrain_rgbo(self):
        self.terrain_rgbo_l = grid_rgbo.make_terrain_rgbo(
            self.all_xy, (0, 1), self.layers, self.rgbo_ref)
        self.clist = grid_rgbo.rgbo_list_to_clist(self.terrain_rgbo_l)

if __name__ == '__main__':
    main.run_game()

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
