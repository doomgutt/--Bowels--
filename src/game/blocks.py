import numpy as np
from src.game import light

class LightWall:

    def __init__(self, xy, grid, group, batch):
        # setup
        density = 360
        steps = 1000
        brightness = 2

        # make light object
        self.grid_ref = grid
        self.xy = np.array(xy)
        self.light = light.LightSource(grid, xy, batch, group, density, steps)
        self.light.cell_brightness = brightness
        self.id = 11
        
        # sprites
        rgbo = [180, 160, 110, 255]
        self.sprite = grid.draw_square(self.xy, rgbo, group)

        # vertex_list
        self.mk_light_vlist()

    def update(self, grid):
        self.grid_ref = grid
        self.light.update_light(grid)

    def update_light(self, grid):
        l01 = grid.layers[0, 1]
        l20 = grid.layers[2, 0]
        object_grid = l01
        light_grid = light.mk_light_grid(object_grid)
        self.vlist.colors = self.get_light_cols(self.all_xy, light_grid, self.rgbo)
    
    def mk_light_vlist(self):
        grid = self.grid_ref

        v_num = np.prod(grid.dims)*6
        self.vlist = self.batch.add(
            v_num, pyglet.gl.GL_TRIANGLES,
            self.group, "v2i/static", "c4B/stream")

        # vertices
        light_vlist = ds.coords_to_v_list(
            grid.anchor, self.all_xy, grid.cell_size)
        self.vlist.vertices[:len(light_vlist)] = light_vlist

        # # colors
        self.update_light(grid)