import geometry
from wind import from_file

FILE1 = "Données/bdap2017002362248.txt"
FILE2 = "Données/bdap2017002362250.txt"
WIND3D_DICT1 = from_file(FILE1)
WIND3D_DICT2 = from_file(FILE2)

class Graph():
    def __init__(self):
        self.nodes_dict = {}
    def add(self, node):
        self.nodes_dict[node.id] = node
    def remove(self, node):
        self.nodes_dict.pop(node)
    def __repr__(self):
        return "<Graph {0.nodes_dict}>".format(self)

class Node():
    def __init__(self, id_oaci, coord):
        self.dico = {} # dictionnaire code OACI ==> aéroport voisins accéssibles
        self.id = id_oaci
        self.coord = coord
        self.parent = None
        self.H = 0
        self.G = 0
    def add(self, voisin, poids):
        self.dico[voisin.id] = poids #ajouter un voisin avec son poids
    def remove(self,oaci_voisin):
        self.dico.pop(oaci_voisin) #supprimer un voisin
    def __repr__(self):
        return "<Node {0.id}: {0.coord}>".format(self)
    def dans_dico(self,oaci_test):
        return oaci_test in self.dico #vérification apartennance aux voisins
    def voisins(self, airplane, windPlan, graphe):
        for (id, node) in graphe.nodes_dict.items():
            if id != self.id :
                duration = airplane.fligth(self.coord, node.coord, windPlan)[-1]
                if duration <= airplane.X:
                    self.add(node, duration)
        return self.dico #renvoie tous les voisins

class Fligth():
    def __init__(self, dep, arr, alt, time_start):
        self.dep = dep
        self.arr = arr
        self.alt = alt
        self.time_start = time_start
        self.duration = None
        self.path = None
    def __repr__(self):
        return "fligth : alt = {0.alt} hPa ; ".format(self) + "duration = " + str(hms(self.duration)) + " ; path = {0.path}".format(self)

def arbre_creation(filename):
    aeroports_coords = geometry.from_file(filename)
    graphe = Graph()
    for (id_oaci, coord) in aeroports_coords.items():
        node = Node(id_oaci, coord)
        graphe.add(node)
    return graphe

def diagonal(node1, node2, airplane, windPlan):
    return 0 if node1.id  == node2.id else airplane.fligth(node1.coord, node2.coord, windPlan)[-1]

# Time string conversions

def hms(s):
    """hms(int) return str
    return a formatted string HH:MM:SS for the given time step"""
    return "{:02d}:{:02d}:{:02d}".format(int(s) // 3600, int(s) // 60 % 60, int(s) % 60)

def time(str_hms):
    """time(str) return int
    return the time step corresponding to a formatted string HH:MM:SS"""
    l = str_hms.replace(':', ' ').split()
    return (int(l[0]) * 3600 + int(l[1]) * 60 + int(l[2]))

def astar(fligth, airplane, wind3D_dict, graphe):
    """astar(Fligth, Airplane, dict, Graph) return Fligth
    return fligth en actualisant fligth.duration et fligth.path"""
    openset = set()
    closedset = set()
    current = fligth.dep
    # ajouter le noeud initial à openset
    openset.add(current)
    # tant que openset n'est pas vide
    while openset:
        # trouver dans openset le noeud avec le plus petit G + H
        current = min(openset, key = lambda node: node.G + node.H)
        current_id = current.id
        # si le noeud correspond à l'arriver
        if  current_id == fligth.arr.id:
            duration = current.G # la durrée du trajet
            path = [] # initialisation du chemin
            # remplir path
            while current_id:
                path.append(current_id)
                current_id = graphe.nodes_dict[current_id].parent
            fligth.duration = duration
            fligth.path = path[-1::-1]
            return fligth
        # supprimer le noeud de openset
        openset.remove(current)
        # ajouter le noeud à closed set
        closedset.add(current)

        time = int(hms(fligth.time_start + current.G).replace(':', '')) # temps au moment ou on parcourt le noeud
        (date, wind3D) = min(wind3D_dict.items(), key=lambda x: abs((x[0]%1e6) - time)) #  pour obtenir le dict des vent à la date la plus proche de time
        windPlan = wind3D.dict[fligth.alt] # class = WindPlan : permet d'obtenir le dict des vent à la date "date" et à l'altitude "alt"

        # parcourir les noeuds voisins
        for (id, duration) in current.voisins(airplane, windPlan, graphe).items():
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
                node.H = diagonal(node, fligth.arr, airplane, windPlan)
                # actualiser le parent de node à current
                node.parent = current_id
                # ajouter node à openset
                openset.add(node)
    # si l'arriver n'est pas atteint lever l'erreur "ValueError"
    raise ValueError('No Path Found')