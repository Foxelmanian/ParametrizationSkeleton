from typing import List
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y', 'z', 'boundary_distance', 'connection_marker', 'branch_marker'])
ChainPoint = namedtuple('Point', ['x', 'y', 'z', 'boundary_distance'])


def points_to_coordinates(points: List[Point]):
    x = []
    y = []
    z = []
    for point in points:
        x.append(point.x)
        y.append(point.y)
        z.append(point.z)
    return x, y, z

