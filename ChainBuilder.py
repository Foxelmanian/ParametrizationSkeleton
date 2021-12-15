from Module import Module
from Point import Point, ChainPoint
from Chain import Chain

import numpy as np

class ChainBuilder(Module):

    def __init__(self, minimum_number_of_voxels_in_a_chain=1):
        super().__init__()
        self.__points = {} # All points

        self.__one_connection_points = {} # Start and End points
        self.__minimum_number_of_voxels_in_a_chain = minimum_number_of_voxels_in_a_chain
        self.__two_connection_points = {}
        self.__branch_connection_points = {}
        self.__connection_keys = {}

    def run(self, classified_skeleton, size, voxel_model):
        # Search for end points and save points
        #print(classified_skeleton)

        once = True
        for point in classified_skeleton:
            point = Point(**point)
            self.__points[(point.x, point.y, point.z)] = point
            if len(point.connection_marker) == 1:
                self.__one_connection_points[(point.x, point.y, point.z)] = point
                self.__connection_keys[((point.x, point.y, point.z), (point.x, point.y, point.z))] = point

            if len(point.connection_marker) == 2:
                self.__two_connection_points[(point.x, point.y, point.z)] = point

            if len(point.connection_marker) > 2:
                for connection_marker in point.connection_marker:
                    self.__connection_keys[(point.x, point.y, point.z), (connection_marker[0], connection_marker[1],connection_marker[2])] = point
                print(point.connection_marker)

        chains = self.__get_chains() # Searches in the classsified_skeleton for chains
        json_dict = []
        for chain in chains:
            point_dict = []
            for point in chain.points:
                point_dict.append(point._asdict())
            json_dict.append({'points': point_dict,
                              'start_connection_id': chain.start_connection_id,
                              'end_connection_id': chain.end_connection_id})
        return {'chains': json_dict, 'size': size}


    def __get_chains(self):
        # Build up point chains
        # Build up point chains
        chains = []
        checked_keys = []

        for key, start_point in self.__one_connection_points.items():
            # Ignore already used points
            if key in checked_keys: continue
            checked_keys.append(key)
            start_con_id = start_point.branch_marker
            points_of_chain = []
            current_point = start_point
            end_of_chain_is_not_reached = True
            while end_of_chain_is_not_reached:
                points_of_chain.append(ChainPoint(x=current_point.x,
                                                  y=current_point.y,
                                                  z=current_point.z,
                                                  boundary_distance=current_point.boundary_distance))
                next_point_keys = current_point.connection_marker
                if len(next_point_keys) == 0:
                    end_of_chain_is_not_reached = False
                elif len(next_point_keys) == 1:
                    try:
                        next_point = self.__points[tuple(next_point_keys[0])]
                    except:
                        print('[-] Connection is not found but was already marked')
                        end_of_chain_is_not_reached = False
                    try:
                        next_point.connection_marker.remove([current_point.x, current_point.y, current_point.z])
                    except:
                        print('[-] Current point Was already removed')
                    current_point = next_point
                else:
                    end_of_chain_is_not_reached = False
                    print('More than one Connection are found something is wrong')
            end_con_id = current_point.branch_marker
            checked_keys.append((current_point.x, current_point.y, current_point.z))
            if len(start_con_id) == 0:
                start_con_id = None
            else:
                start_con_id = start_con_id[0]
            if len(end_con_id) == 0:
                end_con_id = None
            else:
                end_con_id = end_con_id[0]
            chains.append(Chain(points_of_chain, start_con_id, end_con_id))
        return chains







