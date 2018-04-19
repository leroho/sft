import geometry
from numpy import cos, sin, pi


class Airplane:
    """represente un avion
        -alt_inf: int altitude minimale à laquelle l'avion peut voler
        -alt_sup: int altitude maximale à laquelle l'avion peut voler
        -v_c: float vitesse de croisière de l'avion
        -X: int temps d'arrêt de l'avion"""

    def __init__(self, alt_inf, alt_sup, X, vitesse_croisiere):
        self.alt_inf = alt_inf
        self.alt_sup = alt_sup
        self.v_c = vitesse_croisiere
        self.X = X

    def trajectory(self, dep_coord, arr_coord, windPlan, with_wind):
        """
        :param dep_coord: geometry.Point coordonées du point de départ
        :param arr_coord: geometry.Point coordonées du point d'arrivé
        :param windPlan: wind.Windplan
        :param with_wind: bool avec ou sans vent
        :return: float durée du trajet
        renvoie la durée en seconde entre 2 points"""
        ab_vect = geometry.Vect((arr_coord - dep_coord).x, (arr_coord - dep_coord).y)
        windvect = windPlan.windGlobal(dep_coord, arr_coord)
        if with_wind and abs(windvect) != 0:
            angle_au_vent = ab_vect.angle(windvect)
            vent_effectif = abs(windvect) * cos(angle_au_vent)
            derive = (60 / self.v_c) * abs(windvect) * sin(angle_au_vent) * (pi / 180)
            groundSpeed = vent_effectif + self.v_c * cos(derive)
            duration = abs(ab_vect) / groundSpeed
            return duration
        return abs(ab_vect) / self.v_c
