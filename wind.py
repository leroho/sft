import geometry
import numpy as np

WIND_FILE = "DATA/bdap2017002362248.txt"


class Wind3D:
    """Description du vent global à une date donnée (ensemble des vents locaux sur l'ensemble des altitudes),
    avec les attributs suivants:
            - date: int (date des mesures)
            - dict: dict[key= altitude] = windPlan"""

    def __init__(self, date):
        self.date = date
        self.dict = {}

    def __repr__(self):
        return "<wind.Wind3D {0.date}>".format(self)

    def add_windPlan(self, windPlan):
        self.dict[windPlan.alt] = windPlan

    def get_windPlan(self, alt):
        return self.dict[alt]


class WindPlan(Wind3D):
    """Description du vent à une altitude donnée (ensemble des vents locaux), avec les attributs suivants:
        - alt: int (altitude des mesures)
        - dict: dict (dictionnaire des mesures sur le plan)
        - date: int (date des mesures)"""

    def __init__(self, alt, date):
        super().__init__(date)
        self.alt = alt
        self.dict = {}

    def __repr__(self):
        return "<wind.WindPlan {0.alt}>".format(self)

    def add_windLocal(self, wind):
        self.dict[(wind.coord_geo.x, wind.coord_geo.y)] = wind

    def get_windLocal(self, coord):
        return self.dict[(coord.x, coord.y)]

    def generate_list_wind(self, A, B):
        list_wind = []
        P1, P2 = generate_points(A, B)
        for i in np.arange(P1.x, P2.x, 0.5):
            for j in np.arange(P1.y, P2.y, 0.5):
                list_wind.append(self.dict[(i, j)])
        return list_wind


class WindLocal(WindPlan):
    """Description du vent local (mesure point), avec les attributs suivants:
        - coord_geo: Point tuple (coordonnées géographiques des mesures)
        - coord_plan: Point tuple (coordonnées projetées des mesures)
        - u: float (vitesse du vent en m/s suivant l'est)
        - v: float (vitesse du vent en m/s suivant le nord)
        - alt: int (altitude de la mesure)
        - date: int (date de la mesure)"""

    def __init__(self, coord_geo, alt, date):
        super().__init__(alt, date)
        self.coord_geo = coord_geo
        self.coord_plan = geometry.coord_plan(coord_geo)
        self.u = None
        self.v = None
        self.vect = None

    def __repr__(self):
        return "<wind.WindLocal {0.vect} {0.coord_geo}>".format(self)

    def add_valToVect(self, val, param):
        if param == 'u':
            self.u = val
        if param == 'v':
            self.v = val
        self.vect = geometry.Vect(self.u, self.v)

    def get_dir(self):
        return np.degrees(np.arctan2(self.v, self.u))

    def get_speed(self):
        return np.linalg.norm(self.vect)


def generate_points(A, B):
    minx = min(A.x, B.x)
    miny = min(A.y, B.y)
    maxx = max(A.x, B.x)
    maxy = max(A.y, B.y)
    P1 = geometry.Point(minx + 0.5 - minx % 0.5, miny + 0.5 - miny % 0.5)
    P2 = geometry.Point(maxx - maxx % 0.5, maxy - maxy % 0.5)
    return P1, P2


def from_file(filename):
    """from_file(str) return Wind3D : reads a wind map description file"""
    print("Loading wind file", filename + ' ...')
    wind3D_dict = {}
    coord_geo = None
    alt = None
    date = None
    param = None

    file = open(filename)
    for line in file:
        words = line.strip().split()
        if 'U' in words:
            param = 'u'
        if 'V' in words:
            param = 'v'
        if words[0] == 'NIVEAU':
            alt = int(words[2])
            date = int(words[6])
            if date not in wind3D_dict:
                wind3D = Wind3D(date)
                wind3D_dict[date] = wind3D
                windPlan = WindPlan(alt, date)
                wind3D.add_windPlan(windPlan)
            else:
                wind3D = wind3D_dict[date]
                if alt not in wind3D.dict:
                    windPlan = WindPlan(alt, date)
                    wind3D.add_windPlan(windPlan)
        if words[0] == 'LONGITUDE':
            long = int(words[1])/1000
            lat = int(words[3])/1000
            val = float(words[5])
            coord_geo = geometry.Point(long, lat)
            wind3D = wind3D_dict[date]
            windPlan = wind3D.get_windPlan(alt)
            if param == 'u':
                windLocal = WindLocal(coord_geo, alt, date)
                windLocal.add_valToVect(val, param)
                windPlan.add_windLocal(windLocal)
            else:
                windPlan.get_windLocal(coord_geo).add_valToVect(val, param)
    file.close()
    return wind3D_dict


if __name__ == '__main__':
    print(from_file(WIND_FILE))
