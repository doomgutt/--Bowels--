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

        self.cycle = 0
        # a = grid.layers[0]
        # b = self.blow_up_grid_layer(0)
        # np.savetxt("testa", a, fmt='%i')
        # np.savetxt("testb", b, fmt='%i')

    # ==== Draw =================================================
    def draw(self):
        # return self.lights_v2()
        # return self.lights_v3()
        # return self.lights_v0()
        return self.lights_v01()

    # ==== LIGHT STUFF ==========================================
    def beams_origin_to_vertices(self, vertices, xy=None):
        if xy == None:
            xy = self.center
        else:
            xy = self.xy
        beams = []
        for v in vertices:
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
        dims = self.grid_ref.dims
        x_p = np.linspace(0, dims[0], dims[0]+1)# +0.5  ?
        x_m = -x_p
        degs = self.circular_direction1()
        deg = degs[self.cycle]
        slope = np.cos(deg)/np.sin(deg)
        y_chunks = self.get_tiles(x_p, slope)


        # draw
        drawn = []
        cutoff = 10
        x_p_shifted = x_p + self.xy[0]
        x_p_shifted = x_p_shifted[:10]

        # squares
        drawn.append(self.draw_passed_sq(x_p_shifted, y_chunks))

        # beams
        cust_y = x_p[cutoff-1]*slope + self.xy[1]
        vertices = np.array([x_p_shifted[cutoff-1], cust_y])[None]
        beams = self.beams_origin_to_vertices(vertices, xy=True)
        drawn.append(beams)
        return drawn

    def get_tiles(self, xs, slope):
        y = (xs*slope + self.xy[1]).astype(int)
        # if y[1] < y[0]:
        #     y = np.flip(y)
        all_y_chunks = []
        for i in range(len(y)-1):
            all_y_chunks.append(list(range(y[i], y[i+1]+1)))
        return np.array(all_y_chunks)

    def circular_direction1(self, density=360):
        segments = np.linspace(0.001, np.pi, density, endpoint=False)
        return segments

    def draw_passed_sq(self, xs, y_chunks):
        squares = []
        for i, x in enumerate(xs):
            for y in y_chunks[i]:
                square = self.grid_ref.draw_square(x, y, [[255, 255, 255], 70])
                squares.append(square)
        return squares

    # ==== Light Stuff v0 =======================================
    # runs at about 8fps
    def lights_v0(self):
        circ_dirs = self.circular_directions(density=360)
        dir_lines = self.mk_lines(circ_dirs, density=10)
        endpoints = self.get_collisions(dir_lines)
        beams = self.beams_origin_to_vertices(endpoints)
        return beams
        # return None

    def get_collisions(self, dir_lines):
        end_points = []
        for line in dir_lines:
            for i, point in enumerate(line):
                point = point.round().astype(int)
                # print(point)
                if self.grid_ref.layers[0, point[0], point[1]] == 1:
                    end_points.append(line[i])
                    break
        return end_points

    def mk_lines(self, directions, density=10):
        max_dims = self.grid_ref.dims
        dist = 100
        lines = np.zeros((len(directions), dist*density, 2))
        line = np.linspace(0, dist, dist*density)
        for i, deg in enumerate(directions):
            x = line*np.sin(deg)+self.center[0]
            y = line*np.cos(deg)+self.center[1]
            lines[i] = np.array([x, y]).T
        return lines

    def circular_directions(self, density=360):
        segments = np.linspace(0, 2*np.pi, density, endpoint=False)
        return segments

    # ==== Light Stuff v3 =======================================
    def lights_v3(self):
        outer_edges = self.end_of_map_edes()
        vertices = self.edges_to_vertices(outer_edges)
        beams = self.beams_origin_to_vertices(vertices)
        return beams

    def end_of_map_edes(self):
        max_dims = self.grid_ref.max_dims
        outer_edges = []
        for x in range(max_dims[0]-1):
            outer_edges.append([x, 0, x+1, 0])
            outer_edges.append([x, max_dims[1], x+1, max_dims[1]])
        for y in range(max_dims[1]-1):
            outer_edges.append([0, y, 0, y+1])
            outer_edges.append([max_dims[0], y, max_dims[0], y+1])
        return np.array(outer_edges)

    def triangles_to_surfaces(self):
        surfaces = self.grid_ref.wall_surfaces
        closest = self.sort_edges_by_closest(surfaces)
        # edges = closest
        lit = self.lit_edges(closest)
        # lit_v = lit.reshape((len(lit)*2, 2))
        # vertices = edges.reshape((len(edges)*2, 2))
        return self.triangles_origin_to_edges(lit)

    def beams_to_surfaces(self):
        # get surfaces
        surfaces = self.grid_ref.wall_surfaces
        closest = self.sort_edges_by_closest(surfaces)
        # edges = closest
        lit = self.lit_edges(closest)
        lit_v = lit.reshape((len(lit)*2, 2))
        # vertices = edges.reshape((len(edges)*2, 2))
        return self.beams_origin_to_vertices(lit_v)
    
    def edge_cleaner(self, surfaces):
        closest = self.sort_edges_by_closest(surfaces)
        pass

    # ==== Light Stuff v2 =======================================
    def all_objects_from_grid(self):
        return self.grid_ref.layers[0] + self.grid_ref.layers[1]
        

    def expanding_scope(self):
        max_x, max_y = self.grid_ref.max_dims
        for i in range(1, max(max_x, max_y), 10):
            xp = min(self.xy[0]+i, max_x)
            yp = min(self.xy[0]+i, max_y)
            xm = max(0, self.xy[0]-i)
            ym = max(0, self.xy[0]-i)

            # print("-----")
            # for x in range(xm, xp):
            #     for y in range(ym, yp):
            #         print(x, y)
            # if i == 5:
            #     break

    def lights_v2(self):
        self.center = self.xy + [0.5, 0.5]
        t0 = time.time()
        object_grid = self.all_objects_from_grid()
        t1 = time.time()
        object_anchors = np.transpose(np.nonzero(object_grid))
        t2 = time.time()
        edges_by_anchor = self.anchors_to_edgelists(object_anchors)
        t3 = time.time()
        all_edges = edges_by_anchor.reshape((len(edges_by_anchor)*4, 4))
        closest = self.sort_edges_by_closest(all_edges)
        t4 = time.time()
        lit = self.lit_edges(closest)
        lit_v = lit.reshape((len(lit)*2, 2))
        t5 = time.time()
        beams = self.beams_origin_to_vertices(lit_v)
        t6 = time.time()
        print("=======================")
        print(f"all_objects_from_grid time: {t1-t0}") 
        print(f"object_anchors time: {t2-t1}") 
        print(f"anchors_to_edgelists time: {t3-t2}") 
        print(f"sort_edges_by_closest time: {t4-t3}") 
        print(f"lit_edges time: {t5-t4}") 
        print(f"beams_origin_to_vertices time: {t6-t5}") 
        return beams

    def sort_edges_by_closest(self, all_edges):
        dist_list = self.edge_distances(self.center, all_edges)
        closest_idx = np.argsort(dist_list.min(1))
        return all_edges[closest_idx]

    def edge_to_angle_segment(self, edge):
        points = edge.reshape(2,2).T
        rads = np.arctan2(points[0]-self.center[0], points[1]-self.center[1])
        full_rads = rads + (rads<0)*2*np.pi
        arc = np.sort(full_rads)
        return arc
    
    def lit_edges(self, closest_edges):
        shift = 0
        # this shit takes AGES...
        # like up 0.2s per go...
        # that's like 5fps m8
        all_segments = []
        edge_idx = []
        for i, edge in enumerate(closest_edges):
            new_seg = self.edge_to_angle_segment(edge)
            if (new_seg[1] - new_seg[0]) > np.pi:
                new_seg = np.flip(new_seg)
            lower = True
            upper = True
            for seg in all_segments:
                if seg[0]-shift < new_seg[0] < seg[1]+shift:
                    lower = False
                if seg[0]-shift < new_seg[1] < seg[1]+shift:
                    upper = False
            if lower or upper:
                all_segments.append(new_seg)
                edge_idx.append(i)
        # all_segments = np.array(all_segments)
        return closest_edges[edge_idx]

    def segments_circle_asf_ASdf_Asdf(self):
        pass

    # ==== LIGHT STUFF v1 =======================================
    def lights_v1(self, origin, obj_anchors):
        edges_by_anchor = self.anchors_to_edgelists(obj_anchors)
        print(f"all edges: {len(edges_by_anchor)*4}")
        all_light_edges = []
        all_ext_light_edges = []
        for sq in edges_by_anchor:
            light_edges = self.remove_shadow_edges(origin, sq)
            # debug
            for edge1 in light_edges:
                all_light_edges.append(edge1)
            ext_light_edges = self.rm_inside_edges(light_edges)
            for edge in ext_light_edges:
                all_ext_light_edges.append(edge)
        all_ext_light_edges = np.array(all_ext_light_edges)
        print(f"light edges: {len(all_light_edges)}")
        print(f"ext light edges: {len(all_ext_light_edges)}")
        return all_ext_light_edges.reshape((len(all_ext_light_edges)*2, 2))

    def anchors_to_edgelists(self, anchors):
        """ edges must be done like this to be able to remove duplicates
        [0, 0, 0, 1] ^
        [0, 1, 1, 1] ->
        [1, 0, 1, 1] ^
        [0, 0, 1, 0] ->
        """
        edge_by_anchor = np.zeros((len(anchors), 4, 4))
        for i, a in enumerate(anchors):
            edge_by_anchor[i] = np.array([
                [a[0],   a[1],   a[0],   a[1]+1],
                [a[0],   a[1]+1, a[0]+1, a[1]+1],
                [a[0]+1, a[1],   a[0]+1, a[1]+1],
                [a[0],   a[1],   a[0]+1, a[1]]])
        return edge_by_anchor

    def edge_distances(self, origin, edges):
        edge_dists = np.zeros((len(edges), 2))
        for i, edge in enumerate(edges):
            edge_dists[i] = [self.distance(origin, edge[:2]),
                            self.distance(origin, edge[2:])]
        return edge_dists


    def remove_shadow_edges(self, origin, edges):
        edge_dists = self.edge_distances(origin, edges)
        remove_idx = [True for x in edge_dists]
        maxs = edge_dists.max(1)
        mins = edge_dists.min(1)
        for vmin in mins:
            for i, vmax in enumerate(maxs):
                if vmin >= vmax:
                    remove_idx[i] = False
        # # debug
        # print(remove_idx)
        # print(edge_dists[remove_idx])
        light_edges = edges[remove_idx]
        return light_edges


    def rm_inside_edges(self, all_edges):
        uniq, counts = np.unique(all_edges, return_counts=True, axis=0)
        repeat_idx = np.nonzero(counts-1)[0]
        external_only = np.delete(uniq, repeat_idx, axis=0)
        return external_only

    def distance(self, point1, point2):
        return np.hypot((point2[1]-point1[1]), (point2[0]-point1[0]))


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
