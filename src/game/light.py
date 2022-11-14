import numpy as np
import pyglet
from numba import njit, prange
from src.game import physics

# === NUMBA SETUP ============
PARALLEL_TOGGLE = False
NOGIL_TOGGLE = True
# ============================


class LightSource(physics.Radial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_light(self, object_grid, light_grid):
        return self._add_light(
            self.xy, self.radial, object_grid, light_grid)

    @staticmethod
    @njit(nogil=NOGIL_TOGGLE, cache=True)
    def _add_light(start_xy, radial, object_grid, light_grid, brightness=0.1):
        """
        Collision map:
        coll[0] = [x, y] - start point
        coll[1] = [x, y] - end point
        coll[2] = [start_id, int(start_brightness*1000)]
        """
        br_mult = 1000
        start_id = object_grid[start_xy[0], start_xy[1]]

        cut_radial = radial.copy() + start_xy
        collisions = np.zeros((len(radial), 3, 2), dtype='i2')
        for i, ray in enumerate(cut_radial):
            collisions[i, 0] = start_xy
            collisions[i, 2] = [start_id, int(brightness*br_mult)]
            for j, xy in enumerate(ray):
                x, y = xy
                if object_grid[x, y] != 0:
                    light_grid[x, y] += brightness
                    collisions[i, 1] = xy
                    break
                light_grid[x, y] += brightness
        return collisions



# ##################################################################
# ##################################################################


# class LightSource(physics.Radial):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.rgbo = np.array([200, 200, 100, 0])
#         self.brightness = 1

#     def mk_light_grid(self, object_grid):
#         return self.get_light_grid(self.xy, self.rays, object_grid, self.brightness)

#     def RAYZ(self, object_grid, anchor, batch, group):
#         beams = []
#         ray_seqs = ray_collision_seqs(self.xy, self.radial, object_grid)
#         beams = draw_ray_seq(anchor, ray_seqs, self.grid_ref.cell_size, batch, group)
#         return beams
#         # return self.draw_rays(anchor, self.xy, ray_seqs, batch, group)

#     # --- Update Light -------------------------------------------------
#     @staticmethod
#     @njit(nogil=NOGIL_TOGGLE, cache=True)
#     def get_light_grid(xy, rays, object_grid, brightness):
#         ctr = xy + 0.5
#         light_grid = np.zeros(object_grid.shape, dtype='i2')
#         for ii in prange(len(rays)):
#             for jj in prange(len(rays[ii][0])):
#                 x = np.int64(rays[ii][0][jj] + ctr[0])
#                 y = np.int64(rays[ii][1][jj] + ctr[1])
#                 if object_grid[x, y] in (0, 2):
#                     light_grid[x, y] += brightness
#                 else:
#                     light_grid[x, y] += brightness*20
#                     break
#         return light_grid

# @njit(nogil=NOGIL_TOGGLE, cache=True)
# def ray_collision_seqs(start_xy, radial, object_grid,
#                        step=0.3, max_refs=2, brightness=1, br_drop=0.7):
#     ray_seqs = np.zeros((len(radial), max_refs+1, 2), dtype="f8")
#     xy_steps = np.vstack((np.sin(radial), np.cos(radial))).T*step
    
#     for ii in prange(len(xy_steps)):
#         br = brightness
#         xy = start_xy + 0.5
#         ray_seqs[ii, 0] = xy
#         for rr in range(1, max_refs+1):
#             while True:
#                 xy += xy_steps[ii]
#                 tx, ty = xy.astype('i2')
#                 if object_grid[tx, ty] not in (0, 2):
#                     ray_seqs[ii, rr] = xy
#                     reflection_tool(xy, xy_steps[ii])
#                     br *= br_drop
#                     break
#     return ray_seqs


# @njit(nogil=NOGIL_TOGGLE, cache=True)
# def reflection_tool(end_xy, xy_step):
#     block_ctr = np.floor(end_xy) + 0.5
#     xy_dist = end_xy - block_ctr
#     vals = np.abs(xy_dist)
#     if vals[0] >= vals[1]:
#         xy_step *= np.array([-1, 1])  # x reflection
#         if xy_dist[0] < 0:
#             end_xy = np.array([np.floor(end_xy[0]), end_xy[1]])
#         else:
#             end_xy = np.array([np.ceil(end_xy[0]), end_xy[1]])
#     else:
#         xy_step *= np.array([1, -1])  # y reflection
#         if xy_dist[1] < 0:
#             end_xy = np.array([end_xy[0], np.floor(end_xy[1])])
#         else:
#             end_xy = np.array([end_xy[0], np.ceil(end_xy[1])])


# def draw_ray_seq(anchor, ray_seqs, cell_size, batch, group):
#     beams = []
#     for ray_coords in ray_seqs:
#         ray_coords += anchor
#         opacity = 100
#         for ii in range(len(ray_coords)-1):
#             start_xy = ray_coords[ii]
#             end_xy = ray_coords[ii+1]
#             beam = pyglet.shapes.Line(
#                 *(start_xy+1)*cell_size,
#                 *(end_xy+1)*cell_size,
#                 width=2, batch=batch, group=group)
#             opacity = opacity//2
#             beam.opacity = opacity
#             beams.append(beam)
#     return beams
# #################################################################################


    # @staticmethod
    # @njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
    # def get_light_cols(all_xy, light_grid, rgbo):
    #     rgbo_map = np.zeros((len(all_xy), 6, 4))
    #     for ii in prange(len(all_xy)):
    #         x, y = all_xy[ii]
    #         brightness = light_grid[x, y]
    #         col = rgbo.copy()
    #         col[3] = brightness
    #         rgbo_map[ii] = col
    #     return rgbo_map.flatten().astype(np.int32)

    # === Ray Stuff =================================================

    # @staticmethod
    # @njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
    # def get_light_rays(xy, rays, grid):
    #     ray_ends = np.zeros((len(rays), 2))
    #     for ii, ray in enumerate(rays):
    #         for jj in range(len(ray[0])):
    #             x = int(ray[0][jj] + xy[0])
    #             y = int(ray[1][jj] + xy[1])
    #             if grid[x, y] != 0:
    #                 ray_ends[ii][0] = ray[0][jj] + xy[0]
    #                 ray_ends[ii][1] = ray[1][jj] + xy[1]
    #                 break
    #     return ray_ends

    # # --- experimental ------------------------------------------------
    # @staticmethod
    # @njit(nogil=NOGIL_TOGGLE, parallel=PARALLEL_TOGGLE, cache=True)
    # def get_light_rays_w_reflection(xy, rays, grid):
    #     ray_ends = np.zeros((len(rays), 2))
    #     for ii, ray in enumerate(rays):
    #         for jj in range(len(ray[0])):
    #             x = int(ray[0][jj] + xy[0])
    #             y = int(ray[1][jj] + xy[1])
    #             if grid[x, y] != 0:
    #                 ray_ends[ii][0] = ray[0][jj] + xy[0]
    #                 ray_ends[ii][1] = ray[1][jj] + xy[1]
    #                 break
    #     return ray_ends

    # # === extras =======================================================
    # def beams_origin_to_vertices(self, vertices, xy=None):
    #     if xy == None:
    #         xy = self.center
    #     else:
    #         xy = self.xy
    #     beams = []
    #     for v in vertices:
    #         beam = pyglet.shapes.Line(
    #             *(xy+1)*self.grid_ref.cell_size,
    #             *(v+1)*self.grid_ref.cell_size,
    #             width=1,
    #             batch=self.batch, group=self.group)
    #         beam.opacity = 60
    #         beams.append(beam)
    #     return beams
    
    # def draw_lmap(self, light_grid):
    #     """
    #     draws the brightness map
    #     """
    #     active_map = np.clip(light_grid, 0, 255)
    #     squares = []
    #     for x, row in enumerate(active_map):
    #         for y, brightness in enumerate(row):
    #             if brightness == 0: continue
    #             square = self.grid_ref.draw_square(
    #                 x, y, [[200, 200, 0], brightness])
    #             squares.append(square)
    #     return squares


