import numpy as np
from pyglet.window import key
from src.game import senses

class Creature:
    def __init__(self, xy, grid, group, a_id, m_speed, u_speed=30):
        # grid
        self.GRID = grid
        self.glayers = grid.layers
        
        # pyglet setup
        self.batch = grid.batch
        self.group = group

        # movement
        self.xy = np.array(xy)
        self.m_speed = m_speed
        self.u_speed = u_speed
        self.mu, self.md, self.ml, self.mr = 0, 0, 0, 0

        # clock
        self.clock = grid.clock
        self.dt = 0
        # self.clock.schedule_interval(self.update, 1/self.m_speed)
        # self.clock.schedule_interval(self.move,   1/self.m_speed)

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
        self.sight = None
        self.hearing = None
        self.smell = None
        self.touch = None

    # ==== Update ====
    def update(self, dt):
        if self.tick(dt, self.m_speed):
            self.update_senses()
            self.move()

    # ==== Sensing ====
    def update_senses(self):
        pass

    # ==== Moving ====
    def move(self):
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

    def no_wall(self, xy):
        if self.GRID.layers[0, 2, xy[0], xy[1]] == 0:
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
# =========================================================================
class Toe(Creature):
    def __init__(self, xy, grid, group):
        super().__init__(xy, grid, group, a_id=1, m_speed=10, u_speed=100)
        self.sight = senses.SightGrid(grid)
    
    def update_senses(self):
        self.sight.update(self.xy, self.glayers)

# =========================================================================
class Ear(Creature):
    def __init__(self, xy, grid, group):
        super().__init__(xy, grid, group, a_id=2, m_speed=20, u_speed=100)

# =========================================================================
class Nose(Creature):
    def __init__(self, xy, grid, group):
        super().__init__(xy, grid, group, a_id=3, m_speed=4, u_speed=100)

# =========================================================================











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