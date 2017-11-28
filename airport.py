import geometry


class Airport:
    """Description d'un aérodrome, avec les attributs suivants:
    - oaci: str (code OACI des aérodromes)
    - coord_geo: Point tuple (coordonnées géographiques des aérodromes)
    - coord_plan: Point tuple (coordonnées projetées des aérodromes)"""

    def __init__(self, oaci, coord_geo):
        self.oaci = oaci
        self.coord_geo = coord_geo
        self.coord_plan = geometry.coord_plan(coord_geo)

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
        self.apt_dict[airport.oaci] = airport

    def get_coord_geo(self, oaci):
        return self.apt_dict[oaci].coord_geo

    def get_coord_plan(self, oaci):
        return self.apt_dict[oaci].coord_plan


def from_file(filename):
    """from_file(str) return AirportList: lit un fichier de description de l'ensemble des aérodromes"""
    print("Chargement des aérodromes", filename + '...')
    airportList = AirportList()
    file = open(filename)
    for line in file:
        words = line.strip().split()
        oaci = words[1]
        coord_geo = geometry.Point(float(words[2]), float(words[3]))
        airport = Airport(oaci, coord_geo)
        airportList.add_apt(airport)
    file.close()
    return airportList
