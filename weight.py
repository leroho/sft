import geometry
from numpy import cos, sin, pi

VITESSE_CROISIERE = 200


def windVectSquare(A, B, windPlan):
    windVect = geometry.Vect(0, 0)
    list_wind = windPlan.generate_windInSquare(A, B)
    n = len(list_wind)
    for wind in list_wind:
        windVect += wind.vect
    return windVect.__rmul__(1 / n) if n != 0 else min(windPlan.dict.values(), key=lambda wind: abs(wind.coord_plan.__sub__(A))).vect


def duration_calcul(A, B, windPlan, n):
    duration = 0
    for k in range(n):
        Aiplan = A + (B.__sub__(A)).__rmul__(k / n)
        Aigeo = geometry.coord_geo(Aiplan)
        Biplan = A + (B.__sub__(A)).__rmul__((k + 1) / n)
        Bigeo = geometry.coord_geo(Biplan)
        windVect = windVectSquare(Aigeo, Bigeo, windPlan)
        ABi_vect = geometry.Vect((Biplan.__sub__(Aiplan)).x, (Biplan.__sub__(Aiplan)).y)
        angle_au_vent = ABi_vect.angle(windVect)
        vent_effectif = abs(windVect) * cos(angle_au_vent)
        derive = (60 / VITESSE_CROISIERE) * abs(windVect) * sin(angle_au_vent) * (pi / 180)
        groundSpeed = vent_effectif + VITESSE_CROISIERE * cos(derive)
        duration += abs(ABi_vect) / groundSpeed
    return duration
