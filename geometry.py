"""Geometry classes and utilities."""
from numpy import arccos


class Point(object):
    """Meters coordinates, with attributes x, y: int"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "({0.x}, {0.y})".format(self)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __rmul__(self, k):
        return Point(k * self.x, k * self.y)

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def distance(self, other):
        return abs(self - other)

    def seg_dist(self, a, b):
        ab, ap, bp = b - a, self - a, self - b
        if ab.sca(ap) <= 0:
            return abs(ap)
        elif ab.sca(bp) >= 0:
            return abs(bp)
        else:
            return abs(ab.det(ap)) / abs(ap)


class Vect():
    def __init__(self, u, v):
        self.u = u
        self.v = v

    def __repr__(self):
        return "({0.x}, {0.y})".format(self)

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
        return arccos(self.sca(other) / (abs(self) * abs(other)))
