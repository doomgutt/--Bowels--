import numpy as np
from numba import njit

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================
# https://github.com/fjug/BobSeg/blob/master/bresenham.py


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
    scale = np.zeros((len(abs_dxdy), 1), dtype='i8')
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

    return np.rint(bline)


def _bresenhamline_nslope(slope):
    """
    Normalize slope for Bresenham's line algorithm.
    >>> s = np.array([[-2, -2, -2, 0]])
    >>> _bresenhamline_nslope(s)
    array([[-1., -1., -1.,  0.]])
    >>> s = np.array([[0, 0, 0, 0]])
    >>> _bresenhamline_nslope(s)
    array([[ 0.,  0.,  0.,  0.]])
    >>> s = np.array([[0, 0, 9, 0]])
    >>> _bresenhamline_nslope(s)
    array([[ 0.,  0.,  1.,  0.]])
    """
    scale = np.amax(np.abs(slope), axis=1).reshape(-1, 1)
    zeroslope = (scale == 0).all(1)
    scale[zeroslope] = np.ones(1)
    normalizedslope = np.array(slope, dtype=np.double) / scale
    normalizedslope[zeroslope] = np.zeros(slope[0].shape)
    return normalizedslope


def bresenham_numpy(start, end, max_iter=-1, flatten=False):
    """
    Returns npts lines of length max_iter each.
    (npts x max_iter x dimension)
    >>> s = np.array([[3, 1, 9, 0],[0, 0, 3, 0]])
    >>> _bresenhamlines(s, np.zeros(s.shape[1]), max_iter=-1)
    array([[[ 3,  1,  8,  0],
            [ 2,  1,  7,  0],
            [ 2,  1,  6,  0],
            [ 2,  1,  5,  0],
            [ 1,  0,  4,  0],
            [ 1,  0,  3,  0],
            [ 1,  0,  2,  0],
            [ 0,  0,  1,  0],
            [ 0,  0,  0,  0]],
    <BLANKLINE>
           [[ 0,  0,  2,  0],
            [ 0,  0,  1,  0],
            [ 0,  0,  0,  0],
            [ 0,  0, -1,  0],
            [ 0,  0, -2,  0],
            [ 0,  0, -3,  0],
            [ 0,  0, -4,  0],
            [ 0,  0, -5,  0],
            [ 0,  0, -6,  0]]])
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
