import numpy as np
import pyglet
from src.testing import grid

# Use dims of x10 pixels
window_dims = (800, 600)

# ==== Make Window ====
window = pyglet.window.Window(*window_dims)
batch = pyglet.graphics.Batch()


# ---- Grid ----
cell_size = 10
grid_dims = (window_dims[0]//cell_size, window_dims[1]//cell_size)
grid = np.zeros(grid_dims, dtype='object')


col_gap = 10
for x in range(grid.shape[0]):
    col_gap *= -1
    for y in range(grid.shape[1]):
        col_gap *= -1
        col = 110 + col_gap
        grid[x, y] = pyglet.shapes.Rectangle(x*10, y*10, 10, 10, color=(col, col, col), batch=batch)


# ==== Draw ====
@window.event
def on_draw():
    window.clear()
    batch.draw()

if __name__ == '__main__':
    pyglet.app.run()