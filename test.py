from pyglet.window import Window
from pyglet.gl import Config;
w = Window(config=Config(major_version=4, minor_version=1))
print('{}.{}'.format(w.context.config.major_version, w.context.config.minor_version))

