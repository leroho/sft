import arbre_oaci
import wind
import geometry
import airplane
from ui_interface import Ui_Interface
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItemGroup, QGraphicsPathItem
from PyQt5.QtGui import QPen, QColor, QPainterPath, QBrush, QPainter

ALTITUDES = [400, 500, 600, 700, 800]

def create_wind3D_dict(file1, file2):
    wind3D_dict = {}
    for (date, wind3D) in wind.from_file(file1).items():
        wind3D_dict[date] = wind3D
    for (date, wind3D) in wind.from_file(file2).items():
        wind3D_dict[date] = wind3D
    return wind3D_dict

def find_path(dep, arr, timeStart, airplaine, wind3D_dict, graphe):
    list = []
    for alt in ALTITUDES:
        fligth = arbre_oaci.Fligth(dep, arr, alt, arbre_oaci.time(timeStart))
        list.append(arbre_oaci.astar(fligth, airplaine, wind3D_dict, graphe))
    return min(list, key = lambda x : x.duration)


class IHM(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Interface()
        self.ui.setupUi(self)
        self.graphe = arbre_oaci.arbre_creation("Données/aerodrome.txt")
        def change_dep(text):
            self.dep = self.graphe.nodes_dict[text]
        #Ui_Interface.lineEdit.connect.textEdited(lambda text: change_dep(text))
        def change_arr(text):
            self.arr = self.graphe.nodes_dict[text]
        #Ui_Interface.lineEdit_2.connect.textEdited(lambda text: change_arr(text))
        def change_timeStart(text):
            self.timeStart = self.graphe[text]
        self.wind3D_dict = create_wind3D_dict("Données/bdap2017002362248.txt", "Données/bdap2017002362250.txt")
        #self.flight = find_path(self.dep, self.arr, self.timeStart, self.airplane, self.wind3D_dict, self.graphe)
        self.scene = self.ui.scene
        self.ui.graphicsView.setScene(self.scene)
        self.scene.setBackgroundBrush(QBrush(QColor("black")))
        self.aerodromes_dict = geometry.from_file("Données/aerodrome.txt")
        self.add_aerodromes()
        self.path_aerodromes = None
        self.ui.pushButton.clicked.connect(self.search)

    def adapt_scale(self, coord):
        pt = geometry.Point(coord.long, coord.lat)
        pt.x = (pt.x + 400000)*600//1200000
        pt.y = (5800000 - pt.y)*600//1200000
        return pt

    def add_aerodromes(self):
        for id, coord in self.aerodromes_dict.items():
            point = self.adapt_scale(coord)
            item = QGraphicsEllipseItem(point.x, point.y, 6, 6)
            item.setBrush(QBrush(QColor("red")))
            self.scene.addItem(item)

    def draw_path(self,path):
        self.path_aerodromes = QGraphicsItemGroup()
        pen = QPen(QColor("yellow"), 3)
        path_graphic = QPainterPath()
        a = self.adapt_scale(self.aerodromes_dict[path[0]])
        path_graphic.moveTo(a.x + 3, a.y + 3)
        for k in range(len(path) - 1):
            b = self.adapt_scale(self.aerodromes_dict[path[k + 1]])
            path_graphic.lineTo(b.x + 3, b.y + 3)
        item = QGraphicsPathItem(path_graphic, self.path_aerodromes)
        item.setPen(pen)
        for id in path:
            b = self.adapt_scale(self.aerodromes_dict[id])
            item2 = QGraphicsEllipseItem(b.x, b.y, 6, 6, self.path_aerodromes)
            item2.setBrush(QBrush(QColor("#00ff00")))
        self.scene.addItem(self.path_aerodromes)


    def search(self):
        self.scene.removeItem(self.path_aerodromes)
        try :
            self.dep = self.graphe.nodes_dict[self.ui.lineEdit.text()]
            self.arr = self.graphe.nodes_dict[self.ui.lineEdit_2.text()]
            self.timeStart = self.ui.lineEdit_3.text()
            self.v_c = self.ui.spinBox.value()
            self.alt_inf = self.ui.spinBox_2.value()
            self.alt_sup = self.ui.spinBox_3.value()
            self.temps_arrêt = self.ui.spinBox_4.value()*60
            self.airplane = airplane.Airplane(self.alt_inf, self.alt_sup, self.temps_arrêt, self.v_c)
            self.flight = find_path(self.dep, self.arr, self.timeStart, self.airplane, self.wind3D_dict, self.graphe)
            self.draw_path(self.flight.path)
            self.ui.listWidget.addItem(str(self.flight.path))
            self.ui.listWidget.addItem("durrée minimale = " + str(arbre_oaci.hms(self.flight.duration)))
            self.ui.listWidget.addItem("altitude optimale = " + str(self.flight.alt) + " hPa")

        except ValueError:
            return "no path found"