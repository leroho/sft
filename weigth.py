import cartographie
import wind
import geometry
from numpy import cos, sin, pi

VITESSE_CROISIERE = 200

def in_square(A, B, coord):
    return(min(A.x, B.x) <= coord.x <= max(A.x, B.x) and min(A.y, B.y) <= coord.y <= max(A.y, B.y))

def windGlobal(A, B, windPlan):
    vectGlobal = geometry.Vect(0, 0)
    k = 0
    l = []
    for (elt, wind) in windPlan.dict.items():
        coord_plan = wind.coord_plan
        if in_square(A, B, coord_plan):
            k += 1
            vectGlobal += wind.vect
        else :
            l.append(wind)
    return vectGlobal.__rmul__(1/k) if k != 0 else min(l, key=lambda wind:abs(wind.coord_plan.__sub__(A))).vect

def duration_calcul(A, B, windPlan, n):
    duration = 0
    for k in range(n):
        a = A + (B.__sub__(A)).__rmul__(k/n)
        b = A + (B.__sub__(A)).__rmul__((k + 1)/n)
        windvect = windGlobal(a, b, windPlan)
        ab_vect = geometry.Vect((b.__sub__(a)).x, (b.__sub__(a)).y)
        angle_au_vent = ab_vect.angle(windvect)
        vent_effectif = abs(windvect) * cos(angle_au_vent)
        derive = (60 / VITESSE_CROISIERE) * abs(windvect) * sin(angle_au_vent) *(pi/180)
        groundSpeed = vent_effectif + VITESSE_CROISIERE * cos(derive)
        duration += abs(ab_vect) / groundSpeed
    return duration