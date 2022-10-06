import numpy as np
import pyglet
from src.game import game_grid
from src.game import creatures

# Use dims of x10 pixels
window_dims = (800, 600)

# ==== Make Window ====
window = pyglet.window.Window(*window_dims)
batch = pyglet.graphics.Batch()

# ==== Grid ====
grid = game_grid.Grid(10, window_dims, 'default_map.png')
grid.make_floor(batch, rand_col='bw')
fps_counter = game_grid.FPS()

# ==== Agents ====
grid.add_agent(creatures.Agent(grid))
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
    batch.draw()

if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()