import pyglet
import numpy as np
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

# ==== Grid ====
grid = discrete_space.Grid(cell_size, window_dims, batch1, group1, 'default_map.png')
grid.make_floor(rand_col='bw')

# ==== Agents ====
grid.add_agent(creatures.Creature(grid))
# grid.add_agent(creatures.Running_Square(grid))

# ==== Controls ====
for agent in grid.agents:
    window.push_handlers(agent.key_handler)

# ==== Update ====
def update(dt):
    # print(f"FPS is {pyglet.clock.get_fps()}", end="\r")
    grid.update(dt)

# ==== Draw ====
@window.event
def on_draw():
    agents = grid.draw_agents()
    sight = grid.agents[0].draw_sight(batch1, cell_size)
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