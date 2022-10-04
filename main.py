import numpy as np
import pyglet
from src.game import game_grid

# Use dims of x10 pixels
window_dims = (800, 600)

# ==== Make Window ====
window = pyglet.window.Window(*window_dims)
batch = pyglet.graphics.Batch()


# ---- Grid ----
grid = game_grid.Grid(10, window_dims)
# grid.draw_to(batch, 'bw')

# bleeps = grid.test_grid()
# for row in bleeps:
#     for square in row:
#         square.batch = batch

# ==== Update ====
def update(dt):
    pass



# ==== Draw ====
@window.event
def on_draw():
    window.clear()
    grid.draw_to(batch, 'bw')
    batch.draw()

if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()