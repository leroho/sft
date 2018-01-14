import geometry
from numpy import cos, sin, pi

class Flight():
    """represente le vol entre 2 aerodromes données
        -dep: Node aerodrome de départ
        -arr: Node aerodrome d'arrivé
        -pression: int pression du vol considéré
        -time_start: float heure de départ en secondes
        -duration: float durée du trajet
        -path: list liste des id des aerodromes suivis"""

    def __init__(self, dep, arr, pression, time_start):
        self.dep = dep
        self.arr = arr
        self.pression = pression
        self.time_start = time_start
        self.duration = None
        self.path = None
        self.edges = []

    def __repr__(self):
        return "flight : pression = {0.pression} hPa ; ".format(self) + "duration = " + str(
            self.duration) + " ; path = {0.path}".format(self)

class Airplane:
    """represente un avion
        -pression_inf: int pression minimale à laquelle l'avion peut voler
        -pression_sup: int pression maximale à laquelle l'avion peut voler
        -v_c: float vitesse de croisière de l'avion
        -X: int temps d'arrêt de l'avion"""

    def __init__(self, pression_inf, pression_sup, X, vitesse_croisiere):
        self.pression_inf = pression_inf
        self.pression_sup = pression_sup
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
        ab_vect = geometry.Vect(arr_coord.x - dep_coord.x, arr_coord.y - dep_coord.y)
        windvect = windPlan.windGlobal(dep_coord, arr_coord)
        if with_wind and abs(windvect) != 0:
            angle_au_vent = ab_vect.angle(windvect)
            vent_effectif = abs(windvect) * cos(angle_au_vent)
            derive = (60 / self.v_c) * abs(windvect) * sin(angle_au_vent) * (pi / 180)
            groundSpeed = vent_effectif + self.v_c * cos(derive)
            duration = abs(ab_vect) / groundSpeed
            return duration
        return abs(ab_vect) / self.v_c
