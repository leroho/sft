import arbre_oaci
import  wind
import  geometry
import matplotlib.pyplot as pl
import weigth

ALTITUDES = [400, 500, 600, 700, 800]
FILE1 = "Données/bdap2017002362248.txt"
FILE2 = "Données/bdap2017002362250.txt"
DEP = "LFBO"#input("aérodrme de départ : ")
ARR = "LFQQ"#input("aérodrme de d'arriver : ")
TIME_START = "13:30:00"#input("heure de départ : ")

def create_wind3D_dict(file1, file2):
    wind3D_dict = {}
    for (date, wind3D) in wind.from_file(file1).items():
        wind3D_dict[date] = wind3D
    for (date, wind3D) in wind.from_file(file2).items():
        wind3D_dict[date] = wind3D
    return  wind3D_dict

def find_path(airplaine, wind3D_dict, graphe):
    list = []
    dep = graphe.nodes_dict[DEP]
    arr = graphe.nodes_dict[ARR]
    for alt in ALTITUDES:
        fligth = arbre_oaci.Fligth(dep, arr, alt, arbre_oaci.time(TIME_START))
        list.append(arbre_oaci.astar(fligth, airplaine, wind3D_dict, graphe))
    return min(list, key = lambda x : x.duration)

if __name__ == "__main__":
    airplaine = weigth.Airplane(400, 800, 20*60, 200)
    wind3D_dict = create_wind3D_dict("Données/bdap2017002362248.txt", "Données/bdap2017002362250.txt")
    graphe = arbre_oaci.arbre_creation("Données/aerodrome.txt")
    fligth = find_path(airplaine, wind3D_dict, graphe)
    print(fligth)
    d = geometry.from_file("Données/aerodrome.txt")
    for elt in d:
        point = d[elt]
        pl.plot(point.x, point.y,'.',color="green")
    dico = graphe.nodes_dict
    coordx=[dico[id_oaci].coord.x for id_oaci in fligth.path]
    coordy=[dico[id_oaci].coord.y for id_oaci in fligth.path]
    pl.plot(coordx,coordy,"or")
    pl.plot(coordx,coordy,"r")
    pl.show()