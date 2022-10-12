import numpy as np
import pyglet
from pyglet.window import key
from src.utility import utils
from src.game import senses

class Creature:
    def __init__(self, grid_ref, clock, batch, group, rgbo=None):
        # pyglet setup
        self.grid_ref = grid_ref
        self.clock = clock
        self.batch = batch
        self.group = group

        # movement
        self.xy = np.array([10, 10])
        self.speed = 30

        # clock
        clock.schedule_interval(self.move, 1/self.speed)

        # body
        self.size = 1
        self.body_sq = 0
        self.body_circ = 0
        # self.body_edges = 0

        # stats
        self.id = 99
        self.rgbo = [[255, 255, 255], 255] if rgbo == None else rgbo

        # sprite
        self.mk_sprite()

        # controls
        self.key_handler = key.KeyStateHandler()
        self.controls = {
            "up"   : key.UP, 
            "down" : key.DOWN, 
            "left" : key.LEFT, 
            "right": key.RIGHT}

        # debug
        self.debug = False

    # ==== Sprite ====
    def mk_sprite(self):
        self.sprite = pyglet.shapes.Rectangle(
            (self.xy[0] + 1) * self.grid_ref.cell_size,
            (self.xy[1] + 1) * self.grid_ref.cell_size, 
            self.size * self.grid_ref.cell_size,
            self.size * self.grid_ref.cell_size, 
            color=self.rgbo[0], batch=self.batch, group=self.group)
        self.sprite.opacity = self.rgbo[1]

    def draw(self):
        pass

    # ==== Movement ====
    def move(self, dt):
        if self.key_handler[self.controls["up"]]:  # up
            if self.no_wall(self.xy+[0,1]):
                self.xy += [0,1]
        elif self.key_handler[self.controls["down"]]:  # down
            if self.no_wall(self.xy-[0,1]):
                self.xy -= [0,1]

        if self.key_handler[self.controls["left"]]:  # left
            if self.no_wall(self.xy-[1,0]):
                self.xy -= [1,0]
        elif self.key_handler[self.controls["right"]]:  # right
            if self.no_wall(self.xy+[1,0]):
                self.xy += [1,0]
        
        self.sprite.position = (self.xy+1)*self.grid_ref.cell_size

        #debug

    def no_wall(self, xy):
        if self.grid_ref.layers[0, xy[0], xy[1]] == 1:
            return False
        else:
            return True

    # ==== Body ====
    def body_center(self):
        return self.xy + self.grid_ref.cell_size/2


    # def set_body(self):
    #     sq_body = [self.xy, 
    #               [self.xy[0],   self.xy[1]+1],
    #               [self.xy[0]+1, self.xy[1]+1],
    #               [self.xy[0]+1, self.xy[1]  ]]
    #     pass

    # ==== DEBUG ====
    def draw_sight(self, batch, cell_size=10):
        px = 2
        squares = []
        radius = 10
        sight_circle = senses.radial(60) * radius
        shift = 15 - px/2 # +10 for grid_ref shift, +5 for half square -1 for pix size
        sight_circle[0] += self.xy[0]*cell_size + shift
        sight_circle[1] += self.xy[1]*cell_size + shift
        for p in sight_circle.T:
            squares.append(pyglet.shapes.Rectangle(*p, px, px, batch=batch))
        return squares

class LightBoi(Creature):
    def __init__(self, *args) -> None:
        rgbo = [[255, 215, 100], 20]
        super().__init__(*args, rgbo=rgbo)
        self.light = senses.LightSource(self.grid_ref, self.xy, self.batch, self.group)
        self.id = 33
        self.xy = np.array([30, 30])
    
    def move(self, dt):
        super().move(dt)
        self.light.xy = self.xy
        self.light.center = self.xy + [0.5, 0.5]
    
    def draw(self):
        super().draw()
        return self.light.draw()

class Toe(Creature):
    def __init__(self, pos, grid_ref):
        super().__init__(grid_ref)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[255, 255, 0], 255]

class Ear(Creature):
    def __init__(self, pos, grid_ref):
        super().__init__(grid_ref)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[255, 0, 0], 255]

class Nose(Creature):
    def __init__(self, pos, grid_ref):
        super().__init__(grid_ref)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgbo = [[0, 255, 0], 255]

class Running_Square(Creature):
    def __init__(self, grid_ref):
        super().__init__(grid_ref)
        self.rgbo = [[255, 0, 0], 255]
        self.counter = 0
        self.controls = {
            "up"   : key.W, 
            "down" : key.S, 
            "left" : key.A, 
            "right": key.D
        }

    def update(self, dt, grid_ref):
        super().update(dt, grid_ref)











##############################################################################
#### OLD CODE ################################################################
##############################################################################

    # ==== Update ====
    # def update(self, dt, grid_ref):
    #     # get latest grid_ref info
    #     self.grid_ref = grid_ref
        
    #     # move
    #     # self.update_dt(dt)
    #     # self.move()

    # def update_dt(self, dt):
    #     if self.key_handler[self.controls["up"]]:  # up
    #         self.dt_xy[1] = dt * self.speed
    #     elif self.key_handler[self.controls["down"]]:  # down
    #         self.dt_xy[1] = -dt * self.speed
    #     else:
    #         self.dt_xy[1] = 0

    #     if self.key_handler[self.controls["left"]]:  # left
    #         self.dt_xy[0] = -dt * self.speed
    #     elif self.key_handler[self.controls["right"]]:  # right
    #         self.dt_xy[0] = dt * self.speed
    #     else:
    #         self.dt_xy[0] = 0
    

    # # ==== Movement ====

    # def move(self):
    #     for n, val in enumerate(self.dt_xy):

    #         # check for opposite motion
    #         if not utils.same_sign(val, self.dt_xy_sum[n]):
    #             self.dt_xy_sum[n] = 0

    #         # add dt
    #         self.dt_xy_sum[n] += val

    #         # check threshold and wall, then move
    #         sum_abs = abs(self.dt_xy_sum[n])
    #         if sum_abs >= 1:
    #             move_val = round(self.dt_xy_sum[n]/sum_abs)
    #             # if not self.wall_check(move_val, n):
    #             self.xy = self.wall_check(move_val, n)
    #             self.dt_xy_sum = [0, 0]
    #     # self.body = self.xy

    # def wall_check(self, move_val, xy_ind):
    #     new_xy = self.xy.copy()
    #     new_xy[xy_ind] += move_val
    #     if self.grid_ref.layers[0, new_xy[0], new_xy[1]] == 0:
    #         return new_xy
    #     elif self.grid_ref.layers[0, new_xy[0], new_xy[1]] == 1:
    #         return self.xy