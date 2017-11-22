import geometry

APT_FILE = 'DATA/aerodrome.txt'


class Airport:
    """Description d'un aérodrome, avec les attributs suivants:
    - oaci: str (code OACI des aérodromes)
    - coord: Point tuple (coordonnées géographiques des aérodromes)"""

    def __init__(self, oaci, coord):
        self.oaci = oaci
        self.coord = coord

    def __repr__(self):
        return "<airport.Airport {0}>".format(self.oaci)


class AirportList:
    """Description compléte de l'ensemble des aérodromes, avec les attributs suivants:
        - """

    def __init__(self):
        self.apt_dict = {}

    def __repr__(self):
        return "{0.apt_dict}".format(self)

    def add_apt(self, airport):
        self.apt_dict[airport.oaci] = airport.coord

    def get_coord(self, oaci):
        return self.apt_dict[oaci]


def from_file(filename):
    """from_file(str) return AirportMap: lit un fichier de description de l'ensemble des aérodromes"""
    print("Chargement des aérodromes", filename + '...')
    airportList = AirportList()
    file = open(filename)
    for line in file:
        words = line.strip().split()
        oaci = words[1]
        coord = geometry.Point(float(words[2]), float(words[3]))
        airport = Airport(oaci, coord)
        airportList.add_apt(airport)
    file.close()
    return airportList


if __name__ == '__main__':
    airportList = from_file(APT_FILE)
    print(airportList.get_coord('LFAB'))
    print(airportList)
