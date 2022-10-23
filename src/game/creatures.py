import numpy as np
import pyglet
from pyglet.window import key
from src.game import light

class Creature:
    def __init__(self, xy, grid, group, m_speed, u_speed, a_id, rgbo):
        # pyglet setup
        self.grid_ref = grid
        self.batch = grid.batch
        self.group = group

        # movement
        self.xy = np.array(xy)
        self.m_speed = m_speed
        self.u_speed = u_speed

        # clock
        self.clock = grid.clock
        self.clock.schedule_interval(self.update, 1/self.u_speed)
        self.clock.schedule_interval(self.move,   1/self.m_speed)

        # stats
        self.id = a_id
        self.rgbo = rgbo

        # sprite
        self.sprite = grid.draw_square(self.xy, self.rgbo, self.group)

        # controls
        self.key_handler = key.KeyStateHandler()
        self.controls = {
            "up"   : key.UP, 
            "down" : key.DOWN, 
            "left" : key.LEFT, 
            "right": key.RIGHT}

    # ==== Update ====
    def update(self, dt):
        pass

    def draw(self):
        pass

    # ==== Sensing ====
    def update_senses(grid):
        pass

    # ==== Moving ====
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
        
        # move sprite
        pos = (self.xy+1+self.grid_ref.anchor)*self.grid_ref.cell_size
        self.sprite.position = pos

    def no_wall(self, xy):
        if self.grid_ref.layers[0, 2, xy[0], xy[1]] == 0:
            return True
        else:
            return False


# =========================================================================
# =========================================================================

class LightBoi(Creature):
    def __init__(self, *args) -> None:
        rgbo = [0, 255, 0, 255]
        super().__init__(*args, rgbo=rgbo)
        self.light = light.LightSource(self.grid_ref, self.xy, self.batch, self.group)
        self.id = 33
        self.xy = np.array([30, 30])
        self.clock_speed = 1 
        self.clock.schedule_interval(self.update, self.clock_speed)
    
    def move(self, dt):
        super().move(dt)
        self.light.xy = self.xy
        self.light.center = self.xy + [0.5, 0.5]
    
    def update(self, dt):
        super().update(dt)
        self.light.update(dt)


# =========================================================================
class Toe(Creature):
    def __init__(self, xy, grid, group):
        m_speed = 10
        u_speed = 100
        a_id = 1
        rgbo = [100, 200, 0, 255]
        super().__init__(xy, grid, group, m_speed, u_speed, a_id, rgbo)

# =========================================================================
class Ear(Creature):
    def __init__(self, xy, grid, group):
        m_speed = 20
        u_speed = 100
        a_id = 2
        rgbo = [255, 0, 0, 255]
        super().__init__(xy, grid, group, m_speed, u_speed, a_id, rgbo)

# =========================================================================
class Nose(Creature):
    def __init__(self, xy, grid, group):
        m_speed = 4
        u_speed = 100
        a_id = 3
        rgbo = [0, 255, 0, 255]
        super().__init__(xy, grid, group, m_speed, u_speed, a_id, rgbo)

# =========================================================================
# class Running_Square(Creature):
#     def __init__(self, grid_ref):
#         super().__init__(grid_ref)
#         self.rgbo = [[255, 0, 0], 255]
#         self.counter = 0
#         self.controls = {
#             "up"   : key.W, 
#             "down" : key.S, 
#             "left" : key.A, 
#             "right": key.D
#         }











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
    #     if self.grid_ref.layers[0, 1, new_xy[0], new_xy[1]] == 0:
    #         return new_xy
    #     elif self.grid_ref.layers[0, 1, new_xy[0], new_xy[1]] == 1:
    #         return self.xy