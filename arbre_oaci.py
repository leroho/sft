

class Node(object):
    def __init__(self,id_oaci):
        self.dico = {} # dictionnaire code OACI ==> aéroport voisins accéssibles
        self.oaci = id_oaci
    def add(self,oaci_voisin,poids): self.dico[oaci_voisin] = poids
    def remove(self,oaci_voisin): self.dico.pop(oaci_voisin)
    def dans_dico(self,oaci_test): return oaci_test in self.dico
    def poids(self,oaci_voisin): return self.dico[oaci_voisin]
    def voisins(self): return self.dico.items()
    def __lt__(self, other):
        return self.dist < other.dist

