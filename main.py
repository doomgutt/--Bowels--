# import numpy as np
# import pyglet
# from time import time, sleep

# from src.game import graphics

# __WIDTH__ = 800
# __HEIGHT__ = 600
# __CELL_SIZE__ = 10

# class Window(pyglet.window.Window):
#     def __init__(self, width, height, refreshrate):
#         super(Window, self).__init__(width, height, vsync = False)
#         self.fps_display = graphics.fps_custom_display(self)
#         self.clock = pyglet.clock.get_default()
#         self.dt = 0
#         self.alive = 1
#         self.refreshrate = refreshrate
#         self.batch1 = pyglet.graphics.Batch()
#         self.group1 = pyglet.graphics.Group()
#         # self.r = pyglet.shapes.Rectangle(10, 10, 100, 100, color=(100, 100, 100), batch=self.batch1, group=self.group1)
#         self.vlist = np_to_vlist()
#         self.vertex_list = pyglet.graphics.vertex_list(3,('v2i', (100, 100, 150, 100, 150, 150)))

#     def on_draw(self):
#         self.render()

#     def render(self):
#         self.clear()
#         # self.batch1.draw()
#         self.vertex_list.draw(pyglet.gl.GL_TRIANGLES)
#         self.fps_display.draw()
#         self.flip()

#     def on_close(self):
#         self.alive = 0

#     def run(self):
#         while self.alive:
#             self.render()
#             event = self.dispatch_events() # <-- This is the event queue
#             self.dt = self.clock.tick()
#             sleep(1.0/self.refreshrate)

# win = Window(__WIDTH__, __HEIGHT__, 1000) # set the fps
# win.run()


# ============================================================================
import pyglet
from src.game import graphics
from src.game import grid_main

# ==== Game Dims =============================================================
# Use dims of x10 pixels
window_dims = (820, 920)
cell_size = 10

# ==== Pyglet Setup ==========================================================
window = pyglet.window.Window(*window_dims)

# --- enabling transparency?? ---
pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

# --- graphics --------
batch1 = pyglet.graphics.Batch()
group_0 = pyglet.graphics.OrderedGroup(0)
group_1 = pyglet.graphics.OrderedGroup(1)
group_2 = pyglet.graphics.OrderedGroup(2)
group_3 = pyglet.graphics.OrderedGroup(3)
groups = [group_0, group_1, group_2, group_3]

# --- time -------------
clock1 = pyglet.clock.get_default()
fps_display = graphics.fps_custom_display(window)

# ==== Grid ==================================================================
grid = grid_main.Grid(cell_size, clock1, batch1, groups, 'default_map.png')

# ==== Controls ==============================================================
for agent in grid.agents:
    window.push_handlers(agent.key_handler)

# ==== Draw ==================================================================
@window.event
def on_draw():
    window.clear()
    batch1.draw()
    fps_display.draw()

# ==== RUN ===================================================================
if __name__ == '__main__':
    pyglet.app.run()