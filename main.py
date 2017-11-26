import arbre_oaci
import cartographie as car
import matplotlib.pyplot as pl

ALTITUDES = [400, 500, 600, 700, 800]
DEP = "LFBO"#input("aérodrme de départ : ")
ARR = "LFRO"#input("aérodrme de d'arriver : ")
TIME_START = 0#input("heure de départ : ")

def find_path(graphe):
    dict = {}
    dep = graphe.nodes_dict[DEP]
    arr = graphe.nodes_dict[ARR]
    for alt in ALTITUDES:
        result = arbre_oaci.astar(dep, arr, alt, TIME_START, graphe)
        dict[alt] = result
    best_altitude = min(dict, key= lambda alt: list(dict[alt].items())[0][0])
    minimum_duration = list(dict[best_altitude].items())[0][0]
    best_path = dict[best_altitude][minimum_duration]

    return minimum_duration, best_altitude, best_path

if __name__ == "__main__":
    graphe = arbre_oaci.arbre_creation()
    pathh = find_path(graphe)[2]
    d = car.coords_dict("Données/aerodrome.txt")
    print(len(d))
    for elt in d:
        point = d[elt]
        pl.plot(point.x, point.y,'+')
    dico=graphe.nodes_dict
    for i in pathh:
        coord=dico[i].coord
        pl.plot(coord.x,coord.y,"or")
    pl.show()