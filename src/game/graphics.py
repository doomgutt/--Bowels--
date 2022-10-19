import numpy as np
import pyglet
from numba import njit

@njit
def rand_col(rgbo, type, amount=10):
    if type == 'col':
        rnd = np.random.randint(-amount, amount, 3)
    elif type == 'bw':
        rnd = np.repeat(np.random.randint(-amount, amount), 3)
    rgbo[:3] += rnd
    return rgbo


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


@njit(nogil=True, cache=True)
def mix_rgbo_list(rgbo_list):
    # find strongest opacity
    rgbo_list = rgbo_list.astype(np.float64)
    start_idx = 0
    for ii, rgbo in enumerate(rgbo_list):
        if rgbo[-1] == 255:
            start_idx = ii

    # recursively calculate new_rgbo
    new_rgbo_list = rgbo_list[start_idx:]
    new_rgbo = new_rgbo_list[0]
    for rgbo in new_rgbo_list[1:]:
        new_rgbo = mix_rgbo(new_rgbo, rgbo)

    return new_rgbo.astype(np.int64)


@njit(nogil=True, parallel=True, cache=True)
def mix_rgbo(rgbo1, rgbo2):
    """
    first rgbo has to have opacity = 255
    """
    new_rgbo = np.array([0, 0, 0, 255], np.float64)
    new_rgbo[:3] = rgbo1[:3]*(1-rgbo2[-1]/255) + rgbo2[:3]*(rgbo2[-1]/255)
    return new_rgbo



# ==================================
def test_v_lists():
    vlist_list = []
    rgbo1 = [0,   0,   0, 255]
    rgbo2 = [255, 0,   0, 200]
    rgbo3 = [0,   100,   0, 130]
    rgbo4 = [66,   2,   51, 20  ]

    # ==== mixed ======
    rgbo_mix = mix_rgbo_list(np.array([rgbo1, rgbo2, rgbo3, rgbo4])).tolist()
    coords_mix = (100, 100, 100, 200, 200, 200, 200, 200, 100, 100, 200, 100)
    vlist_mix = pyglet.graphics.vertex_list(6, ('v2i', coords_mix), ('c4B', rgbo_mix * 6))

    # ==== natural ====
    coords1 = (200, 100, 200, 200, 300, 200, 300, 200, 200, 100, 300, 100)
    vlist1 = pyglet.graphics.vertex_list(6, ('v2i', coords1), ('c4B', rgbo1 * 6))
    vlist2 = pyglet.graphics.vertex_list(6, ('v2i', coords1), ('c4B', rgbo2 * 6))
    vlist3 = pyglet.graphics.vertex_list(6, ('v2i', coords1), ('c4B', rgbo3 * 6))
    vlist4 = pyglet.graphics.vertex_list(6, ('v2i', coords1), ('c4B', rgbo4 * 6))

    # === add stuff ====
    vlist_list.append(vlist_mix)
    vlist_list.append(vlist1)
    vlist_list.append(vlist2)
    vlist_list.append(vlist3)
    vlist_list.append(vlist4)
    return vlist_list