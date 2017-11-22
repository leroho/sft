import geometry
import numpy as np

WIND_FILE = "DATA/bdap2017002362248.txt"


class Wind3D:
    """Description du vent global à une date donnée (ensemble des vents locaux sur l'ensemble des altitudes),
    avec les attributs suivants:
            - date: int (date des mesures)
            - wind_dict: dict[key= altitude] = windPlan"""

    def __init__(self, date):
        self.date = date
        self.wind_dict = {}

    def __repr__(self):
        return "<wind.Wind3D {0.date}>".format(self)

    def add_windPlan(self, windPlan):
        self.wind_dict[windPlan.alt] = windPlan


class WindPlan(Wind3D):
    """Description du vent à une altitude donnée (ensemble des vents locaux), avec les attributs suivants:
        - alt: int (altitude des mesures)
        - list: np.array (liste des mesures sur le plan)
        - date: int (date des mesures)"""

    def __init__(self, alt, date):
        super().__init__(date)
        self.alt = alt
        self.list = []

    def __repr__(self):
        return "<wind.WindPlan {0.alt}>".format(self)

    def add_windLocal(self, wind):
        self.list = np.append(self.list, wind)

    def get_windLocal(self, coord):
        for wind in self.list:
            if wind.coord == coord:
                return wind

                # def get_map(self):
                #    return self.list.reshape(27, 20)


class WindLocal(WindPlan):
    """Description du vent local (mesure point), avec les attributs suivants:
        - u: float (vitesse du vent en m/s suivant l'est)
        - v: float (vitesse du vent en m/s suivant le nord)
        - coord: Point tuple (coordonnées géographiques des mesures)
        - alt: int (altitude de la mesure)
        - date: int (date de la mesure)"""

    def __init__(self, coord, alt, date):
        super().__init__(alt, date)
        self.coord = coord
        self.u = None
        self.v = None
        self.vect = None

    def __repr__(self):
        return "<wind.WindLocal {0.vect} {0.coord}>".format(self)

    def add_valToVect(self, val, param):
        if param == 'u':
            self.u = val
        if param == 'v':
            self.v = val
        self.vect = np.array((self.u, self.v))

    def get_dir(self):
        return np.degrees(np.arctan2(self.v, self.u))

    def get_speed(self):
        return np.linalg.norm(self.vect)


def from_file(filename):
    """from_file(str) return Wind3D : reads a wind map description file"""
    print("Loading wind map", filename + '...')
    wind3D_dict = {}
    coord = None
    alt = None
    date = None
    param = None

    file = open(filename)
    i=0
    for line in file:
        i+=1
        words = line.strip().split()
        print(i,words)
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
                if alt not in wind3D.wind_dict:
                    windPlan = WindPlan(alt, date)
                    wind3D.add_windPlan(windPlan)
        if words[0] == 'LONGITUDE':
            long = words[1]
            lat = words[2]
            val = words[5]
            coord = geometry.Point(long, lat)
            wind3D = wind3D_dict[date]
            windPlan = wind3D.wind_dict[alt]
            if param == 'u':
                windLocal = WindLocal(coord, alt, date)
                windLocal.add_valToVect(val, param)
                windPlan.add_windLocal(windLocal)
            else:
                windPlan.get_windLocal(coord).add_valToVect(val, param)
    file.close()
    return wind3D_dict


if __name__ == '__main__':
    print(from_file(WIND_FILE))
