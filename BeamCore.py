from trimesh import transformations
from scipy import interpolate
from Point import ChainPoint
import numpy as np
import trimesh
from shapely.geometry import Point
from MeshToVoxelModelFitter import MeshToVoxelFitter
from trimesh.exchange.load import load_path

class BeamCore(object):

    def __init__(self, origin_mesh_path, cross_section_stl_path):
        self._triangle_mesh = trimesh.load_mesh(origin_mesh_path)
        self._triangle_mesh_cross = trimesh.load_mesh(cross_section_stl_path)
        self.__is_watertight = self._triangle_mesh_cross.is_watertight

    def fit_mesh(self, size, splines):
        mesh_fitter = MeshToVoxelFitter(self._triangle_mesh)
        return mesh_fitter.fit_voxel_model_into_mesh(size, splines)

    def slice_mesh(self, point, normal_vec, point2, normal_vec2):
        self._triangle_mesh_cross.slice_mesh_plane()

    def __get_closed_polygon_consisting_origin(self, origin_2D, polygons):
        polygons_containing_origin = []
        for polygon in polygons:
            if polygon == None:
                continue
            polygon = polygon.simplify(0.05, preserve_topology=True)
            red_polygon_len = len(polygon.exterior.xy[0])
            print(f'Reduced Cross Section from {len(polygon.exterior.xy[0])} to {red_polygon_len}')
            # Check if point is in polygon --> Choose the right cross section
            if polygon.contains(origin_2D):
                polygons_containing_origin.extend([list(polygon.exterior.coords)])
        return polygons_containing_origin

    def __get_open_polygons(self, section_2D):
        # 1. Build up dictionary which counts the number of cross sections
        dict_point = {}
        for p1, p2 in section_2D.vertex_nodes:
            dict_point[p1] = []
            dict_point[p2] = []

        for p1, p2 in section_2D.vertex_nodes:
            dict_point[p1].append(p2)
            dict_point[p2].append(p1)
        one_conn_keys = []
        for key, value in dict_point.items():
            if len(value) == 1: one_conn_keys.append(key)

        print(f'[i] Open Polygons are found {int(len(one_conn_keys) / 2)}')
        current_chains = []
        one_keys_used = []
        for one_conn_key in one_conn_keys:
            if one_conn_key in one_keys_used: continue
            # Start with one key
            not_end_is_reached = True
            current_key = one_conn_key
            current_chain = []
            next_key = -1
            start_key = True
            key_before = -1
            while not_end_is_reached:
                current_chain.append(current_key)
                if len(dict_point[current_key]) == 1 and start_key:
                    start_key = False
                    one_keys_used.append(current_key)
                    key_before = current_key
                    next_key = dict_point[current_key][0]
                if len(dict_point[current_key]) == 2:
                    p1, p2 = dict_point[current_key]
                    if p1 == key_before:
                        key_before = current_key
                        next_key = p2
                    else:
                        key_before = current_key
                        next_key = p1
                current_key = next_key
                if len(dict_point[current_key]) == 1 and not start_key:
                    not_end_is_reached = False
                    one_keys_used.append(current_key)
                    current_chain.append(current_key)
                if len(dict_point[current_key]) > 2 and not start_key:
                    not_end_is_reached = False
                    print('[i] to much connections of one point')
            current_chains.append(current_chain)
        if len(current_chains) == int(len(one_conn_keys) / 2):
            print('[i] Equal number of open polygons according to open points')
        # Genearte polygon representation
        polygons = []
        for chain in current_chains:
            polygon = []
            for point_id in chain:
                polygon.append(tuple(section_2D.vertices[point_id]))
            polygons.append(polygon)
        return polygons

    def __get_closest_polygon_to_point(self, polygons, origin):
        polygon_min_distances_origin = []
        for polygon_id, polygon in enumerate(polygons):
            point_distance = []
            for point in polygon:
                point_distance.append(origin.distance(Point(point[0], point[1])))
            polygon_min_distances_origin.append(min(point_distance))
        print(polygon_min_distances_origin)
        return polygons[np.argmin(polygon_min_distances_origin)]


    def find_cross_section(self, point, normal_vec):
        origin = point
        lines, face_index = trimesh.intersections.mesh_plane(self._triangle_mesh_cross, plane_origin=origin,
                                                             plane_normal=normal_vec,
                                                             return_faces=True)
        # if the section didn't hit the mesh return None
        if len(lines) == 0: return None
        path = load_path(lines)
        path.metadata['face_index'] = face_index
        section = path
        if section != None:
            polygon_cross_candidate = []
            # Convert the 3D defined polygon and origin into 2D Space
            section_2D, to_3D = section.to_planar()
            to_2D = np.linalg.inv(to_3D)
            origin_2D = transformations.transform_points([origin], to_2D)
            origin_2D = Point(origin_2D[0][0], origin_2D[0][1])

            # 1. Search for polygons in 3D and 2D
            polygons = section_2D.polygons_closed
            if self.__is_watertight:
                polygon_cross_candidate.extend(self.__get_closed_polygon_consisting_origin(origin_2D, polygons))
            else:
                polygon_cross_candidate.extend(self.__get_open_polygons(section_2D))
                for polygon in polygons:
                    if polygon != None:
                        polygon_cross_candidate.extend([list(polygon.exterior.coords)])
            print(f'[i] Polygon candidates are found {len(polygon_cross_candidate)}')

            # 2. Find the closest polygon which is valid
            if len(polygon_cross_candidate) == 0:
                return None
            polygon = self.__get_closest_polygon_to_point(polygon_cross_candidate, origin_2D)
            cross_section_vertices = []
            for point in polygon:
                cross_section_vertices.append([point[0], point[1], 0])
            cross_section = [cross_section_vertices, to_3D]
            return cross_section
        return None

    def get_interpolation_function(self, chain, interp_degree):
        x, y, z = [], [], []
        for point in chain.points:
            point = ChainPoint(**point)
            x.append(point.x)
            y.append(point.y)
            z.append(point.z)

        c1 = ChainPoint(**chain.points[0])
        c2 = ChainPoint(**chain.points[-1])

        try:
            if len(x) >= interp_degree:
                tck, u = interpolate.splprep([x, y, z], k=interp_degree)

                # End point Cut positions as t value
                # Push to end and start point
                #if chain.end_connection_id != None:
                u_fine = np.linspace(0, 1, 100)
                [x_coordinates, y_coordinates, z_coordinates] = interpolate.splev(u_fine, tck)
                return [tck, u], [0,1]
            else:
                tck, u = interpolate.splprep([x, y, z], k=len(x))

                u_fine = np.linspace(0, 1, 100)
                [x_coordinates, y_coordinates, z_coordinates] = interpolate.splev(u_fine, tck)
                return [tck, u], [0,1]
        except:
            return [None, None], [0,1]


    def get_interpolation_function_xyz(self, x, y, z, interp_degree):
        try:
            if len(x) >= interp_degree:
                tck, u = interpolate.splprep([x, y, z], k=interp_degree)
                return [tck, u]
            else:
                tck, u = interpolate.splprep([x, y, z], k=len(x))
                return [tck, u]
        except:
            return None, None




