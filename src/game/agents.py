import numpy as np

class Agent:
    def __init__(self, grid, controls):
        self.grid_ref = grid
        self.x = 0
        self.y = 0
        self.speed = 1
        self.controls = controls
        self.rgb = np.array([255, 255, 255])
        self.opacity = 255

    def randomize_colour(self):
        pass

    def move_left(self):
        self.x -= self.speed

    def move_right(self):
        self.x += self.speed

    def move_up(self):
        self.y += self.speed

    def move_down(self):
        self.y -= self.speed


class Toe(Agent):
    def __init__(self, pos, grid, controls):
        super().__init__(grid, controls)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgb = np.array([255, 255, 0])

class Ear(Agent):
    def __init__(self, pos, grid, controls):
        super().__init__(grid, controls)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgb = np.array([255, 0, 0])

class Nose(Agent):
    def __init__(self, pos, grid, controls):
        super().__init__(grid, controls)
        self.x = pos[0]
        self.y = pos[1]
        self.speed = 4
        self.rgb = np.array([0, 255, 0])




controls = {
    "left"   :"",
    "right"  :"",
    "up"     :"",
    "down"   :"",
    "action" :""
}