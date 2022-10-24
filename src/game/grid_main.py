import numpy as np
import pyglet
from numba import njit, prange
from PIL import Image
from src.game import graphics
from src.game import light
from src.game import creatures
from src.game import open_gl_tools
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
        """
        # === Pyglet ===
        self.batch = batch
        self.groups = groups
        self.clock = clock
        clock.schedule_interval(self.update, 1/120.0)
        
        # === making map ===
        self.cell_size = cell_size
        self.anchor = np.array([0, 30])

        # --- loading map ---
        if floor_file == None:
            print("select a level to load")
            self.dims = np.array((20, 20))
        else:
            print(f"loaded: {floor_file}")
            floor_plan = self.import_map_floor(floor_file)
            self.dims = floor_plan.shape

        layer_dims = (3, 4)
        self.layers = np.zeros((*layer_dims, *self.dims), dtype='i8')
        self.get_all_xy()

        # --- populating layers ---
        self.layers[0,2] = floor_plan

        # === RGBO stuff ===
        self.rgbo_ref = grid_rgbo.mk_rgbo_ref()
        self.rgbo_grid = np.zeros((*self.layers.shape, 4), dtype=np.int64)

        # === entities ===
        self.agents = []
        self.light_sources = []
        self.init_entities()

        # === vertex list stuff ===
        self.make_vertex_lists()

    # ==== SETUP =============================================================
    # ---- VERTEX LISTS ------------------------------------------------------
    def make_vertex_lists(self):
        # setup
        v_num = np.prod(self.dims)*6
        vlist = open_gl_tools.coords_to_v_list(self.anchor, self.all_xy, self.cell_size)
        v_st = "v2i/static"
        tri = pyglet.gl.GL_TRIANGLES

        # terrain
        self.v_list = self.batch.add(v_num, tri, self.groups[0], v_st, "c4f/stream")
        self.v_list.vertices = vlist

        r_val = 3
        rgbo_l01 = grid_rgbo.layer_to_rgbo(self.layers, 0, 1, self.rgbo_ref)
        rgbo_l01[:,:,:3] += np.random.randint(-r_val, r_val, (80, 60, 1))/100
        rgbo_l02 = grid_rgbo.layer_to_rgbo(self.layers, 0, 2, self.rgbo_ref)
        rgbo_l02[:,:,:3] += np.random.randint(-r_val, r_val, (80, 60, 1))/100
        self.terrain_rgbo = grid_rgbo.mix_2_rgbo_grids(rgbo_l01, rgbo_l02)

    
    # ---- ENTITIES ----------------------------------------------------------
    def init_entities(self):
        # Lights
        # l1_xy = (25, 25)
        l1_xy = self.rnd_non_wall_space(self.layers[0,2])
        self.add_light_source(light.LightSource(l1_xy, self))
        self.layers[0,2,l1_xy[0], l1_xy[1]] = 2

        # l2_xy = (10, 40)
        l2_xy = self.rnd_non_wall_space(self.layers[0,2])
        self.add_light_source(light.LightSource(l2_xy, self))
        self.layers[0,2,l2_xy[0], l2_xy[1]] = 2

        # l3_xy = (60, 30)
        l3_xy = self.rnd_non_wall_space(self.layers[0,2])
        self.add_light_source(light.LightSource(l3_xy, self))
        self.layers[0,2,l3_xy[0], l3_xy[1]] = 2

        # Agents
        self.add_agent(creatures.Toe((30, 30), self, self.groups[2]))
        

    # ==== UPDATES =============================================================
    def update(self, dt):

        self.update_agents()
        self.update_lights()
        
        self.draw_map(4, 0.3)

        
    
    def draw_map(self, br_mult, br_min):
        rgbo_l20 = grid_rgbo.layer_to_rgbo(self.layers, 2, 0, self.rgbo_ref)
        rgbo_l11 = grid_rgbo.layer_to_rgbo(self.layers, 1, 1, self.rgbo_ref)
        rgbog = grid_rgbo.mix_2_rgbo_grids(self.terrain_rgbo, rgbo_l20)
        rgbog = grid_rgbo.mix_2_rgbo_grids(rgbog, rgbo_l11)
        rgbog[:,:,-1] = np.clip(br_mult*self.layers[1,1]/255, br_min, 1)
        self.v_list.colors = open_gl_tools.grid_to_clist(self.all_xy, rgbog)

    
    def update_agents(self):
        self.layers[2, 0] = 0
        for agent in self.agents:
            self.layers[2, 0, agent.xy[0], agent.xy[1]] = agent.id

    # njit this one?
    def update_lights(self):
        object_grid = self.layers[0,2] + self.layers[2,0]
        self.layers[1, 1] = 0
        for l_source in self.light_sources:
            self.layers[1, 1] += l_source.mk_light_grid(object_grid)
        self.layers[1, 1] = np.clip(self.layers[1, 1], 0, 255)

    def update_vlist_cols(self):
        # light
        self.l11_vlist.colors = self.l11_rgbos(self.all_xy, self.layers[1,1], self.rgbo_ref).flatten()
        # agents
        self.l20_vlist = 0

    # ==== ADDIGNG STUFF =====================================================
    def add_agent(self, agent):
        self.agents.append(agent)

    def add_light_source(self, light_source):
        self.light_sources.append(light_source)    

    # ==== RGBO GRID =========================================================
    def layers_to_rgbo(self):
        pass

    # ==== GRID ==============================================================
    def get_all_xy(self):
        x = np.arange(self.dims[0], dtype='i8')
        y = np.arange(self.dims[1], dtype='i8')
        self.all_xy = np.transpose([np.tile(x, len(y)), np.repeat(y, len(x))])

    def import_map_floor(self, filename):
        dir_str = "./assets/maps/floors/"
        filepath = dir_str + filename
        img = Image.open(filepath)
        img_arr = np.delete(np.asarray(img), np.s_[1:], 2)
        img_arr = np.squeeze(img_arr) // 255
        return img_arr.T.astype(np.int64)

    # ==== UTILITY ===========================================================

    def draw_square(self, xy, rgbo, group):
        sprite = pyglet.shapes.Rectangle(
            (xy[0] + 1 + self.anchor[0]) * self.cell_size,
            (xy[1] + 1 + self.anchor[1]) * self.cell_size, 
            self.cell_size,
            self.cell_size, 
            color=rgbo[:3], batch=self.batch, group=group)
        sprite.opacity = rgbo[-1]
        return sprite

    @staticmethod
    @njit(nogil=NOGIL_TOGGLE, cache=True)
    def rnd_non_wall_space(wall_grid):
        max_x = len(wall_grid)-3
        max_y = len(wall_grid[1])-3
        wall_check = True
        while wall_check:
            x = np.random.randint(3, max_x)
            y = np.random.randint(3, max_y)
            wall_check = (wall_grid[x, y] != 0)
        return (x, y)



# === Pyglet drawing ======================================






    # def make_floor(self, rand_col=None):
    #     l = 0 
    #     self.squares = np.zeros(self.layers.shape, dtype='object')
    #     for x, row in enumerate(self.layers[l]):
    #         for y, val in enumerate(row):
    #             if rand_col:
    #                 rgbo = graphics.randomize_color(self.color_map['env'][val], rand_col)
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


### %%%% UTILS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%





##############################################################################
#### OLD CODE ################################################################
##############################################################################


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