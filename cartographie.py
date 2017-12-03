import numpy as np
import matplotlib.pyplot as pl
import geometry

R_TERRE = 6371000
LAT_MOY = 46
L = LAT_MOY * (np.pi/180)

LONG_TO_X = R_TERRE * np.cos(L) * (np.pi / 180)
LAT_TO_Y = R_TERRE * (np.pi / 180)

def coord_plan(long, lat):
    x = long * LONG_TO_X
    y = lat * LAT_TO_Y
    return geometry.Point(x, y)

def coords_dict(file):
    dict = {}
    with open(file, "r") as f:
        for line in f :
            l = line.strip().split()
            long, lat = float(l[-2]), float(l[-1])
            dict[l[1]] = coord_plan(long, lat)
    return dict

if __name__ == "__main__":
    d = coords_dict("Données/aerodrome.txt")
    print(len(d))
    for elt in d:
        point = d[elt]
        pl.plot(point.x, point.y,'+')
    pl.show()