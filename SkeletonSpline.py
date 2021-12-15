from scipy import interpolate
from SkeletonPoint import SkeletonPoint
import numpy as np

class SkeletonSpline(object):

    def __init__(self, spline_func):
        self.__spline_tck = spline_func[0]
        self.__connection_marker_start_point = []
        self.__connection_marker_end_point = []

    def get_end_connection_marker(self):
        return self.__connection_marker_end_point

    def get_start_connection_marker(self):
        return self.__connection_marker_start_point

    def set_start_connection_marker(self, marker):
        self.__connection_marker_start_point = marker

    def set_end_connection_marker(self, marker):
        self.__connection_marker_end_point = marker

    def __str__(self):
        return "Start point {}, End Point {}, Length of Spline {} ".format(
            self.get_start_point(),
            self.get_end_point(),
            self.get_spline_length())

    def get_spline_function(self):
        return self.__spline_tck

    def set_spline_function(self, tck):
        self.__spline_tck = tck


    def get_x_y_z(self, interp_points=1000):
        u_fine = np.linspace(0, 1, interp_points)
        [x, y, z] = interpolate.splev(u_fine, self.__spline_tck)
        return [x, y, z]

    def get_start_point(self):
        tck = self.__spline_tck
        x = tck[1][0][0]
        y = tck[1][1][0]
        z = tck[1][2][0]
        return SkeletonPoint(x,y,z)

    def get_end_point(self):
        tck = self.__spline_tck
        x = tck[1][0][-1]
        y = tck[1][1][-1]
        z = tck[1][2][-1]
        return SkeletonPoint(x,y,z)

    def get_normal_start_vectors(self):
        tck = self.__spline_tck
        x = tck[1][0]
        y = tck[1][1]
        z = tck[1][2]
        n = tck[2]

        n_x1 = n * (x[0] - x[1])
        n_y1 = n * (y[0] - y[1])
        n_z1 = n * (z[0] - z[1])

        norm = np.sqrt(n_x1**2 + n_y1**2 + n_z1**2)
        norm_vec = 1.0 / norm * np.array([n_x1, n_y1, n_z1])
        return norm_vec

    def get_normal_end_vectors(self):
        tck = self.__spline_tck
        x = tck[1][0]
        y = tck[1][1]
        z = tck[1][2]
        n = tck[2]

        n_x1 = n * (x[-1] - x[-2])
        n_y1 = n * (y[-1] - y[-2])
        n_z1 = n * (z[-1] - z[-2])

        norm = np.sqrt(n_x1 ** 2 + n_y1 ** 2 + n_z1 ** 2)
        norm_vec = 1.0 / norm * np.array([n_x1, n_y1, n_z1])
        return norm_vec


    def get_spline_length(self):
        [x,y,z] = self.get_x_y_z()
        length = 0.0
        for ii in range(len(x)):
            if ii == len(x) - 1:
                continue
            delta_x = x[ii] - x[ii + 1]
            delta_y = y[ii] - y[ii + 1]
            delta_z = z[ii] - z[ii + 1]
            length += np.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        return length








