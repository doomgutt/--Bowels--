import numpy as np
import pyglet
from src.game import game_grid
import time

# Use dims of x10 pixels
window_dims = (800, 600)

# ==== Make Window ====
window = pyglet.window.Window(*window_dims)
batch = pyglet.graphics.Batch()
# batch2 = pyglet.graphics.Batch()


# ==== STATICS ====
# ---- Grid ----
grid = game_grid.Grid(10, window_dims, 'default_map.png')
grid.init_grid(batch, rand_col='bw')


# ==== Update ====
FPS_COUNTER = 0
DT_COUNTER = 0
SQ_COUNTER = 2
def update(dt):
    global FPS_COUNTER, DT_COUNTER, SQ_COUNTER

    # FPS
    FPS_COUNTER += 1
    DT_COUNTER += dt
    if DT_COUNTER > 1:
        print(FPS_COUNTER)
        DT_COUNTER = 0
        FPS_COUNTER = 0
    
    # Other stuff
    SQ_COUNTER += 1


    # grid.draw_to(batch, 'bw')
    # t0 = time.time()
    # t1 = time.time()
    # total = t1-t0
    # print(total)
    # print("frame")


# ==== Draw ====
@window.event
def on_draw():
    run_sq = grid.running_square(SQ_COUNTER, batch)
    window.clear()
    batch.draw()
    # batch2.draw()

if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()