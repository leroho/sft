import geometry
from numpy import cos, sin, pi

class Airplane:

    def __init__(self, alt_inf, alt_sup, X, vitesse_croisiere):
        self.alt_inf = alt_inf
        self.alt_sup = alt_sup
        self.v_c = vitesse_croisiere
        self.X = X

    def trajectory(self, dep_coord, arr_coord, windPlan):
        windvect = windPlan.windGlobal(dep_coord, arr_coord)
        ab_vect = geometry.Vect((arr_coord - dep_coord).x, (arr_coord - dep_coord).y)
        angle_au_vent = ab_vect.angle(windvect)
        vent_effectif = abs(windvect) * cos(angle_au_vent)
        derive = (60 / self.v_c) * abs(windvect) * sin(angle_au_vent) * (pi / 180)
        groundSpeed = vent_effectif + self.v_c * cos(derive)
        duration = abs(ab_vect) / groundSpeed
        normal_duration = abs(ab_vect)/self.v_c
        return normal_duration, duration