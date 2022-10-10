import pyglet
import numpy as np
from src.game import graphics
from src.game import discrete_space
from src.game import creatures
from src.game import senses
# =========================================================
# Use dims of x10 pixels
window_dims = (800, 600)
cell_size = 10

# ==== Pyglet Setup ====
window = pyglet.window.Window(*window_dims)
batch1 = pyglet.graphics.Batch()
group1 = pyglet.graphics.Group()
clock1 = pyglet.clock.get_default()
clock1.schedule_interval(graphics.printFPS, 1)

# ==== Grid ====
grid = discrete_space.Grid(cell_size, window_dims, batch1, group1, 'default_map.png')
grid.make_floor(rand_col='bw')

# ==== Agents ====
grid.add_agent(creatures.Creature(grid, clock1, batch1, group1))
grid.agents_to_l1()

# ==== Controls ====
for agent in grid.agents:
    window.push_handlers(agent.key_handler)

# ==== Lights ====
# light_source_1 = senses.LightSource(grid, (20, 20), batch1, group1)
# light_source_1.attemptv2()

# ==== Update ====
def update(dt):
    grid.update(dt)

# ==== Draw ====

@window.event
def on_draw():
    sight = grid.agents[0].draw_sight(batch1, cell_size)
    # walls = grid.draw_surfaces()
    window.clear()
    batch1.draw()

# ==== Debug ====
# for agent in grid.agents:
#     # agent.debug = True
#     pass

# ==== TESTING ====


# ==== RUN ====
if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()