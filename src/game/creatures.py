import numpy as np
from pyglet.window import key

class Agent:
    def __init__(self, grid, controls=None):
        self.grid_ref = grid
        self.x = 10
        self.y = 10
        self.id = 99
        self.speed = 1
        self.controls = controls
        self.rgbo = [[255, 255, 255], 255]
        self.dt_counter = 0
        self.key_handler = key.KeyStateHandler()
        self.controls = {
            "up"   : key.UP, 
            "down" : key.DOWN, 
            "left" : key.LEFT, 
            "right": key.RIGHT
        }

    def update(self, dt, grid):
        # get latest grid info
        self.grid_ref = grid
        # move
        self.move(grid, dt)
            
    def move(self, grid, dt):
        if self.key_handler[self.controls["up"]]:  # up
            new_y = self.y + self.speed
            if not self.wall_check(self.x, new_y):
                self.y = new_y
        elif self.key_handler[self.controls["down"]]:  # down
            new_y = self.y - self.speed
            if not self.wall_check(self.x, new_y):
                self.y = new_y

        if self.key_handler[self.controls["left"]]:  # left
            new_x = self.x - self.speed
            if not self.wall_check(new_x, self.y):
                self.x = new_x
        elif self.key_handler[self.controls["right"]]:  # right
            new_x = self.x + self.speed
            if not self.wall_check(new_x, self.y):
                self.x = new_x

    def wall_check(self, x, y):
        if self.grid_ref[0, x, y] == 0:
            return False
        elif self.grid_ref[0, x, y] == 1:
            return True

class Toe(Agent):
    def __init__(self, pos, grid):
        super().__init__(grid)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[255, 255, 0], 255]

class Ear(Agent):
    def __init__(self, pos, grid):
        super().__init__(grid)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[255, 0, 0], 255]

class Nose(Agent):
    def __init__(self, pos, grid):
        super().__init__(grid)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[0, 255, 0], 255]

class Running_Square(Agent):
    def __init__(self, grid):
        super().__init__(grid)
        self.rgbo = [[255, 0, 0], 255]
        self.counter = 0
        self.controls = {
            "up"   : key.W, 
            "down" : key.S, 
            "left" : key.A, 
            "right": key.D
        }

    def update(self, dt, grid):
        super().update(dt, grid)
        # self.x = self.counter % grid.shape[-2]
        # self.y = self.counter // grid.shape[-2] % grid.shape[-1]
        # self.counter += 1