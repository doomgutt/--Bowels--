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
clock1.schedule_interval(graphics.printFPS, 1)

# ==== Grid ====
grid = discrete_space.Grid(cell_size, window_dims, batch1, group1, 'default_map.png')
grid.make_floor(rand_col='bw')

# ==== Agents ====
grid.add_agent(creatures.LightBoi(grid, clock1, batch1, group1))
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

# ==== Debug ====
# for agent in grid.agents:
#     # agent.debug = True
#     pass

# ==== TESTING ====


# ==== RUN ====
if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()