from shapely.geometry import Polygon
import numpy as np
from trimesh import transformations


class CrossSection(object):


    def __init__(self, xy_transfomration):
        self.__vertices = xy_transfomration[0]
        self.__to_3D = xy_transfomration[1]

        cross_section = transformations.transform_points(self.__vertices, self.__to_3D)
        cross_section = [cross_section[:, 0], cross_section[:, 1], cross_section[:, 2]]

        self.__x = cross_section[0]
        self.__y = cross_section[1]
        self.__z = cross_section[2]

    def get_xy(self):
        return self.__vertices

    def get_to_3D(self):
        return self.__to_3D

    def get_to_2D(self):
        return np.linalg.inv(self.__to_3D)

    def get_xyz(self):
        return self.__x.tolist(), self.__y.tolist(), self.__z.tolist()

    def set_xyz(self, x, y, z):
        self.__x = x
        self.__y = y
        self.__z = z

    def get_3D_center_points(self):
        xc = self.get_center_points()[0]
        yc = self.get_center_points()[1]
        points = transformations.transform_points([[xc, yc, 0]], self.__to_3D)
        return points[0]

    def get_length(self):
        length = 0.0
        for ii in range(len(self.__x)):
            length += np.sqrt((self.__x[ii - 1] - self.__x[ii])**2 + (self.__y[ii - 1] - self.__y[ii])**2 + (self.__z[ii - 1] - self.__z[ii])**2)
        return length

    def get_center_points(self):
        points = self.__vertices
        poly = Polygon(points)
        point = poly.centroid
        xc = point.xy[0][0]
        yc = point.xy[1][0]
        return (xc, yc)

    def get_area(self):
        points = self.__vertices
        poly = Polygon(points)
        return poly.area

    def get_second_moments(self):
        xc, yc = self.get_center_points()
        x = []
        y = []
        for vertex in self.__vertices:
            x.append(vertex[0])
            y.append(vertex[1])

        Ix, Iy, Ixy = 0, 0, 0
        for i in range(len(x)):
            x1, y1 = x[i - 1], y[i - 1]
            x2, y2 = x[i], y[i]
            x1 -= xc
            x2 -= xc
            y1 -= yc
            y2 -= yc
            v = x1 * y2 - x2 * y1
            Ix += v * (y1 * y1 + y1 * y2 + y2 * y2)
            Iy += v * (x1 * x1 + x1 * x2 + x2 * x2)
            Ixy += v * (x1 * y2 + 2 * x1 * y1 + 2 * x2 * y2 + x2 * y1)
        Ix /= 12
        Iy /= 12
        Ixy /= 24
        return (Ix, Iy, Ixy)