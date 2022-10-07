import numpy as np

def sight():
    pass



def radial(divisions=360):
    points = np.zeros((2, divisions))
    circle_full = 2*np.pi
    circle_segments = np.linspace(0, 359, divisions) * (circle_full/360)
    points[0] = np.sin(circle_segments)
    points[1] = np.cos(circle_segments)
    return points
