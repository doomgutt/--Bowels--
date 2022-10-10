import numpy as np
import pyglet

def randomize_color(rgbo, type, amount=10):
    if type == 'col':
        rgb = np.array(rgbo[0]) + np.random.randint(-amount, amount, 3)
    elif type == 'bw':
        rgb = np.array(rgbo[0]) + np.random.randint(-amount, amount)
    return [rgb, rgbo[1]]


def printFPS(dt):
    print(pyglet.clock.get_fps())