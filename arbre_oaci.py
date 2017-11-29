import weight
import wind

FILE1 = "DATA/bdap2017002362248.txt"
FILE2 = "DATA/bdap2017002362250.txt"
APT_FILE = "DATA/aerodrome.txt"
WIND3D_DICT1 = wind.from_file(FILE1)
WIND3D_DICT2 = wind.from_file(FILE2)
DATES = [20171104000000, 20171104060000, 20171104120000, 20171104180000]
X = 20 * 60


class Graph():
    def __init__(self):
        self.nodes_dict = {}

    def add(self, node):
        self.nodes_dict[node.id] = node

    def remove(self, node):
        self.nodes_dict.pop(node)

    def __repr__(self):
        return "<arbre_oaci.Graph {0.nodes_dict}>".format(self)


class Node():
    def __init__(self, id_oaci, coord_geo, coord_plan):
        self.dico = {}  # dictionnaire code OACI ==> aéroport voisins accéssibles
        self.id = id_oaci
        self.coord_geo = coord_geo
        self.coord_plan = coord_plan
        self.parent = None
        self.H = 0
        self.G = 0

    def add(self, voisin, poids):
        self.dico[voisin.id] = poids  # ajouter un voisin avec son poids

    def remove(self, oaci_voisin):
        self.dico.pop(oaci_voisin)  # supprimer un voisin

    def __repr__(self):
        return "<Node {0.id}>".format(self)

    def dans_dico(self, oaci_test):
        return oaci_test in self.dico  # vérification apartennance aux voisins

    def voisins(self, windPlan, graphe, n):
        for (id, node) in graphe.nodes_dict.items():
            if id != self.id:
                poids = weight.duration_calcul(self.coord_plan, node.coord_plan, windPlan, n)
                if poids <= X:
                    self.add(node, poids)
        return self.dico  # renvoie tous les voisins


def arbre_creation(airportList):
    graphe = Graph()
    for (oaci, airport) in airportList.apt_dict.items():
        node = Node(oaci, airport.coord_geo, airport.coord_plan)
        graphe.add(node)
    return graphe


def diagonal(node1, node2, windPlan, n):
    return 0 if node1.id == node2.id else weight.duration_calcul(node1.coord_plan, node2.coord_plan, windPlan, n)


def convert_into_format(x):
    heures = x // 3600
    min = (x - heures * 3600) // 60
    sec = int(x - heures * 3600 - min * 60)
    return heures * 1e5 + min * 1e3 + sec


def astar(dep, arr, alt, time_start, graphe):
    openset = set()
    closedset = set()
    current = dep
    # Add the starting point to the open set
    openset.add(current)
    # While the open set is not empty
    while openset:
        # Find the item in the open set with the lowest G + H score
        current = min(openset, key=lambda node: node.G + node.H)
        # If it is the item we want, retrace the path and return it
        current_id = current.id
        if current_id == arr.id:
            duration = current.G
            path = []
            while current_id:
                path.append(current_id)
                current_id = graphe.nodes_dict[current_id].parent
            return {duration: path[-1::-1]}
        # Remove the item from the open set
        openset.remove(current)
        # Add it to the closed set
        closedset.add(current)

        time = convert_into_format(time_start + current.G)
        date = min(DATES, key=lambda x: abs(x - time))
        wind3D = WIND3D_DICT1[date] if date in WIND3D_DICT1 else WIND3D_DICT2[date]
        windPlan = wind3D.dict[alt]

        # Loop through the node's children/siblings
        for (id, duration) in current.voisins(windPlan, graphe, 3).items():
            node = graphe.nodes_dict[id]
            # If it is already in the closed set, skip it
            if node in closedset:
                new_g = current.G + duration
                if node.G > new_g:
                    # If so, update the node to have a new parent
                    node.G = new_g
                    node.parent = current_id
                    openset.add(node)
                    closedset.remove(node)
            # Otherwise if it is already in the open set
            elif node in openset:
                # Check if we beat the G score
                new_g = current.G + duration
                if node.G > new_g:
                    # If so, update the node to have a new parent
                    node.G = new_g
                    node.parent = current_id
            else:
                # If it isn't in the open set, calculate the G and H score for the node
                node.G = current.G + duration
                node.H = diagonal(node, arr, windPlan, 7)
                # Set the parent to our current item
                node.parent = current_id
                # Add it to the set
                openset.add(node)
    # Throw an exception if there is no path
    raise ValueError('No Path Found')
