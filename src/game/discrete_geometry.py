import PIL.ImageDraw
import PIL.Image
import numpy as np
from numba import njit

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================
# LINE: https://github.com/fjug/BobSeg/blob/master/bresenham.py
# CIRCLE: https://funloop.org/post/2021-03-15-bresenham-circle-drawing-algorithm.html


# ==== INDEX STUFF ===========================================================
# @njit(nogil=NOGIL_TOGGLE, cache=True)
def box_index(max_x, max_y, xy_shift):
    box = np.zeros((max_x * 2 + max_y * 2 - 4, 2), dtype='i2')
    i = 0
    for x in range(max_x):
        for y in range(max_y):
            if (x == 0) or (x == max_x-1) or (y == 0) or (y == max_y-1):
                box[i] = [x, y]
                i += 1
    return box + xy_shift


# ==== RADIAL of BRESENHAM LINES =============================================

def bresenham_radial(dims, mode="numba"):
    radius = hypot(*dims)
    ends = np.array(bresenham_circle(radius))
    # ends = np.array(b_circle(radius))
    starts = np.repeat(np.array([[0, 0]]), len(ends), axis=0)
    if mode == "numpy":
        lines = bresenham_numpy(starts, ends)
    elif mode == "numba":
        lines = bresenham_numba(starts, ends)
    return lines

def rad_radial(dims, density=360, mode="numba"):
    radius = hypot(*dims)
    rads = np.linspace(0, 2*np.pi, density, endpoint=False)
    start = np.repeat(np.array([[0, 0]]), len(rads), axis=0)
    ends = np.array((np.sin(rads), np.cos(rads))).T*radius
    if mode == "numpy":
        lines = bresenham_numpy(start, ends)
    elif mode == "numba":
        lines = bresenham_numba(start, ends)
    return lines

# ==== BRESENHAM CIRCLES =====================================================

@njit
def b_circle(radius):
    "Bresenham complete circle algorithm in Python"
    # init vars
    switch = 3 - (2 * radius)
    points = set()
    x = 0
    y = radius
    # first quarter/octant starts clockwise at 12 o'clock
    while x <= y:
        # first quarter first octant
        points.add((x, -y))
        # first quarter 2nd octant
        points.add((y, -x))
        # second quarter 3rd octant
        points.add((y, x))
        # second quarter 4.octant
        points.add((x, y))
        # third quarter 5.octant
        points.add((-x, y))
        # third quarter 6.octant
        points.add((-y, x))
        # fourth quarter 7.octant
        points.add((-y, -x))
        # fourth quarter 8.octant
        points.add((-x, -y))
        if switch < 0:
            switch = switch + (4 * x) + 6
        else:
            switch = switch + (4 * (x - y)) + 10
            y = y - 1
        x = x + 1
    return list(points)



@njit(nogil=NOGIL_TOGGLE, cache=True)
def mirror_points_8(x, y):
    """ Return 8-way symmetry of points. """
    return [( x,  y),
            ( y,  x),
            (-x,  y),
            (-y,  x),
            ( x, -y),
            ( y, -x),
            (-x, -y),
            (-y, -x)]


@njit(nogil=NOGIL_TOGGLE, cache=True)
def bresenham_circle(r):
    """ Like draw_circle_bresenham_integer_ene, but start from (0, -r) and move
    E or NE. Notice how we only need the addition instruction in the while loop
    (y is incremented, not decremented). """
    points = []
    x = 0
    y = -r
    F_M = 1 - r
    # Initial value for (0,-r) for 2x + 3 = 0x + 3 = 3.
    d_e = 3
    # Initial value for (0,-r) for 2(x + y) + 5 = 0 - 2y + 5 = -2y + 5.
    d_ne = -(r << 1) + 5
    points.extend(mirror_points_8(x, y))
    while x < -y:
        if F_M < 0:
            F_M += d_e
        else:
            F_M += d_ne
            d_ne += 2
            y += 1
        d_e += 2
        d_ne += 2
        x += 1
        points.extend(mirror_points_8(x, y))
    return list(set(points))


@njit(nogil=NOGIL_TOGGLE, cache=True)
def bresenham_circle_tweaked(radius):
    """
    Taken from:
    https://funloop.org/post/2021-03-15-bresenham-circle-drawing-algorithm.html
    """
    points = []
    x = 0
    y = -radius
    F_M = 1 - radius
    d_e = 3
    d_ne = -(radius << 1) + 5
    points.extend(mirror_points_8(x, y))
    while x < -y:
        if F_M <= 0:
            F_M += d_e
        else:
            F_M += d_ne
            d_ne += 2
            y += 1
        d_e += 2
        d_ne += 2
        x += 1
        points.extend(mirror_points_8(x, y))
    return list(set(points))


# ==== BRESENHAM LINES =======================================================

@njit(nogil=NOGIL_TOGGLE, cache=True)
def bresenham_numba(start, end, max_iter=-1):
    """
    - Normalizing Slope
        - dxdy: calculate slopes: ends-starts
        - scale: get furthest x/y distance for every dxdy
            - set 0 slope entries to 1's (when two points are the same)
        - nslope: normalized slope
    - Calculate lines
        - npts, dims: number of points and point dimensions
        - max_iter: get furthest distance for any two points
    """

    # Normalizing slope
    dxdy = (end - start)
    abs_dxdy = np.abs(dxdy)
    scale = np.zeros((len(abs_dxdy), 1), dtype='i2')
    for ii, xy in enumerate(abs_dxdy):
        sc = max(xy)
        scale[ii] = sc if sc != 0 else 1
    nslope = dxdy.astype('f8') / scale

    # Steps to iterate on
    npts, dim = start.shape
    if max_iter == -1:
        max_iter = np.max(scale)
    stepseq = np.arange(1, max_iter + 1)
    stepmat = stepseq.repeat(dim).reshape((-1, dim))

    # Calculate lines
    bline = np.zeros((len(start), *stepmat.shape), dtype='f8')
    for ii, start_xy in enumerate(start):
        bline[ii] = start_xy + nslope[ii] * stepmat

    return np.rint(bline).astype('i2')

def _bresenhamline_nslope(slope):
    scale = np.amax(np.abs(slope), axis=1).reshape(-1, 1)
    zeroslope = (scale == 0).all(1)
    scale[zeroslope] = np.ones(1)
    normalizedslope = np.array(slope, dtype=np.double) / scale
    normalizedslope[zeroslope] = np.zeros(slope[0].shape)
    return normalizedslope


def bresenham_numpy(start, end, max_iter=-1):
    """
    Taken from:
    https://github.com/fjug/BobSeg/blob/master/bresenham.py
    """
    if max_iter == -1:
        max_iter = np.amax(np.amax(np.abs(end - start), axis=1))
    npts, dim = start.shape
    nslope = _bresenhamline_nslope(end - start)

    # steps to iterate on
    stepseq = np.arange(1, max_iter + 1)
    stepmat = np.tile(stepseq, (dim, 1)).T

    # some hacks for broadcasting properly
    bline = start[:, np.newaxis, :] + nslope[:, np.newaxis, :] * stepmat

    # Approximate to nearest int
    return np.array(np.rint(bline), dtype=start.dtype)

# ==== MATH ==================================================================

def hypot(x, y):
    return np.sqrt(x**2 + y**2).astype("i8")