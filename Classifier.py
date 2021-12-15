from Module import Module
from Point import Point
import numpy as np
class Classifier(Module):
    def __init__(self, delete_voxel_in_radius_around_branch_point=1.0, minimum_number_of_voxels_along_spline=3,
                 delete_number_of_voxel_around_branch_point = 1, minimum_voxel_branch_length=2):
        super().__init__()
        self.__delete_voxel_in_radius_around_branch_point = delete_voxel_in_radius_around_branch_point
        self.__delete_number_of_voxel_around_branch_point = delete_number_of_voxel_around_branch_point
        self.__minimum_number_of_voxels_along_spline = minimum_number_of_voxels_along_spline
        self.__minimum_voxel_branch_length = minimum_voxel_branch_length
        self.__connection_index_tree = {}

    def run(self, skeleton, boundary_distance, size, no_design_space, voxel_model):
        self._build_up_connection_tree(skeleton, boundary_distance)
        #if self.__delete_number_of_voxel_around_branch_point != 0:
        if self.__delete_voxel_in_radius_around_branch_point != 0 or self.__delete_number_of_voxel_around_branch_point != 0:
            self._decompose_skeleton_on_branch_points()

        json_dict = []
        for point in self.__connection_index_tree.values():
            json_dict.append(point._asdict())
        return {'classified_skeleton': json_dict, 'size': size}

    def _decompose_skeleton_on_branch_points(self):
        #Search for all branch points
        branch_points = []
        for point_key in self.__connection_index_tree:
            point = self.__connection_index_tree[point_key]
            if len(point.connection_marker) >= 3:
                branch_points.append((point.x, point.y, point.z))

        # Go through all branch points
        branch_point_dict = {}
        for branch_point_key in branch_points:
            # Store these branch point informations
            points_to_delete = set()
            points_to_mark = set()
            point = self.__connection_index_tree[branch_point_key]
            points_to_check = []
            points_to_check.append(point)
            used_connections = []
            # Search until all connected are found
            while(len(points_to_check) != 0):
                point_to_check = points_to_check.pop()
                dist_p_check = (point.x - point_to_check.x)** 2 + (point.y - point_to_check.y) ** 2 + (point.z - point_to_check.z) ** 2

                dx = abs(point.x - point_to_check.x)
                dy = abs(point.y - point_to_check.y)
                dz = abs(point.z - point_to_check.z)

                is_in_k_neighbourhood = False
                if (dx <= self.__delete_number_of_voxel_around_branch_point and
                    dy <= self.__delete_number_of_voxel_around_branch_point and
                    dz <= self.__delete_number_of_voxel_around_branch_point):
                    is_in_k_neighbourhood = True

                # If the point is in range
                if dist_p_check < self.__delete_voxel_in_radius_around_branch_point * point.boundary_distance ** 2 or is_in_k_neighbourhood:
                    points_to_delete.add((point_to_check.x, point_to_check.y, point_to_check.z))
                    # Search new connection and check if that point was not already used
                    new_connections = point_to_check.connection_marker
                    for connection in new_connections:
                        if not connection in used_connections:
                            points_to_check.append(self.__connection_index_tree[(connection[0], connection[1], connection[2])])
                            used_connections.append(connection)
                else:
                    points_to_mark.add((point_to_check.x, point_to_check.y, point_to_check.z))
            branch_point_dict[branch_point_key] = (points_to_delete, points_to_mark)

        # Combine regions for deletion
        intersected_regions = {}
        for branch_point_key in branch_point_dict:
            intersected_regions[branch_point_key] = set()
            points_to_delete, points_to_mark = branch_point_dict[branch_point_key]
            for branch_point_key2 in branch_point_dict:
                points_to_delete2, points_to_mark2 = branch_point_dict[branch_point_key2]
                delete_points = points_to_delete.intersection(points_to_delete2)
                if len(delete_points) != 0:
                    intersected_regions[branch_point_key].add(branch_point_key2)
        change = True
        only_interseced_regions = intersected_regions
        while (change):
            keys_to_skip = []
            for key in only_interseced_regions:
                if key in keys_to_skip:
                    continue
                values = only_interseced_regions[key]
                for key2 in only_interseced_regions:
                    if key != key2:
                        values2 = only_interseced_regions[key2]
                        if len(values.intersection(values2)) != 0:
                            for val in values2:
                                only_interseced_regions[key].add(val)
                            keys_to_skip.append(key2)
            if len(keys_to_skip) != 0:
                for key2 in keys_to_skip:
                    try:
                        only_interseced_regions.pop(key2)
                    except:
                        pass
                change = True
            else:
                change = False
        #marker = 0
        for key in only_interseced_regions:
            marker = key
            branch_keys = only_interseced_regions[key]
            points_to_delete, points_to_mark = branch_point_dict[key]
            for key2 in branch_keys:
                points_to_delete2, points_to_mark2 = branch_point_dict[key2]
                for point in points_to_delete2:
                    points_to_delete.add(point)

                for point in points_to_mark2:
                    points_to_mark.add(point)
            # Mark the point and delete old connections
            for point in points_to_mark:
                try:
                    point = self.__connection_index_tree[point]
                    connections = point.connection_marker
                    for con in connections:
                        con_tup = tuple(con)
                        if con_tup in points_to_delete:
                            point.connection_marker.remove(con)
                    point.branch_marker.append(marker)
                except:
                    pass
            # Delete the connection from the tree
            for point in points_to_delete:
                self.__connection_index_tree.pop(point)


    def _build_up_connection_tree(self, voxel_skeleton, boundary_distance):
        self.__connection_index_tree = {}

        # Check for connections along the skeleton points
        voxel_skeleton = np.array(voxel_skeleton).astype(int)
        for p_index, point_coordinates in enumerate(voxel_skeleton):
            xx, yy, zz = point_coordinates.tolist()
            self.__connection_index_tree[xx, yy, zz] = []

            x_conection = np.abs(voxel_skeleton[:, 0] - xx * np.ones(len(voxel_skeleton[:, 0])).astype(int))
            y_conection = np.abs(voxel_skeleton[:, 1] - yy * np.ones(len(voxel_skeleton[:, 1])).astype(int))
            z_conection = np.abs(voxel_skeleton[:, 2] - zz * np.ones(len(voxel_skeleton[:, 2])).astype(int))
            xy_dist = np.logical_and(x_conection <= 1, y_conection <= 1).astype(int)
            xyz_dist = np.logical_and(xy_dist, z_conection <= 1).astype(int)
            indexes = np.argwhere(xyz_dist == True)

            # Add connection
            point_connections = []
            for index in indexes[:, 0]:
                point_connections.append(tuple(voxel_skeleton[index].tolist()))
            point_connections.remove((xx, yy, zz))

            # Save Connection tree index
            self.__connection_index_tree[xx, yy, zz] = Point(xx, yy, zz,
                                                             boundary_distance=boundary_distance[p_index],
                                                             connection_marker=point_connections, branch_marker=[])

