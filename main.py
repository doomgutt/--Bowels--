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



import pyglet
from src.game import graphics
from src.game import discrete_space
from src.game import creatures
# =========================================================
# Use dims of x10 pixels
window_dims = (800, 600)
cell_size = 10

# ==== Pyglet Setup ====
window = pyglet.window.Window(*window_dims)
batch1 = pyglet.graphics.Batch()
group1 = pyglet.graphics.Group()
clock1 = pyglet.clock.get_default()
fps_display = graphics.fps_custom_display(window)

# ==== Grid ====
grid = discrete_space.Grid(cell_size, window_dims, batch1, group1, 'default_map.png')
grid.make_floor(rand_col='bw')

# ==== Agents ====
grid.add_agent(creatures.LightBoi(grid, clock1, batch1, group1))
# grid.agents_to_l1()

# ==== Controls ====
for agent in grid.agents:
    window.push_handlers(agent.key_handler)

# ==== Lights ====
# 
#
#

# ==== Update ====
def update(dt):
    grid.update(dt)

# ==== Draw ====

@window.event
def on_draw():
    window.clear()
    
    # is there a better way to do this?
    draw_pile = []
    
    # Grid
    draw_pile.append(grid.draw())
    
    # Agents
    for agent in grid.agents:
        draw_pile.append(agent.draw())
    
    # Batch
    batch1.draw()
    fps_display.draw()

# ==== Debug ====
# 
#
#

# ==== TESTING ====
#
#

# ==== RUN ====
if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()