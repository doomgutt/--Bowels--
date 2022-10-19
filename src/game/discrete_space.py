import numpy as np
import pyglet
from numba import njit, prange
from PIL import Image
from src.game import graphics

"""
Grid layers:
0 = floor and walls
1 = agents
2 = terrain
4 = smell
"""

class Grid:
    def __init__(self, cell_size, dims, batch, group, floor_file=None):
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
        self.group = group
        
        self.cell_size = cell_size
        self.dims = np.array(dims)//self.cell_size - 2
        self.get_all_xy()

        self.number_of_layers = 4
        self.layers = np.zeros((self.number_of_layers, *self.dims))
        self.agents = []

        # make colors
        self.mk_color_map()

        # Populate grid
        if floor_file:
            print(f"loaded: {floor_file}")
            self.layers[0] = self.import_map_floor(floor_file)

        # --- vertex list stuff ---
        self.mk_vlist()
        # make vertex lists for different things
        # instead of deleting and re-drawing stuff, you can edit
        # vertex positions and colours in a vertex list.
        # VERY sexy.

    # ==== TESTING ===========================================================

    # ==== UPDATE =============================================================
    def update(self, dt):
        self.agents_to_l1()
    
    # ==== DRAW ==============================================================
    def draw(self):
        pass

    def draw_square(self, x, y, rgbo):
        """draws the square of appropriate size, color and offset"""
        square = pyglet.shapes.Rectangle(
            (x+1)*self.cell_size, (y+1)*self.cell_size,
            self.cell_size, self.cell_size,
            color=rgbo[0], batch=self.batch, group=self.group)
        square.opacity = rgbo[1]
        return square
    
    def mk_vlist(self):
        """
        make vertex list
        """
        v_num = np.prod(self.dims)*6
        self.vlist = self.batch.add(
            v_num, pyglet.gl.GL_TRIANGLES, 
            self.group, "v2i/static", "c4B/static"
        )

        # vertices
        l0_vlist = coords_to_v_list(self.all_xy, self.cell_size)
        self.vlist.vertices[:len(l0_vlist)] = l0_vlist

        # colors
        cols = self.get_l0_rgbo_list(self.all_xy, self.layers[0])
        self.vlist.colors = cols

    @staticmethod
    @njit(nogil=True, parallel=True, cache=True)
    def get_l0_rgbo_list(all_xy, l0, rand_val=10):
        """
        make color map for layers[0]
        """

        floor_rgbo = np.array([20,  20,  20 , 255],)
        wall_rgbo  = np.array([100, 100, 100, 255])
        unknown    = np.array([200, 11,  11 , 255])

        rgbo_map = np.zeros((len(all_xy), 6, len(floor_rgbo)))
        for ii in prange(len(all_xy)):
            x, y = all_xy[ii]
            if l0[x,y] == 0:
                col = floor_rgbo.copy()
            elif l0[x,y] == 1:
                col = wall_rgbo.copy()
            else:
                col = unknown
            col = graphics.rand_col(col, 'bw', rand_val)
            rgbo_map[ii] = col

        return rgbo_map.flatten().astype(np.int32)

    # ==== AGENTS ============================================================
    def agents_to_l1(self):
        self.layers[1] = 0
        for agent in self.agents:
            self.layers[1, agent.xy[0], agent.xy[1]] = agent.id

    def add_agent(self, agent):
        self.agents.append(agent)


    # ==== GRID ==============================================================
    def get_all_xy(self):
        x = np.arange(self.dims[0])
        y = np.arange(self.dims[1])
        self.all_xy = np.transpose([np.tile(x, len(y)), np.repeat(y, len(x))])


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

    def import_map_floor(self, filename):
        dir_str = "./assets/maps/floors/"
        filepath = dir_str + filename
        img = Image.open(filepath)
        img_arr = np.delete(np.asarray(img), np.s_[1:], 2)
        img_arr = np.squeeze(img_arr) // 255
        return img_arr.T

    # ==== UTILITY ===========================================================
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
def coords_to_v_list(xy_list, cell_size):
    template = np.array([
        [0, 0], [0, 1], [1, 0],
        [0, 1], [1, 0], [1, 1]])
    v_list = np.zeros((len(xy_list), 12))
    for ii in prange(len(xy_list)):
        v_list[ii] = (template + xy_list[ii] + 1).flatten()
    return (v_list*cell_size).flatten().astype(np.int32)





    
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