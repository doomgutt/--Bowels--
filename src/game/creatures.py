import numpy as np
from pyglet.window import key
from src.game.senses import eyes
from src.game.senses import ears

class Creature:
    def __init__(self, xy, grid, a_id, m_speed, u_speed=30):
        # grid
        self.GRID = grid
        
        # movement
        self.moving = False
        self.xy = np.array(xy)
        self.m_speed = m_speed
        self.u_speed = u_speed

        # clock
        self.dt = 0

        # stats
        self.id = a_id

        # controls
        self.key_handler = key.KeyStateHandler()
        self.controls = {
            "up"   : key.UP, 
            "down" : key.DOWN, 
            "left" : key.LEFT, 
            "right": key.RIGHT}

        # senses
        self.eyes = None
        self.ears = None
        self.noses = None
        self.skin = None

    # ==== Update ====
    def update(self, dt, grid):
        self.GRID = grid
        if self.tick(dt, self.m_speed):
            self.update_senses()
            self.move()

    # ==== Sensing ====
    def update_senses(self):
        pass

    # ==== Moving ====
    def move(self):
        self.moving = False
        if self.key_handler[self.controls["up"]]:  # up
            self.moving = True
            if self.no_wall(self.xy+[0,1]):
                self.xy += [0,1]
        elif self.key_handler[self.controls["down"]]:  # down
            self.moving = True
            if self.no_wall(self.xy-[0,1]):
                self.xy -= [0,1]

        if self.key_handler[self.controls["left"]]:  # left
            self.moving = True
            if self.no_wall(self.xy-[1,0]):
                self.xy -= [1,0]
        elif self.key_handler[self.controls["right"]]:  # right
            self.moving = True
            if self.no_wall(self.xy+[1,0]):
                self.xy += [1,0]

    def no_wall(self, xy):
        if self.GRID.layers[1, xy[0], xy[1]] == 0:
            return True
        else:
            return False

    def tick(self, dt, mult):
        self.dt += dt
        if self.dt*mult > 1:
            self.dt = 0
            return True
        return False


# =========================================================================
class Eye(Creature):
    def __init__(self, xy, grid):
        super().__init__(xy, grid, a_id=200, m_speed=10, u_speed=100)
        self.eyes = eyes.Eyes(grid, anchor=(4, 4))
        self.controls = {
            "up"   : key.W, 
            "down" : key.S, 
            "left" : key.A, 
            "right": key.D}
    
    def update_senses(self):
        self.eyes.see(self.xy, self.GRID)

# -------------------------------------------------------------------------
class Ear(Creature):
    def __init__(self, xy, grid):
        super().__init__(xy, grid, a_id=201, m_speed=20, u_speed=100)
        self.ears = ears.Ears(grid, anchor=(10, 4))
    
    def update_senses(self):
        self.ears.see(self.xy, self.GRID)

# -------------------------------------------------------------------------
class Nose(Creature):
    def __init__(self, xy, grid):
        super().__init__(xy, grid, a_id=202, m_speed=4, u_speed=100)

# -------------------------------------------------------------------------











##############################################################################
#### OLD CODE ################################################################
##############################################################################

    # ==== Update ====
    # def update(self, dt, GRID):
    #     # get latest GRID info
    #     self.GRID = GRID
        
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
    #     if self.GRID.layers[0, 1, new_xy[0], new_xy[1]] == 0:
    #         return new_xy
    #     elif self.GRID.layers[0, 1, new_xy[0], new_xy[1]] == 1:
    #         return self.xy