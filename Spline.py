from collections import namedtuple

Spline = namedtuple('Spline', ['t', 'x', 'y', 'z', 'degree', 'start_connection_id', 'end_connection_id'])