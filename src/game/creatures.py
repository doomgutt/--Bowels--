import numpy as np
from src.utility import utils
from pyglet.window import key

class Creature:
    def __init__(self, grid):
        self.grid_ref = grid

        # movement
        self.xy = [10, 10]
        self.dt_xy = [0, 0]
        self.dt_xy_sum = [0, 0]
        self.speed = 30

        # stats
        self.id = 99
        self.rgbo = [[255, 255, 255], 255]

        # controls
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
        self.update_dt(dt)
        self.move()

    def update_dt(self, dt):
        if self.key_handler[self.controls["up"]]:  # up
            self.dt_xy[1] = dt * self.speed
        elif self.key_handler[self.controls["down"]]:  # down
            self.dt_xy[1] = -dt * self.speed
        else:
            self.dt_xy[1] = 0

        if self.key_handler[self.controls["left"]]:  # left
            self.dt_xy[0] = -dt * self.speed
        elif self.key_handler[self.controls["right"]]:  # right
            self.dt_xy[0] = dt * self.speed
        else:
            self.dt_xy[0] = 0
    
    def move(self):
        for n, val in enumerate(self.dt_xy):

            # check for opposite motion
            if not utils.same_sign(val, self.dt_xy_sum[n]):
                self.dt_xy_sum[n] = 0

            # add dt
            self.dt_xy_sum[n] += val

            # check threshold and wall, then move
            sum_abs = abs(self.dt_xy_sum[n])
            if sum_abs >= 1:
                move_val = round(self.dt_xy_sum[n]/sum_abs)
                # if not self.wall_check(move_val, n):
                self.xy = self.wall_check(move_val, n)
                self.dt_xy_sum = [0, 0]

    def wall_check(self, move_val, xy_ind):
        new_xy = self.xy.copy()
        new_xy[xy_ind] += move_val
        if self.grid_ref[0, new_xy[0], new_xy[1]] == 0:
            return new_xy
        elif self.grid_ref[0, new_xy[0], new_xy[1]] == 1:
            return self.xy

class Toe(Creature):
    def __init__(self, pos, grid):
        super().__init__(grid)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[255, 255, 0], 255]

class Ear(Creature):
    def __init__(self, pos, grid):
        super().__init__(grid)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[255, 0, 0], 255]

class Nose(Creature):
    def __init__(self, pos, grid):
        super().__init__(grid)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[0, 255, 0], 255]

class Running_Square(Creature):
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