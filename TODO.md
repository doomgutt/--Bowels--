
# Stuff I should do/consider doing


## Speed
Try using Numba from the beginning. Perhaps even Cuda?


## Aesthetics
### Draw square random noise
it makes the noise every time a square is drawn. Need to be every time an object is made...


Remake board with TILE objects?


## Design
### Continuous movement
- instead of doing grid-movement, maybe do continuous movement, but render it on a grid...? probably not?


### Make a "tile" object? 


### Agent movement:

level 1 of grid:
    - at every timestep the agent returns their x,y
    - at every timestep the grid is reset and the agents are placed in order
        - conflicts resolved depending on who ate who