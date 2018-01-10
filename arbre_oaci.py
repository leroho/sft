import geometry
from wind import from_file


class Graph():
    def __init__(self):
        self.nodes_dict = {}

    def add(self, node):
        self.nodes_dict[node.id] = node

    def remove(self, node):
        self.nodes_dict.pop(node)

    def __repr__(self):
        return "<Graph {0.nodes_dict}>".format(self)

    def dim(self):
        min_x = min(node.coord.x for node in self.nodes_dict.values())
        max_x = max(node.coord.x for node in self.nodes_dict.values())
        min_y = min(node.coord.y for node in self.nodes_dict.values())
        max_y = max(node.coord.y for node in self.nodes_dict.values())
        return min_x, max_x, min_y, max_y
class Node():
    """represente un aedrome dans le graphe
        - id: string code OACI
        - coord: geometry.Point coordonnées de l'aerodrome
        - parent: Node parent du noeud considéré
        - H: float heuristique(estimation de la durée vers l'arrivé) du noeud courant
        - G: float durée du trajet depuis le départ"""

    def __init__(self, id_oaci, coord):
        self.id = id_oaci
        self.coord = coord
        self.parent = None
        self.H = 0
        self.G = 0

    def __repr__(self):
        return "<Node {0.id}: {0.coord}>".format(self)

    def voisins(self, airplane, windPlan, graphe, with_wind):
        """voisin(node, airplane.Airplane, wind.WindPlan, Graph, bool) return dict
        renvoie le dictionnaire des voisins à moin de X min"""
        dico = {}
        for (id, node) in graphe.nodes_dict.items():
            if id != self.id:
                duration = airplane.trajectory(self.coord, node.coord, windPlan, with_wind)
                if duration <= airplane.X:
                    dico[id] = duration
        return dico


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

    def __repr__(self):
        return "flight : pression = {0.pression} hPa ; ".format(self) + "duration = " + str(
            hms(self.duration)) + " ; path = {0.path}".format(self)


def arbre_creation(filename):
    """arbre_creation(str) return Graph
    renvoie le graphe formé par l'ensemble des aerodromes"""
    aerodrome_coords = geometry.from_file(filename)
    graphe = Graph()
    for (id_oaci, coord) in aerodrome_coords.items():
        node = Node(id_oaci, coord)
        graphe.add(node)
    return graphe


def diagonal(node1, node2, airplane, windPlan, with_wind):
    """
    :param node1: Node premier aerodrome
    :param node2: Node deuxième aerodrome
    :param airplane: airplane.Airplane avion considéré
    :param windPlan: wind.WindPlan
    :param with_wind: bool avec ou sans vent
    :return: float durée en seconde
    renvoie l'estimation de la durée du trajet entr node1 et node2"""
    return 0 if node1.id == node2.id else airplane.trajectory(node1.coord, node2.coord, windPlan, with_wind)


def hms(s):
    """hms(int) return str
    convertion d'une durée en seconde au format hh:mm:ss"""
    return "{:02d}:{:02d}:{:02d}".format(int(s) // 3600, int(s) // 60 % 60, int(s) % 60)


def time(str_hms):
    """time(str) return int
    conversion d'une durée au format hh:mm:ss en une durée en seconde"""
    l = str_hms.replace(':', ' ').split()
    return (int(l[0]) * 3600 + int(l[1]) * 60 + int(l[2]))


def get_wind3D(wind3D_dict, sec):
    t = int(hms(sec).replace(':', ''))
    (date, wind3D) = min(wind3D_dict.items(), key=lambda x: abs((x[0] % 1e6) - t))
    return wind3D


def astar(flight, airplane, wind3D_dict, graphe, with_wind):
    """astar(Flight, Airplane, dict, Graph) return Flight
    return flight en actualisant flight.duration et flight.path"""
    openset = set()
    closedset = set()
    current = flight.dep
    # ajouter le noeud initial à openset
    openset.add(current)
    # tant que openset n'est pas vide
    while openset:
        # trouver dans openset le noeud avec le plus petit G + H
        current = min(openset, key=lambda node: node.G + node.H)
        current_id = current.id

        # si le noeud correspond à l'arriver
        if current_id == flight.arr.id:
            duration = current.G  # la durrée du trajet
            path = []  # initialisation du chemin
            # remplir path
            while current_id:
                path.append(current_id)
                current_id = graphe.nodes_dict[current_id].parent
            flight.duration = duration
            flight.path = path[-1::-1]
            return flight
        # supprimer le noeud de openset
        openset.remove(current)
        # ajouter le noeud à closed set
        closedset.add(current)
        wind3D = get_wind3D(wind3D_dict, flight.time_start + current.G)
        # class = WindPlan : permet d'obtenir le dict des vent à la date "date" et à l'pressionitude "pression"
        windPlan = wind3D.dict[flight.pression]

        # parcourir les noeuds voisins
        for (id, duration) in current.voisins(airplane, windPlan, graphe, with_wind).items():
            node = graphe.nodes_dict[id]
            # si node est déjà dans closedset
            if node in closedset:
                # vérifier s'il vaut mieux passer pr current
                new_g = current.G + duration
                if node.G > new_g:
                    # si c'est le cas, actualiser le parent de node à current
                    node.G = new_g
                    node.parent = current_id
                    # remettre node dans openset
                    openset.add(node)
                    # supprimer node de closedset
                    closedset.remove(node)
            # sinon, si node est déjà dans openset
            elif node in openset:
                # vérifier s'il vaut mieux passer pr current
                new_g = current.G + duration
                if node.G > new_g:
                    # si c'est le cas, actualiser le parent de node à current
                    node.G = new_g
                    node.parent = current_id
            else:
                # sinon, calculer G et H de node
                node.G = current.G + duration
                node.H = diagonal(node, flight.arr, airplane, windPlan, with_wind)
                # actualiser le parent de node à current
                node.parent = current_id
                # ajouter node à openset
                openset.add(node)
    # si l'arriver n'est pas atteint lever l'erreur "ValueError"
    raise NoPathError

class NoPathError(Exception): pass