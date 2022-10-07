import numpy as np

def sight():
    pass


class Radial:
    def __init__(self):
        self.xy = [100, 100]
        self.divisions = 360
        self.step = 0.1

def radial(divisions=360):
    points = np.zeros((2, divisions))
    circle_full = 2*np.pi
    circle_segments = np.linspace(0, 359, divisions) * (circle_full/360)
    points[0] = np.sin(circle_segments)
    points[1] = np.cos(circle_segments)
    return points

class Eyes():
    pass


class Ears():
    pass


class Nose():
    pass


class LightBeam():
    def __init__(self, origin, step, xy_slope, radian_slope):
        self.origin = origin  # [0, 0]?
        self.xy_slope = xy_slope  # [1, 1]?
        self.radian_slope = radian_slope  # 0.5?
        self.step = step  # 0.01?

# make light sources
# - how to check light beams...



# instead of having a bunch of beams, 
# can just count the distance from origin to agent and see the angle...
#   but how do you check if something's inbetween...
#   calculate the closest target for each beam and stop there?


# pyglet.shapes.Line(x, y, x2, y2, width=2, batch=None)
