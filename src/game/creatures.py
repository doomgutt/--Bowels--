import numpy as np
from pyglet.window import key

class Agent:
    def __init__(self, grid, controls=None):
        self.grid_ref = grid
        self.x = 10
        self.y = 10
        self.speed = 1
        self.controls = controls
        self.rgbo = [[255, 255, 255], 255]
        self.key_handler = key.KeyStateHandler()

    def randomize_colour(self):
        pass

    def update(self, dt, grid):
        # super(Player, self).update(dt)
        self.grid_ref = grid
            
        if self.key_handler[key.W]:  # up
            self.y += self.speed
        elif self.key_handler[key.S]:  # down
            self.y -= self.speed

        if self.key_handler[key.A]:  # left
            self.x -= self.speed
        elif self.key_handler[key.D]:  # right
            self.x += self.speed

    def data(self):
        return (self.x, self.y), 99

class Toe(Agent):
    def __init__(self, pos, grid, controls):
        super().__init__(grid, controls)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[255, 255, 0], 255]

class Ear(Agent):
    def __init__(self, pos, grid, controls):
        super().__init__(grid, controls)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[255, 0, 0], 255]

class Nose(Agent):
    def __init__(self, pos, grid, controls):
        super().__init__(grid, controls)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[0, 255, 0], 255]




controls = {
    "left"   :"",
    "right"  :"",
    "up"     :"",
    "down"   :"",
    "action" :""
}


class Running_Square(Agent):
    def __init__(self, grid):
        super().__init__(grid)
        self.counter = 0

    def update(self, dt, grid):
        super().update(dt, grid)
        self.x = self.counter % grid.shape[-2]
        self.y = self.counter // grid.shape[-2] % grid.shape[-1]
        self.counter += 1