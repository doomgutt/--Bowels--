import numpy as np
import pyglet
from numba import njit, prange
from PIL import Image
from src.game import graphics
from src.game import light
from src.game import creatures

"""
Grid layers:
0, 0       = floor
0, 1       = walls
1, [1 -10] = light
1, [11-20] = smell
1, [21-30] = sound
2, 0       = agents
"""

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
        self.layers = np.zeros((*layer_dims, *self.dims))
        self.get_all_xy()

        # --- populating layers ---
        self.layers[0, 1] = floor_plan

        # === entities ====
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
        vlist = coords_to_v_list(self.anchor, self.all_xy, self.cell_size)
        v_st = "v2i/static"
        tri = pyglet.gl.GL_TRIANGLES

        # floor
        self.l00_vlist = self.batch.add(v_num, tri, self.groups[0], v_st, "c4B/static")
        self.l00_vlist.vertices = vlist
        self.l00_vlist.colors = self.l00_rgbos(self.all_xy, self.layers[0, 0])

        # walls
        self.l01_vlist = self.batch.add(v_num, tri, self.groups[1], v_st, "c4B/static")
        self.l01_vlist.vertices = vlist
        self.l01_vlist.colors = self.l01_rgbos(self.all_xy, self.layers[0, 1])

        # light
        self.l11_vlist = self.batch.add(v_num, tri, self.groups[2], v_st, "c4B/dynamic")
        self.l11_vlist.vertices = vlist

        # sound
        # smell

        # agents
        self.l20_vlist = self.batch.add(v_num, tri, self.groups[3], v_st, "c4B/stream")
        self.l20_vlist.vertices = vlist
    
    # ---- ENTITIES ----------------------------------------------------------
    def init_entities(self):
        # Lights
        # custom
        # l1_xy = (25, 25)
        # l2_xy = (10, 40)
        # l3_xy = (60, 30)
        # random
        l1_xy = (np.random.randint(5, 75), np.random.randint(5, 55))
        l2_xy = (np.random.randint(5, 75), np.random.randint(5, 55))
        l3_xy = (np.random.randint(5, 75), np.random.randint(5, 55))
        self.add_light_source(light.LightSource(l1_xy, self))
        self.layers[0,1,l1_xy[0], l1_xy[1]] = 2
        self.add_light_source(light.LightSource(l2_xy, self))
        self.layers[0,1,l2_xy[0], l2_xy[1]] = 2
        self.add_light_source(light.LightSource(l3_xy, self))
        self.layers[0,1,l3_xy[0], l3_xy[1]] = 2

        # Agents
        self.add_agent(creatures.Toe((30, 30), self, self.groups[2]))
        

    # ==== UPDATES =============================================================
    def update(self, dt):
        self.update_lights()
        self.update_agents()
        self.update_vlist_cols() # this one drops fps to 30 from 60
    
    def update_agents(self):
        self.layers[2, 0] = 0
        for agent in self.agents:
            self.layers[2, 0, agent.xy[0], agent.xy[1]] = agent.id

    # njit this one?
    def update_lights(self):
        object_grid = self.layers[0,1] + self.layers[2,0]
        self.layers[1, 1] = 0
        for l_source in self.light_sources:
            self.layers[1, 1] += l_source.mk_light_grid(object_grid)
        np.clip(self.layers[1, 1], 0, 255).astype(np.int32)

    def update_vlist_cols(self):
        # light
        self.l11_vlist.colors = self.l11_rgbos(self.all_xy, self.layers[1,1])
        # agents
        self.l20_vlist = 0

    # ==== ADDIGNG STUFF =====================================================
    def add_agent(self, agent):
        self.agents.append(agent)

    def add_light_source(self, light_source):
        self.light_sources.append(light_source)    


    # ==== DRAWING COLORS ====================================================
    @staticmethod
    @njit(nogil=True, parallel=True, cache=True)
    def l00_rgbos(all_xy, l00, rand_val=6):
        floor_rgbo = np.array([10, 10, 10, 255],)
        unknown    = np.array([255, 0, 0, 255])

        rgbo_map = np.zeros((len(all_xy), 6, 4))
        for ii in prange(len(all_xy)):
            x, y = all_xy[ii]
            if l00[x,y] == 0:
                col = floor_rgbo.copy()
            else:
                col = unknown
            col = graphics.rand_col(col, 'bw', rand_val)
            rgbo_map[ii] = col

        return rgbo_map.flatten().astype(np.int32)
    
    @staticmethod
    @njit(nogil=True, parallel=True, cache=True)
    def l01_rgbos(all_xy, l01, rand_val=6):
        """
        make color map for layers[0]
        """

        no_wall_rgbo = np.array([0, 0, 0, 0],)
        wall_rgbo  = np.array([30, 30, 30, 255])
        light_block_rgbo = np.array([120, 120, 80, 255])
        unknown_rgbo = np.array([0, 255, 0, 255])

        rgbo_map = np.zeros((len(all_xy), 6, 4))
        for ii in prange(len(all_xy)):
            x, y = all_xy[ii]
            if l01[x,y] == 0:
                col = no_wall_rgbo.copy()
            elif l01[x,y] == 1:
                col = wall_rgbo.copy()
            elif l01[x,y] == 2:
                col = light_block_rgbo.copy()
            else:
                col = unknown_rgbo
            col = graphics.rand_col(col, 'bw', rand_val)
            rgbo_map[ii] = col

        return rgbo_map.flatten().astype(np.int32)
    
    @staticmethod
    @njit(nogil=True, parallel=True, cache=True)
    def l11_rgbos(all_xy, light_grid, rand_val=2):
        light_rgbo = np.array([200, 200, 100, 0])

        rgbo_map = np.zeros((len(all_xy), 6, 4))
        for ii in prange(len(all_xy)):
            x, y = all_xy[ii]
            brightness = light_grid[x, y]
            col = light_rgbo.copy()
            col[3] = brightness
            rgbo_map[ii] = col
        rgbo_map = np.clip(rgbo_map, 0, 255).flatten()
        return rgbo_map.astype(np.int32)

    # ==== GRID ==============================================================
    def get_all_xy(self):
        x = np.arange(self.dims[0])
        y = np.arange(self.dims[1])
        self.all_xy = np.transpose([np.tile(x, len(y)), np.repeat(y, len(x))])

    def import_map_floor(self, filename):
        dir_str = "./assets/maps/floors/"
        filepath = dir_str + filename
        img = Image.open(filepath)
        img_arr = np.delete(np.asarray(img), np.s_[1:], 2)
        img_arr = np.squeeze(img_arr) // 255
        return img_arr.T

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

    def mk_color_map(self):
        env = {
            0 : [[20,  20,  20 ], 255],
            1 : [[100, 100, 100], 255]
        }

        agents = {
            1 : [(255, 0,   0  ), 255],
            2 : [(0,   255, 0  ), 255],
            3 : [(0,   0,   255), 255],
            99 : [(200, 200, 200), 255]
        }

        self.color_map = {
            'env'    : env,
            'agents' : agents
        }

# === Pyglet drawing ======================================
@njit(nogil=True, parallel=True, cache=True)
def coords_to_v_list(anchor, xy_list, cell_size):
    template = np.array([
        [0, 0], [0, 1], [1, 0],
        [0, 1], [1, 0], [1, 1]])
    v_list = np.zeros((len(xy_list), 12))
    for ii in prange(len(xy_list)):
        v_list[ii] = (template + xy_list[ii] + anchor + 1).flatten()
    return (v_list*cell_size).flatten().astype(np.int32)





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