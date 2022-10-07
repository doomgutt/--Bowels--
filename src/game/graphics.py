import numpy as np
import pyglet

class FPS:
    def __init__(self):
        self.fps_sum = 0
        self.dt_sum = 0
    
    def update(self, dt):
        self.fps_sum += 1
        self.dt_sum += dt
        if self.dt_sum > 1:
            print(self.fps_sum)
            self.dt_sum = 0
            self.fps_sum = 0

def randomize_color(rgbo, type, amount=10):
    if type == 'col':
        rgb = np.array(rgbo[0]) + np.random.randint(-amount, amount, 3)
    elif type == 'bw':
        rgb = np.array(rgbo[0]) + np.random.randint(-amount, amount)
    return [rgb, rgbo[1]]