import numpy as np
import matplotlib.pyplot as pl

R_TERRE = 6371
LAT_MOY = 46

def long_to_x():
    L = LAT_MOY * (np.pi/180)
    return R_TERRE * np.cos(L)*  (np.pi/180)

def lat_to_y():
    return R_TERRE * (np.pi/180)

def coord(long, lat):
    x = long * long_to_x()
    y = lat * lat_to_y()
    return np.array([x, y])

def coords(file):
    dict = {}
    with open(file, "r") as f:
        for line in f :
            l = line.strip().split()
            long, lat = float(l[-2]), float(l[-1])
            dict[l[1]] = coord(long, lat)
    return dict

if __name__ == "__main__":
    d = coords("Données/aerodrome.txt")
    print(len(d))
    for elt in d:
        x, y = d[elt]
        pl.plot(x,y,'+g')

    pl.show()

