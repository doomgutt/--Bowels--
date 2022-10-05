import numpy as np
import pyglet
from src.game import map_utils

"""
Grid layers:
0 = floor and walls
2 = terrain
3 = agents
4 = smell
"""

class Grid:
    def __init__(self, cell_size, window_dims, floor_file=None):
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
        
        self.cell_size = cell_size
        self.max_dims = (window_dims[0]//self.cell_size, 
                            window_dims[1]//self.cell_size)
        self.dims = np.array(self.max_dims) - 2

        self.layers = 4
        self.grid = np.zeros((self.layers, *self.dims))

        # make colors
        self.mk_color_map()

        # Populate grid
        if floor_file:
            print(f"loaded: {floor_file}")
            self.grid[0] = map_utils.import_map_floor(floor_file)

    # ==== TESTING ==========================================================
    def running_square(self, counter, batch):
        y = counter // self.dims[0] % self.dims[1]
        x = counter % self.dims[0]
        # print(x,y)
        self.grid[1] = 0
        self.grid[1, x, y] = 1
        rgbo = [(255, 255, 255), 255]
        square = self.draw_square(1, x, y, rgbo, batch)
        return square

    # ==== UDATE ============================================================
    def update(self):
        pass

    # ==== DRAWING STUFF ====================================================
    def init_grid(self, batch, rand_col=None):
        # Setting up...
        self.squares = np.zeros(self.grid.shape, dtype='object')
        
        # Making Floor
        l = 0 
        for x, row in enumerate(self.grid[l]):
            for y, val in enumerate(row):
                if rand_col:
                    rgbo = randomize_color(self.color_map['env'][val], rand_col)
                else:
                    rgbo = self.color_map['env'][val]
                self.squares[l, x, y] = self.draw_square(l, x, y, rgbo, batch)

        # Making Agents
        # l = 1
        # for l, layer in enumerate(self.grid):
        # for x, row in enumerate(layer):
        #     for y, _ in enumerate(row):
        #         self.squares[l, x, y] = self.draw_square(l, x, y, batch)
    
    def draw_square(self, l, x, y, rgbo, batch):
        """
        draws the square of appropriate size, color and offset
        """
        if l != 0 and self.grid[l, x, y] == 0:
            return

        # make square
        square = pyglet.shapes.Rectangle(
            (x+1)*self.cell_size, (y+1)*self.cell_size, 
            self.cell_size, self.cell_size, 
            color=rgbo[0], batch=batch)
        square.opacity = rgbo[1]

        return square

    def mk_color_map(self):
        env_rgbo = {
            0 : [[20,  20,  20 ], 255],
            1 : [[100, 100, 100], 255]
        }

        char_rgbo = {
            1 : [(200, 200, 200), 255],
            2 : [(255, 0,   0  ), 255],
            3 : [(0,   255, 0  ), 255],
            4 : [(0,   0,   255), 255]
        }

        self.color_map = {
            'env'    : env_rgbo,
            'agents' : char_rgbo
        }


### %%%% UTILS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def randomize_color(rgbo, type, amount=10):
    if type == 'col':
        rgb = np.array(rgbo[0]) + np.random.randint(-amount, amount, 3)
    elif type == 'bw':
        rgb = np.array(rgbo[0]) + np.random.randint(-amount, amount)
    return [rgb, rgbo[1]]