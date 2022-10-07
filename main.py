import pyglet
import numpy as np
from src.game import discrete_space
from src.game import creatures
from src.game import senses
from src.game import graphics

# Use dims of x10 pixels
window_dims = (800, 600)
cell_size = 10

# ==== Make Window ====
window = pyglet.window.Window(*window_dims)
batch = pyglet.graphics.Batch()

# ==== Grid ====
grid = discrete_space.Grid(cell_size, window_dims, 'default_map.png')
grid.make_floor(batch, rand_col='bw')
fps_counter = graphics.FPS()

# ==== Agents ====
grid.add_agent(creatures.Creature(grid))
# grid.add_agent(creatures.Running_Square(grid))

# ==== Controls ====
for agent in grid.agents:
    window.push_handlers(agent.key_handler)

# ==== Update ====
def update(dt):
    fps_counter.update(dt)
    grid.update(dt)


# ==== Draw ====
@window.event
def on_draw():
    window.clear()
    agents = grid.draw_agents(batch)
    sight = grid.agents[0].draw_sight(batch, cell_size)
    batch.draw()

# ==== Debug ====
# for agent in grid.agents:
#     # agent.debug = True
#     pass

# ==== RUN ====
if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()