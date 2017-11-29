import arbre_oaci
import airport
import matplotlib.pyplot as pl

APT_FILE = "DATA/aerodrome.txt"

ALTITUDES = [400, 500, 600, 700, 800]
DEP = "LFBO"  # input("aérodrme de départ : ")
ARR = "LFPG"  # input("aérodrme de d'arriver : ")
TIME_START = 0  # input("heure de départ : ")


def find_path(graphe):
    dict = {}
    dep = graphe.nodes_dict[DEP]
    arr = graphe.nodes_dict[ARR]
    for alt in ALTITUDES:
        result = arbre_oaci.astar(dep, arr, alt, TIME_START, graphe)
        dict[alt] = result
    best_altitude = min(dict, key=lambda alt: list(dict[alt].items())[0][0])
    minimum_duration = list(dict[best_altitude].items())[0][0]
    best_path = dict[best_altitude][minimum_duration]

    return minimum_duration, best_altitude, best_path


if __name__ == "__main__":
    airportList = airport.from_file(APT_FILE)
    graphe = arbre_oaci.arbre_creation(airportList)
    info_path = find_path(graphe)
    path = info_path[2]
    alt = info_path[1]
    print(path, alt)
    for oaci in airportList.apt_dict:
        point = airportList.get_coord_plan(oaci)
        pl.plot(point.x, point.y, '+')
    dico = graphe.nodes_dict
    for i in path:
        coord = dico[i].coord_plan
        pl.plot(coord.x, coord.y, "or")
    pl.show()
