import numpy as np

def sight():
    pass


class Radial:
    def __init__(self):
        self.xy = [100, 100]
        self.divisions = 360
        self.step = 0.1

class LightSource:
    def __init__(self, grid, xy, batch, group, divisions=360, step=0.1):
        self.batch = batch
        self.group = group
        self.grid_ref = grid
        self.xy = xy
        self.center = xy + [0.5, 0.5]
        self.divisions = divisions
        self.step = step
        self.coord_shift = np.array([[[0, 0], [0, 1], [1, 1], [1, 0]]])

        # a = grid.layers[0]
        # b = self.blow_up_grid_layer(0)
        # np.savetxt("testa", a, fmt='%i')
        # np.savetxt("testb", b, fmt='%i')

    def get_vertices(self, layer_id):
        """
        recreates the grid layer as an array of vetrices:
        xy = [0, 0] -> [[0, 0], [0, 1], [1, 1], [1, 0]]
        """
        layer = self.grid_ref.layers[layer_id]
        object_coords = np.transpose(np.nonzero(layer))
        v_template = np.array([[[0, 0], [0, 1], [1, 1], [1, 0]]])
        v_list = np.repeat(v_template, repeats=len(object_coords), axis=0)
        for i, coord in enumerate(object_coords):
            v_list[i] += coord
        return v_list
    
    def closest_vertices(self, layer_id):
        v_list = self.get_vertices(layer_id)
        
        for entry in v_list:
            self.distance
            pass

    # ---- experimental ----

    def wall_distances(self):
        coords = np.nonzero(self.blow_up_grid_layer(0)).T
        for x in coords:
            pass


    def blow_up_grid_layer(self, layer_id):
        layer = self.grid_ref.layers[layer_id]
        blown_up_layer = np.repeat(layer, repeats=2, axis=0)
        blown_up_layer = np.repeat(blown_up_layer, repeats=2, axis=1)
        return blown_up_layer
    
def distance(x1, y1, x2, y2):
    return np.hypot((y2-y1), (x2-x1))

def radial(divisions=360):
    points = np.zeros((2, divisions))
    circle_full = 2*np.pi
    circle_segments = np.linspace(0, 359, divisions) * (circle_full/360)
    points += [np.sin(circle_segments), np.cos(circle_segments)]
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


"""
# Making lights work

- every wall's xy is its bottom left corner
- I can make vertices for it then and calculate the light for all the nearest vertices
- then kill the redundancies?

"""





# make light sources
# - how to check light beams...



# instead of having a bunch of beams, 
# can just count the distance from origin to agent and see the angle...
#   but how do you check if something's inbetween...
#   calculate the closest target for each beam and stop there?


# pyglet.shapes.Line(x, y, x2, y2, width=2, batch=None)
