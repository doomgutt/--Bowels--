import numpy as np
import pyglet
import time

def sight():
    pass


class Radial:
    def __init__(self):
        self.xy = [100, 100]
        self.divisions = 360
        self.step = 0.1

class LightSource:
    def __init__(self, grid, xy, batch, group, divisions=360, step=0.1):
        self.batch = batch
        self.group = group
        self.grid_ref = grid
        self.xy = np.array(xy)
        self.center = self.xy + [0.5, 0.5]
        self.divisions = divisions
        self.step = step
        self.coord_shift = np.array([[[0, 0], [0, 1], [1, 1], [1, 0]]])

        # light?
        self.mk_light_map()
        # a = grid.layers[0]
        # b = self.blow_up_grid_layer(0)
        # np.savetxt("testa", a, fmt='%i')
        # np.savetxt("testb", b, fmt='%i')

    # ==== Draw =================================================
    def draw(self):
        return self.lights_v01()

    # ==== LIGHT STUFF ==========================================
    def beams_origin_to_vertices(self, vertices, xy=None):
        if xy == None:
            xy = self.center
        else:
            xy = self.xy
        beams = []
        for v in vertices:
            # print(v)
            # print(xy)
            beam = pyglet.shapes.Line(
                *(xy+1)*self.grid_ref.cell_size,
                *(v+1)*self.grid_ref.cell_size,
                width=1, 
                batch=self.batch, group=self.group)
            beam.opacity = 60
            beams.append(beam)
        return beams
    
    def triangles_origin_to_edges(self, edges):
        triangles = []
        for edge in edges:
            tri = pyglet.shapes.Triangle(
                *(self.center+1)*self.grid_ref.cell_size,
                *(edge[2:]+1)*self.grid_ref.cell_size,
                *(edge[:2]+1)*self.grid_ref.cell_size, 
                color=(255, 255, 255), 
                batch=self.batch, group=self.group)
            tri.opacity = 40
            triangles.append(tri)
        return triangles
    
    # def draw_sq(self, x, y, rgb, opacity):
    #     pass

    def edges_to_vertices(self, edges):
        return edges.reshape((len(edges)*2, 2))
    
    # ==== Light Stuff v0.1 =====================================
    # thoughts:
    # - pre-calculate the directional stuff
    # - check at run-time

    def lights_v01(self):
        return self.debug_light_map2()

    # drawing
    def draw_light_tiles(self, xs, y_chunks):
        squares = []
        for i, x in enumerate(xs):
            for y in y_chunks[i]:
                if self.grid_ref.layers[0, int(x), int(y)] == 1:
                    return squares
                square = self.grid_ref.draw_square(x, y, [[200, 200, 0], 200])
                squares.append(square)
        return squares

    def mk_light_map(self):
        """
        px: positive x
        nx: negative x

        the idea is
        1. have a pre-made grid of ALL potential tiles
        2. shift that grid around and check light_beams for where they should end
        """

        # --- x_range setup ---
        dims = self.grid_ref.dims
        self.x_range = np.linspace(0, dims[0], dims[0], endpoint=False).astype(int)

        # --- radial setup ---
        self.cycle = 0
        self.light_density = 100  # has to be even to work well
        self.radial = np.linspace(0.001, np.pi, self.light_density//2, endpoint=False)

        # --- light map 2 ---
        self.light_map2 = np.zeros((self.light_density, dims[0]*2, dims[1]*2))

        # --- getting the light tiles ---
        light_map = []
        for i, rad in enumerate(self.radial):
            # new
            self.get_ray(i)

            # old
            y_chunks_p = self.get_tiles_all(rad)
            y_chunks_n = [-chunk for chunk in y_chunks_p]
            light_map.append([y_chunks_p, y_chunks_n])

        # --- return ---
        self.light_map = light_map

    def debug_light_map2(self):
        drawn = []
        # self.move_lmap2()
        # drawn.append(self.draw_lmap2())

        drawn = self.old_draw()
        return drawn
    
    def old_draw(self):
        drawn = []
        for i, _ in enumerate(self.radial):
            # y chunks
            y_chunks_p, y_chunks_n = self.light_map[i]

            # move and cut y_chunks
            py_shifted, ny_shifted = self.shift_y_chunks(
                self.center, y_chunks_p, y_chunks_n)

            # draw
            px_coords = self.xy[0] + self.x_range
            nx_coords = self.xy[0] - self.x_range

            # squares
            drawn.append(self.draw_light_tiles(px_coords[:-1], py_shifted))
            drawn.append(self.draw_light_tiles(nx_coords[:-1], ny_shifted))

            # beams
            # beam_px =  self.x_range_center[-1]       + self.center[0]
            # beam_py =  self.x_range_center[-1]*slope + self.center[1]
            # beam_nx = -self.x_range_center[-1]       + self.center[0]
            # beam_ny = -self.x_range_center[-1]*slope + self.center[1]
            # vertices = []
            # vertices.append(np.array([beam_px, beam_py]))
            # vertices.append(np.array([beam_nx, beam_ny]))
            # beams = self.beams_origin_to_vertices(vertices)
            # drawn.append(beams)
        return drawn

    def shift_y_chunks(self, xy, y_chunks_p, y_chunks_n):
        """
        Shift the 'light_map' to the position of the light source.
        """
        dims = self.grid_ref.dims
        y_chunks_p_shifted = []
        y_chunks_n_shifted = []
        for pchunk in y_chunks_p:
            shifted_chunk = xy[1]+pchunk
            y_chunks_p_shifted.append(shifted_chunk[shifted_chunk < dims[1]])
        for nchunk in y_chunks_n:
            shifted_chunk = xy[1]+nchunk-1
            y_chunks_n_shifted.append(shifted_chunk[shifted_chunk > 0])
        return y_chunks_p_shifted, y_chunks_n_shifted
    
    def get_ray(self, radial_idx):
        ray_angle = self.radial[radial_idx]
        slope = np.cos(ray_angle)/np.sin(ray_angle)

        y_lim = self.grid_ref.dims[1]-0.5
        self.x_range_center = np.concatenate((np.array([0]), self.x_range+0.5))
        y = self.x_range_center*slope
        off_grid = np.linspace(-0.5, y_lim, int(y_lim+0.5)+1)


        # pos slope
        if y[0] <= y[-1]:
            for i in range(len(y)-1):
                cond = (y[i]-1 <= off_grid) & (off_grid <= y[i+1])
                y_range = (off_grid[cond]+0.5).astype(int)

                self.light_map2[radial_idx][i][y_range] = 1
                self.light_map2[radial_idx+(self.light_density//2)][-i][y_range] = 1

        # neg slope
        elif y[0] > y[-1]:
            off_grid = -off_grid
            y_lim = - y_lim
            y = np.clip(y, y_lim, 0)
            for i in range(len(y)-1):
                cond = (y[i] >= off_grid) & (off_grid >= y[i+1]-1)
                y_range = (off_grid[cond]+0.5).astype(int)
                
                self.light_map2[radial_idx][i][y_range] = 1
                self.light_map2[radial_idx+(self.light_density//2)][-i][y_range] = 1
    
    def move_lmap2(self):
        shift = self.xy[0]
        lmap = np.roll(self.light_map2, shift)
        lmap[:, shift:] = 0
        self.active_lmap = lmap
        self.active_lmap = self.light_map2 + self.xy[1]
        self.smushed_lmap = np.sum(self.active_lmap, axis=0)

    def draw_lmap2(self):
        squares = []
        for y, row in enumerate(self.smushed_lmap):
            for x, brightness in enumerate(row):
                # print(brightness)
                square = self.grid_ref.draw_square(x, y, [[200, 200, 0], brightness])
                squares.append(square)
        return squares

        # squares = []
        # halfway = int(self.light_density//2)
        # for ray in self.active_lmap[:halfway]:
        #     for x in self.x_range:
        #         for y in ray[x]:
        #             if self.grid_ref.layers[0, int(x), int(y)] == 1:
        #                 return squares
        #             square = self.grid_ref.draw_square(x, y, [[200, 200, 0], 200])
        #             squares.append(square)
        # for ray in self.active_lmap[halfway:]:
        #     for x in self.x_range:
        #         x = -x
        #         for y in ray[x]:
        #             if self.grid_ref.layers[0, int(x), int(y)] == 1:
        #                 return squares
        #             square = self.grid_ref.draw_square(x, y, [[200, 200, 0], 200])
        #             squares.append(square)
        # return squares



    def get_tiles_all(self, ray_angle):
        """
        Because the center of the tile is at (0.5, 0.5) this
        function uses a custom `off_grid` variable instead of
        `np.floor` in order to get the values for the grid.
        """

        slope = np.cos(ray_angle)/np.sin(ray_angle)
        y_lim = self.grid_ref.dims[1]-0.5

        self.x_range_center = np.concatenate((np.array([0]), self.x_range+0.5))
        y = self.x_range_center*slope

        all_y_chunks = []
        off_grid = np.linspace(-0.5, y_lim, int(y_lim+0.5)+1)

        # pos slope
        if y[0] <= y[-1]:
            for i in range(len(y)-1):
                cond = (y[i]-1 <= off_grid) & (off_grid <= y[i+1])
                y_range = off_grid[cond]
                all_y_chunks.append(y_range)

        # neg slope
        if y[0] > y[-1]:
            off_grid = -off_grid
            y_lim = - y_lim
            y = np.clip(y, y_lim, 0)
            for i in range(len(y)-1):
                cond = (y[i] >= off_grid) & (off_grid >= y[i+1]-1)
                y_range = off_grid[cond]
                all_y_chunks.append(y_range)
        
        return all_y_chunks

    def circular_direction1(self, density=360):
        segments = np.linspace(0.001, np.pi, density, endpoint=False)
        return segments
    
    # def get_tiles2_backup(self, xs, slope):
    #     y_lim = self.grid_ref.dims[1]
    #     y = (xs*slope).astype(int)
    #     all_y_chunks = []
    #     for i in range(len(y)-1):
    #         upper = y[i+1]
    #         if y[i+1] > y_lim:
    #             upper = y_lim
    #         all_y_chunks.append(np.arange(y[i], upper+1))
    #     return all_y_chunks


    # def get_tiles2(self, xs, slope):
    #     """
    #     Because the center of the tile is at (0.5, 0.5) this
    #     function uses a custom `off_grid` variable instead of
    #     `np.floor` in order to get the values for the grid.
    #     """
    #     y_lim = self.grid_ref.dims[1]-0.5
    #     y = xs*slope
    #     off_grid = np.linspace(-0.5, y_lim, int(y_lim+0.5)+1)
    #     all_y_chunks = []
    #     for i in range(len(y)-1):
    #         lower = y[i]
    #         upper = y[i+1]
    #         if y[i+1] > y_lim:
    #             upper = y_lim
    #         y_range = off_grid[(lower-1 <= off_grid) & (off_grid <= upper)]
    #         all_y_chunks.append(y_range)
    #     return all_y_chunks
    
    # def get_tiles2_2(self, xs, slope):
    #     """
    #     Because the center of the tile is at (0.5, 0.5) this
    #     function uses a custom `off_grid` variable instead of
    #     `np.floor` in order to get the values for the grid.
    #     """
    #     y_lim = self.grid_ref.dims[1]-0.5
    #     y = xs*slope
    #     off_grid = -np.linspace(-0.5, y_lim, int(y_lim+0.5)+1)
    #     all_y_chunks = []
    #     for i in range(len(y)-1):
    #         lower = y[i]
    #         upper = y[i+1]
    #         if y[i+1] < -y_lim:
    #             upper = -y_lim
    #         y_range = off_grid[(lower >= off_grid) & (off_grid >= upper-1)]
    #         all_y_chunks.append(y_range)
    #     return all_y_chunks


# ============================================================
# ============================================================
# ============================================================
    # def calculating_light(self):
    #     """
    #     px: positive x
    #     nx: negative x

    #     the idea is
    #     1. have a pre-made grid of ALL potential tiles
    #     2. shift that grid around and check light_beams for where they should end
    #     """
        
    #     # setup
    #     dims = self.grid_ref.dims

    #     px_start = int(np.ceil(self.center[0]))
    #     px_range = np.linspace(px_start, dims[0], dims[0]-px_start+1).astype(int)
        
    #     nx_start = int(np.floor(self.center[0]))
    #     nx_range = np.flip(np.linspace(0, nx_start, nx_start+1).astype(int))
        
    #     print(nx_range)
    #     print(px_range)


    # # calculating
    # def get_tiles(self, xs, slope):
    #     y_lim = self.grid_ref.dims[1]
    #     y = (xs*slope + self.xy[1]).astype(int)
    #     all_y_chunks = []
    #     for i in range(len(y)-1):
    #         upper = y[i+1]
    #         if y[i+1] > y_lim:
    #             upper = y_lim
    #         all_y_chunks.append(list(range(y[i], upper+1)))
    #     return np.array(all_y_chunks)

    # # ==== Light Stuff v0 =======================================
    # # runs at about 8fps
    # def lights_v0(self):
    #     circ_dirs = self.circular_directions(density=360)
    #     dir_lines = self.mk_lines(circ_dirs, density=10)
    #     endpoints = self.get_collisions(dir_lines)
    #     beams = self.beams_origin_to_vertices(endpoints)
    #     return beams
    #     # return None

    # def get_collisions(self, dir_lines):
    #     end_points = []
    #     for line in dir_lines:
    #         for i, point in enumerate(line):
    #             point = point.round().astype(int)
    #             # print(point)
    #             if self.grid_ref.layers[0, point[0], point[1]] == 1:
    #                 end_points.append(line[i])
    #                 break
    #     return end_points

    # def mk_lines(self, directions, density=10):
    #     max_dims = self.grid_ref.dims
    #     dist = 100
    #     lines = np.zeros((len(directions), dist*density, 2))
    #     line = np.linspace(0, dist, dist*density)
    #     for i, deg in enumerate(directions):
    #         x = line*np.sin(deg)+self.center[0]
    #         y = line*np.cos(deg)+self.center[1]
    #         lines[i] = np.array([x, y]).T
    #     return lines

    # def circular_directions(self, density=360):
    #     segments = np.linspace(0, 2*np.pi, density, endpoint=False)
    #     return segments

    # # ==== Light Stuff v3 =======================================
    # def lights_v3(self):
    #     outer_edges = self.end_of_map_edes()
    #     vertices = self.edges_to_vertices(outer_edges)
    #     beams = self.beams_origin_to_vertices(vertices)
    #     return beams

    # def end_of_map_edes(self):
    #     max_dims = self.grid_ref.max_dims
    #     outer_edges = []
    #     for x in range(max_dims[0]-1):
    #         outer_edges.append([x, 0, x+1, 0])
    #         outer_edges.append([x, max_dims[1], x+1, max_dims[1]])
    #     for y in range(max_dims[1]-1):
    #         outer_edges.append([0, y, 0, y+1])
    #         outer_edges.append([max_dims[0], y, max_dims[0], y+1])
    #     return np.array(outer_edges)

    # def triangles_to_surfaces(self):
    #     surfaces = self.grid_ref.wall_surfaces
    #     closest = self.sort_edges_by_closest(surfaces)
    #     # edges = closest
    #     lit = self.lit_edges(closest)
    #     # lit_v = lit.reshape((len(lit)*2, 2))
    #     # vertices = edges.reshape((len(edges)*2, 2))
    #     return self.triangles_origin_to_edges(lit)

    # def beams_to_surfaces(self):
    #     # get surfaces
    #     surfaces = self.grid_ref.wall_surfaces
    #     closest = self.sort_edges_by_closest(surfaces)
    #     # edges = closest
    #     lit = self.lit_edges(closest)
    #     lit_v = lit.reshape((len(lit)*2, 2))
    #     # vertices = edges.reshape((len(edges)*2, 2))
    #     return self.beams_origin_to_vertices(lit_v)
    
    # def edge_cleaner(self, surfaces):
    #     closest = self.sort_edges_by_closest(surfaces)
    #     pass

    # # ==== Light Stuff v2 =======================================
    # def all_objects_from_grid(self):
    #     return self.grid_ref.layers[0] + self.grid_ref.layers[1]
        

    # def expanding_scope(self):
    #     max_x, max_y = self.grid_ref.max_dims
    #     for i in range(1, max(max_x, max_y), 10):
    #         xp = min(self.xy[0]+i, max_x)
    #         yp = min(self.xy[0]+i, max_y)
    #         xm = max(0, self.xy[0]-i)
    #         ym = max(0, self.xy[0]-i)

    #         # print("-----")
    #         # for x in range(xm, xp):
    #         #     for y in range(ym, yp):
    #         #         print(x, y)
    #         # if i == 5:
    #         #     break

    # def lights_v2(self):
    #     self.center = self.xy + [0.5, 0.5]
    #     t0 = time.time()
    #     object_grid = self.all_objects_from_grid()
    #     t1 = time.time()
    #     object_anchors = np.transpose(np.nonzero(object_grid))
    #     t2 = time.time()
    #     edges_by_anchor = self.anchors_to_edgelists(object_anchors)
    #     t3 = time.time()
    #     all_edges = edges_by_anchor.reshape((len(edges_by_anchor)*4, 4))
    #     closest = self.sort_edges_by_closest(all_edges)
    #     t4 = time.time()
    #     lit = self.lit_edges(closest)
    #     lit_v = lit.reshape((len(lit)*2, 2))
    #     t5 = time.time()
    #     beams = self.beams_origin_to_vertices(lit_v)
    #     t6 = time.time()
    #     print("=======================")
    #     print(f"all_objects_from_grid time: {t1-t0}") 
    #     print(f"object_anchors time: {t2-t1}") 
    #     print(f"anchors_to_edgelists time: {t3-t2}") 
    #     print(f"sort_edges_by_closest time: {t4-t3}") 
    #     print(f"lit_edges time: {t5-t4}") 
    #     print(f"beams_origin_to_vertices time: {t6-t5}") 
    #     return beams

    # def sort_edges_by_closest(self, all_edges):
    #     dist_list = self.edge_distances(self.center, all_edges)
    #     closest_idx = np.argsort(dist_list.min(1))
    #     return all_edges[closest_idx]

    # def edge_to_angle_segment(self, edge):
    #     points = edge.reshape(2,2).T
    #     rads = np.arctan2(points[0]-self.center[0], points[1]-self.center[1])
    #     full_rads = rads + (rads<0)*2*np.pi
    #     arc = np.sort(full_rads)
    #     return arc
    
    # def lit_edges(self, closest_edges):
    #     shift = 0
    #     # this shit takes AGES...
    #     # like up 0.2s per go...
    #     # that's like 5fps m8
    #     all_segments = []
    #     edge_idx = []
    #     for i, edge in enumerate(closest_edges):
    #         new_seg = self.edge_to_angle_segment(edge)
    #         if (new_seg[1] - new_seg[0]) > np.pi:
    #             new_seg = np.flip(new_seg)
    #         lower = True
    #         upper = True
    #         for seg in all_segments:
    #             if seg[0]-shift < new_seg[0] < seg[1]+shift:
    #                 lower = False
    #             if seg[0]-shift < new_seg[1] < seg[1]+shift:
    #                 upper = False
    #         if lower or upper:
    #             all_segments.append(new_seg)
    #             edge_idx.append(i)
    #     # all_segments = np.array(all_segments)
    #     return closest_edges[edge_idx]

    # def segments_circle_asf_ASdf_Asdf(self):
    #     pass

    # # ==== LIGHT STUFF v1 =======================================
    # def lights_v1(self, origin, obj_anchors):
    #     edges_by_anchor = self.anchors_to_edgelists(obj_anchors)
    #     print(f"all edges: {len(edges_by_anchor)*4}")
    #     all_light_edges = []
    #     all_ext_light_edges = []
    #     for sq in edges_by_anchor:
    #         light_edges = self.remove_shadow_edges(origin, sq)
    #         # debug
    #         for edge1 in light_edges:
    #             all_light_edges.append(edge1)
    #         ext_light_edges = self.rm_inside_edges(light_edges)
    #         for edge in ext_light_edges:
    #             all_ext_light_edges.append(edge)
    #     all_ext_light_edges = np.array(all_ext_light_edges)
    #     print(f"light edges: {len(all_light_edges)}")
    #     print(f"ext light edges: {len(all_ext_light_edges)}")
    #     return all_ext_light_edges.reshape((len(all_ext_light_edges)*2, 2))

    # def anchors_to_edgelists(self, anchors):
    #     """ edges must be done like this to be able to remove duplicates
    #     [0, 0, 0, 1] ^
    #     [0, 1, 1, 1] ->
    #     [1, 0, 1, 1] ^
    #     [0, 0, 1, 0] ->
    #     """
    #     edge_by_anchor = np.zeros((len(anchors), 4, 4))
    #     for i, a in enumerate(anchors):
    #         edge_by_anchor[i] = np.array([
    #             [a[0],   a[1],   a[0],   a[1]+1],
    #             [a[0],   a[1]+1, a[0]+1, a[1]+1],
    #             [a[0]+1, a[1],   a[0]+1, a[1]+1],
    #             [a[0],   a[1],   a[0]+1, a[1]]])
    #     return edge_by_anchor

    # def edge_distances(self, origin, edges):
    #     edge_dists = np.zeros((len(edges), 2))
    #     for i, edge in enumerate(edges):
    #         edge_dists[i] = [self.distance(origin, edge[:2]),
    #                         self.distance(origin, edge[2:])]
    #     return edge_dists


    # def remove_shadow_edges(self, origin, edges):
    #     edge_dists = self.edge_distances(origin, edges)
    #     remove_idx = [True for x in edge_dists]
    #     maxs = edge_dists.max(1)
    #     mins = edge_dists.min(1)
    #     for vmin in mins:
    #         for i, vmax in enumerate(maxs):
    #             if vmin >= vmax:
    #                 remove_idx[i] = False
    #     # # debug
    #     # print(remove_idx)
    #     # print(edge_dists[remove_idx])
    #     light_edges = edges[remove_idx]
    #     return light_edges


    # def rm_inside_edges(self, all_edges):
    #     uniq, counts = np.unique(all_edges, return_counts=True, axis=0)
    #     repeat_idx = np.nonzero(counts-1)[0]
    #     external_only = np.delete(uniq, repeat_idx, axis=0)
    #     return external_only

    # def distance(self, point1, point2):
    #     return np.hypot((point2[1]-point1[1]), (point2[0]-point1[0]))


# ==== Utility ===========================================    


def radial(divisions=360):
    points = np.zeros((2, divisions))
    circle_full = 2*np.pi
    circle_segments = np.linspace(0, 359, divisions) * (circle_full/360)
    points += [np.sin(circle_segments), np.cos(circle_segments)]
    return points


# ==== SENSES =========================================
class Eyes():
    pass


class Ears():
    pass


class Nose():
    pass


class LightBeam():
    def __init__(self, origin, step, xy_slope, radian_slope):
        self.origin = origin  # [0, 0]?
        self.xy_slope = xy_slope  # [1, 1]?
        self.radian_slope = radian_slope  # 0.5?
        self.step = step  # 0.01?


"""
# Making lights work

- every wall's xy is its bottom left corner
- I can make vertices for it then and calculate the light for all the nearest vertices
- then kill the redundancies?

"""





# make light sources
# - how to check light beams...



# instead of having a bunch of beams, 
# can just count the distance from origin to agent and see the angle...
#   but how do you check if something's inbetween...
#   calculate the closest target for each beam and stop there?


# pyglet.shapes.Line(x, y, x2, y2, width=2, batch=None)
