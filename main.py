import numpy as np
import pyglet
from src.game import game_grid
import time

# Use dims of x10 pixels
window_dims = (800, 600)

# ==== Make Window ====
window = pyglet.window.Window(*window_dims)
batch = pyglet.graphics.Batch()
batch2 = pyglet.graphics.Batch()


# ---- Grid ----
grid = game_grid.Grid(10, window_dims)
grid.draw_to(batch, 'bw')

# bleeps = grid.test_grid()
# for row in bleeps:
#     for square in row:
#         square.batch = batch

# ==== Update ====
fps_counter = 0
dt_counter = 0
sq_counter = 2
def update(dt):
    global fps_counter, dt_counter, sq_counter
    # FPS
    fps_counter += 1
    dt_counter += dt
    if dt_counter > 1:
        print(fps_counter)
        dt_counter = 0
        fps_counter = 0
    
    # Other stuff
    sq_counter += 1
    grid.running_square(sq_counter, batch)
    # grid.draw_to(batch, 'bw')
    # t0 = time.time()
    # t1 = time.time()
    # total = t1-t0
    # print(total)
    # print("frame")
    # pass


# ==== Draw ====
@window.event
def on_draw():
    window.clear()
    batch.draw()

if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()