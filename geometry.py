"""Geometry classes and utilities."""
from numpy import arccos, cos, pi

class Point(object):
    """Meters coordinates, with attributes long, y: int"""

    def __init__(self, longitude, latitude):
        self.long = longitude
        self.lat = latitude
        self.lat_moy = 46*(pi/180)
        self.rayon_terrestre = 6371000
        self.long_to_x = self.rayon_terrestre * cos(self.lat_moy) * (pi / 180)
        self.lat_to_y = self.rayon_terrestre * (pi / 180)
        self.x = self.long * self.long_to_x
        self.y = self.lat * self.lat_to_y

    def __repr__(self):
        return "({0.long}, {0.lat})".format(self)

    def __eq__(self, other):
        return self.long == other.long and self.lat == other.lat

    def __sub__(self, other):
        return Point(self.long - other.long, self.lat - other.lat)

    def __add__(self, other):
        return Point(self.long + other.long, self.lat + other.lat)

    def __rmul__(self, k):
        return Point(k * self.long, k * self.lat)

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def distance(self, other):
        return abs(self - other)

class Vect():
    def __init__(self, u, v):
        self.u = u
        self.v = v

    def __repr__(self):
        return "({0.u}, {0.v})".format(self)

    def __eq__(self, other):
        return self.u == other.u and self.v == other.v

    def __sub__(self, other):
        return Vect(self.u - other.u, self.v - other.v)

    def __add__(self, other):
        return Vect(self.u + other.u, self.v + other.v)

    def __rmul__(self, k):
        return Vect(k * self.u, k * self.v)

    def __abs__(self):
        return (self.u ** 2 + self.v ** 2) ** 0.5

    def sca(self, other):
        """sca(Point) return float
        returns the scalar product between self and other"""
        return self.u * other.u + self.v * other.v

    def det(self, other):
        """det(Vect) return float
        returns the determinant between self and other"""
        return self.u * other.v - self.v * other.u

    def angle(self, other):
        return arccos(self.sca(other)/(abs(self)*abs(other)))

def from_file(file):
    dict = {}
    with open(file, "r") as f:
        for line in f :
            l = line.strip().split()
            long, lat = float(l[-2]), float(l[-1])
            dict[l[1]] = Point(long, lat)
    return dict