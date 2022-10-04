import numpy as np
import pyglet

class Grid:
    def __init__(self, cell_size, window_dims):
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
        
        self.max_dims = (window_dims[0]//cell_size, window_dims[1]//cell_size)
        self.dims = np.array(self.max_dims) - 2
        # [self.max_dims[0]-2, self.max_dims[1]-2]

        self.sq_size = 10
        self.layers = 2
        self.grid = np.zeros((self.layers, *self.dims))

        # self.batch = batch
        self.mk_colour_map()

    def test_grid(self):
        grid = np.zeros(self.dims, dtype='object')

        col_gap = 10
        for x in range(grid.shape[0]):
            col_gap *= -1
            for y in range(grid.shape[1]):
                col_gap *= -1
                col = 110 + col_gap
                grid[x, y] = pyglet.shapes.Rectangle(x*10, y*10, 10, 10, color=(col, col, col), batch=batch)
        
        return grid

    def update(self, input=None):
        # WIL NEED CUSTOM UPDATES DEPENDING ON WHAT WE'RE UPDATING

        """ Make the grid as a numpy array """
        self.grid = np.zeros((self.layers, *self.dims))

### ==== DRAWING STUFF ===============================

    def draw_to(self, batch, rand=None):
        self.squares = np.zeros(self.grid.shape, dtype='object')
        for l, layer in enumerate(self.grid):
            for x, row in enumerate(layer):
                for y, entry in enumerate(row):
                    self.squares[l, x, y] = self.draw_square(l, x, y, batch, rand=rand)
    
    def draw_square(self, l, x, y, batch, rgbo=None, rand=None):
        """
        draws the square of appropriate size, colour and offset
        """
        
        # setting colour
        if rgbo:
            col = rgbo[:3]
            opacity = rgbo[3]
        else:
            col = self.colour_map[l][self.grid[l, x, y]][:3]
            opacity = self.colour_map[l][self.grid[l, x, y]][3]

        # adding aesthetic noise
        rand_val = 10
        if rand == 'col':
            col = np.array(col) + np.random.randint(-rand_val, rand_val, 3)
        elif rand == 'bw':
            col = np.array(col) + np.random.randint(-rand_val, rand_val)

        # make square
        square = pyglet.shapes.Rectangle(
            (x+1)*self.sq_size, (y+1)*self.sq_size, 
            self.sq_size, self.sq_size, 
            color=col, batch=batch)
        square.opacity = opacity
        
        return square

    def mk_colour_map(self):
        env_colour = {
            0 : (200, 200, 200, 255),
            1 : (10, 10, 10, 255),
            2 : (255, 0, 0, 255),
            3 : (0, 255, 0, 255),
            4 : (0, 0, 255, 255)
        }

        char_colour = {
            0 : (10, 10, 255, 100),
            1 : (200, 200, 200, 255),
            2 : (255, 0, 0, 255),
            3 : (0, 255, 0, 255),
            4: (0, 0, 255, 255)
        }

        self.colour_map = [env_colour, char_colour]
