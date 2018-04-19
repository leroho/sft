import geometry
from numpy import cos, sin, pi

def in_square(A, B, coord):
    return(min(A.long, B.long) <= coord.long <= max(A.long, B.long) and min(A.lat, B.lat) <= coord.lat <= max(A.lat, B.lat))

def windGlobal2(A, B, windPlan):
    vectGlobal = geometry.Vect(0, 0)
    k = 0
    l = []
    for (elt, wind) in windPlan.dict.items():
        coord = wind.coord
        if in_square(A, B, coord):
            k += 1
            vectGlobal += wind.vect
        else :
            l.append(wind)
    return vectGlobal.__rmul__(1/k) if k != 0 else min(l, key=lambda wind:abs(wind.coord.__sub__(A))).vect

def windGlobal(a, b, windplan):
    k1 = int(min(a.long, b.long)/0.5)
    k2 = int(max(a.long, b.long)/0.5) + 1
    vent = geometry.Vect(0,0)
    n=0
    for i in range(k1, k2+1):
        x = i*0.5
        y = ((b.lat - a.lat)/(b.long - a.long))*(x - a.long) + a.lat
        try :
            vent += (windplan.dict[(x, int(y/0.5)*0.5)].vect)
            n+=1
        except KeyError:
            pass
        try:
            vent += (windplan.dict[(x, int(y/0.5 + 1)*0.5)].vect)
            n+=1
        except KeyError:
            pass
    if n ==0 :
        k1 = int(min(a.lat, b.lat) / 0.5)
        k2 = int(max(a.lat, b.lat) / 0.5) + 1
        vent = geometry.Vect(0, 0)
        n = 0
        for i in range(k1, k2 + 1):
            y = i * 0.5
            x = ((b.long - a.long) / (b.lat - a.lat)) * (y - a.lat) + a.long
            try:
                vent += (windplan.dict[(int(x / 0.5) * 0.5), y].vect)
                n += 1
            except KeyError:
                pass
            try:
                vent += (windplan.dict[(int(x / 0.5 + 1) * 0.5, x)].vect)
                n += 1
            except KeyError:
                pass
    return vent.__rmul__(1/n)

class Airplane():

    def __init__(self, alt_inf, alt_sup, X, vitesse_croisière):
        self.alt_inf = alt_inf
        self.alt_sup = alt_sup
        self.v_c = vitesse_croisière
        self.X = X

    def fligth(self, dep_coord, arr_coord, windPlan):
        windvect = windGlobal(dep_coord, arr_coord, windPlan)
        ab_vect = geometry.Vect((arr_coord - dep_coord).x, (arr_coord - dep_coord).y)
        angle_au_vent = ab_vect.angle(windvect)
        vent_effectif = abs(windvect) * cos(angle_au_vent)
        derive = (60 / self.v_c) * abs(windvect) * sin(angle_au_vent) * (pi / 180)
        groundSpeed = vent_effectif + self.v_c * cos(derive)
        duration = abs(ab_vect) / groundSpeed
        normal_duration = abs(ab_vect)/self.v_c
        return normal_duration, duration