import numpy as np
from PIL import Image

def import_map_floor(filename):
    dir_str = "./assets/maps/floors/"
    filepath = dir_str + filename
    img = Image.open(filepath)
    img_arr = np.asarray(img)
    img_arr = np.delete(img_arr, np.s_[1:], 2)
    img_arr = np.squeeze(img_arr) // 255
    # np.savetxt(dir_str+'ASCII_display.txt', img_arr, fmt='%i')
    return img_arr.T



