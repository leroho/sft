from Cartographie import coords
import numpy as np

class Node(object):
    def __init__(self,id_oaci):
        self.dico = {} # dictionnaire code OACI ==> aéroport voisins accéssibles
        self.id = id_oaci
    def add(self,oaci_voisin,poids): self.dico[oaci_voisin] = poids #ajouter un voisin avec son poids
    def remove(self,oaci_voisin): self.dico.pop(oaci_voisin) #supprimer un voisin
    def dans_dico(self,oaci_test): return oaci_test in self.dico #vérification apartennance aux voisins
    def poids(self,oaci_voisin): return self.dico[oaci_voisin] #renvoie le poids d'un voisin
    def voisins(self): return self.dico.items() #renvoie tous les voisins
    def __lt__(self, other):
        return self.dist < other.dist

def arbre_creation():
    aeroports_coords = coords("aerodrome.txt")
    liste_noeuds=[]
    x = float(input("l'avion doit s'arrêter tous les x minutes, choisir x : "))*60
    v = float(input("entrez la vitesse de croisière (km/h) : "))/3.6
    for ae1 in aeroports_coords:
        n = Node(ae1)
        for ae2 in aeroports_coords:
            if ae1 != ae2:
                dx = abs(aeroports_coords[ae1][0] - aeroports_coords[ae2][0]) #calcul de la deltaX entre les deux aerodrome ae1 et ae2
                dy = abs(aeroports_coords[ae1][1] - aeroports_coords[ae2][1]) #calcul de la deltaY entre les deux aerodrome ae1 et ae2
                distance = np.sqrt(dx**2 + dy**2)
                temps = distance / v
                if temps <= x :
                    n.add(ae2,temps)  #ajout des aérodromes accéssibles
        liste_noeuds.append(n)
    return liste_noeuds

arbre=arbre_creation()
# a10=arbre[10]
# print(len(a10.dico))
# print(a10.dico)