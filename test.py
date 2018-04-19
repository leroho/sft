import geometry
import numpy

a = geometry.Point(1,5)
b = geometry.Point(3,6)
d = {1:a, 2:b}
d[1] = b

print(a)