import numpy as np
import pyglet
from src.game import map_utils
from src.game import graphics

"""
Grid layers:
0 = floor and walls
2 = terrain
3 = agents
4 = smell
"""

class Grid:
    def __init__(self, cell_size, window_dims, batch, group, floor_file=None):
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
        self.max_dims = (window_dims[0]//self.cell_size, 
                            window_dims[1]//self.cell_size)
        self.dims = np.array(self.max_dims) - 2

        self.number_of_layers = 4
        self.layers = np.zeros((self.number_of_layers, *self.dims))
        self.agents = []

        # make colors
        self.mk_color_map()

        # Populate grid
        if floor_file:
            print(f"loaded: {floor_file}")
            self.layers[0] = map_utils.import_map_floor(floor_file)
        
        # surfaces
        self.wall_surfaces = self.calculate_surfaces()

    # ==== TESTING ===========================================================


    # ==== UPDATE =============================================================
    def update(self, dt):
        self.agents_to_l1()
    
    # ==== DRAW ==============================================================
    def draw(self):
        # return self.draw_surfaces()
        return None

    # ==== SENSES ============================================================
    # def draw_senses(self, batch):
    #     sense_groups = []
    #     for agent in self.agents:
    #         pass

    # ==== AGENTS ============================================================
    def agents_to_l1(self):
        self.layers[1] = 0
        for agent in self.agents:
            self.layers[1, agent.xy[0], agent.xy[1]] = agent.id

    def add_agent(self, agent):
        self.agents.append(agent)


    # ==== GRID ==============================================================
    def make_floor(self, rand_col=None):
        l = 0 
        self.squares = np.zeros(self.layers.shape, dtype='object')
        for x, row in enumerate(self.layers[l]):
            for y, val in enumerate(row):
                if rand_col:
                    rgbo = graphics.randomize_color(self.color_map['env'][val], rand_col)
                else:
                    rgbo = self.color_map['env'][val]
                self.squares[l, x, y] = self.draw_square(x, y, rgbo)

    # ==== SURFACES ==========================================================
    def draw_surfaces(self):
        beams = []
        for edge in self.wall_surfaces:
            beam = pyglet.shapes.Line(
                *(edge[:2]+1)*self.cell_size,
                *(edge[2:]+1)*self.cell_size,
                width=2, 
                batch=self.batch, group=self.group)
            beam.opacity = 200
            beams.append(beam)
        return beams

    def calculate_surfaces(self):
        wall_coords = np.transpose(np.nonzero(self.layers[0]))
        all_edges = np.concatenate(self.anchors_to_edges(wall_coords))
        surfaces = self.surfaces_from_edges(all_edges)
        return surfaces
    
    def connect_surfaces(self):
        self.surface_list = []
        new_surface = []
        for edge in self.wall_surfaces:
            pass

    def surfaces_from_edges(self, all_edges):
        uniq, counts = np.unique(all_edges, return_counts=True, axis=0)
        repeat_idx = np.nonzero(counts-1)[0]
        external_only = np.delete(uniq, repeat_idx, axis=0)
        return external_only

    def anchors_to_edges(self, anchors):
        """ edges must be done like this to be able to remove duplicates
        [0, 0, 0, 1] ^
        [0, 1, 1, 1] ->
        [1, 0, 1, 1] ^
        [0, 0, 1, 0] ->
        """
        edge_by_anchor = np.zeros((len(anchors), 4, 4))
        for i, a in enumerate(anchors):
            edge_by_anchor[i] = np.array([
                [a[0],   a[1],   a[0],   a[1]+1],
                [a[0],   a[1]+1, a[0]+1, a[1]+1],
                [a[0]+1, a[1],   a[0]+1, a[1]+1],
                [a[0],   a[1],   a[0]+1, a[1]]])
        return edge_by_anchor


    # ==== UTILITY ===========================================================
    def draw_square(self, x, y, rgbo):
        """draws the square of appropriate size, color and offset"""
        square = pyglet.shapes.Rectangle(
            (x+1)*self.cell_size, (y+1)*self.cell_size, 
            self.cell_size, self.cell_size, 
            color=rgbo[0], batch=self.batch, group=self.group)
        square.opacity = rgbo[1]
        return square
    
    def draw_circle(self, x, y, rgbo, batch):
        """draws the square of appropriate size, color and offset"""
        circle = pyglet.shapes.Circle(
            (x+1.5)*self.cell_size, (y+1.5)*self.cell_size, 
            (self.cell_size/2), color=rgbo[0], batch=batch, group=self.group)
        circle.opacity = rgbo[1]
        return circle

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