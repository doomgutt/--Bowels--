import numpy as np
import pyglet

def randomize_color(rgbo, type, amount=10):
    if type == 'col':
        rgb = np.array(rgbo[0]) + np.random.randint(-amount, amount, 3)
    elif type == 'bw':
        rgb = np.array(rgbo[0]) + np.random.randint(-amount, amount)
    return [rgb, rgbo[1]]


# def printFPS(dt):
#     print(pyglet.clock.get_fps())

def fps_custom_display(window):
    fps_display = pyglet.window.FPSDisplay(window=window)
    fps_display.label.font_name='Verdana'
    fps_display.label.font_size=8
    fps_display.label.x=10
    fps_display.label.y=10
    fps_display.label.color=(255, 255, 255, 255)
    return fps_display


