import arbre_oaci
import wind
import geometry
import airplane
from ui_interface import Ui_Interface
from PyQt5 import QtCore, QtGui, QtWidgets
import math

WIND_PATH1 = "Données/bdap2017002362248.txt"
WIND_PATH2 = "Données/bdap2017002362250.txt"
AERODROMES_PATH = "Données/aerodrome.txt"


def create_wind3D_dict(file1, file2):
    wind3D_dict = {}
    for (date, wind3D) in wind.from_file(file1).items():
        wind3D_dict[date] = wind3D
    for (date, wind3D) in wind.from_file(file2).items():
        wind3D_dict[date] = wind3D
    return wind3D_dict


def find_path(dep, arr, timeStart, airplane, wind3D_dict, graphe, with_wind):
    if with_wind:
        dico = {}
        for alt in range(airplane.alt_inf, airplane.alt_sup + 100, 100):
            flight = arbre_oaci.Flight(dep, arr, alt, arbre_oaci.time(timeStart))
            dico[alt] = arbre_oaci.astar(flight, airplane, wind3D_dict, graphe, with_wind)
        return min(dico.values(), key=lambda x: x.duration)
    flight = arbre_oaci.Flight(dep, arr, airplane.alt_inf, arbre_oaci.time(timeStart))
    return arbre_oaci.astar(flight, airplane, wind3D_dict, graphe, with_wind)


class PanZoomView(QtWidgets.QGraphicsView):
    """An interactive view that supports Pan and Zoom functions"""

    def __init__(self, scene):
        super().__init__(scene)
        # enable anti-aliasing
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        # enable drag and drop of the view
        self.setDragMode(self.ScrollHandDrag)

    def wheelEvent(self, event):
        """Overrides method in QGraphicsView in order to zoom it when mouse scroll occurs"""
        factor = math.pow(1.001, event.angleDelta().y())
        self.zoom_view(factor)

    @QtCore.pyqtSlot(int)
    def zoom_view(self, factor):
        """Updates the zoom factor of the view"""
        self.setTransformationAnchor(self.AnchorUnderMouse)
        super().scale(factor, factor)


class IHM(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Interface()
        self.ui.setupUi(self)
        self.scene = QtWidgets.QGraphicsScene()
        self.view = PanZoomView(self.scene)
        self.view.setEnabled(True)
        self.view.setMinimumSize(QtCore.QSize(600, 600))
        self.view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.view.setObjectName("view")
        self.ui.verticalLayout_radar.addWidget(self.view)
        self.view.raise_()
        self.view.setScene(self.scene)
        self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("black")))
        self.graph = arbre_oaci.arbre_creation(AERODROMES_PATH)
        self.wind3D_dict = create_wind3D_dict(WIND_PATH1, WIND_PATH2)
        id_list = [id for id in self.graph.nodes_dict]
        self.ui.comboBox_depart.addItems(id_list)
        self.ui.comboBox_arrive.addItems(id_list)
        self.add_node()
        self.path_aerodromes = QtWidgets.QGraphicsItemGroup()
        self.ui.pushButton_recherche.clicked.connect(self.search)

    def adapt_scale(self, coord):
        pt = geometry.Point(coord.long, coord.lat)
        pt.x = (pt.x + 400000) * 600 // 1200000
        pt.y = (5800000 - pt.y) * 600 // 1200000
        return pt

    def add_node(self):
        for id, node in self.graph.nodes_dict.items():
            point = self.adapt_scale(node.coord)
            item = QtWidgets.QGraphicsEllipseItem(point.x, point.y, 6, 6)
            item.setBrush(QtGui.QBrush(QtGui.QColor("#0000CC")))
            self.scene.addItem(item)

    def draw_path(self, path, color, path_width, node_width):
        pen = QtGui.QPen(QtGui.QColor(color), path_width)
        path_graphic = QtGui.QPainterPath()
        w = node_width / 2
        a = self.adapt_scale(self.graph.nodes_dict[path[0]].coord)
        path_graphic.moveTo(a.x + w, a.y + w)
        for k in range(len(path) - 1):
            b = self.adapt_scale(self.graph.nodes_dict[path[k + 1]].coord)
            path_graphic.lineTo(b.x + w, b.y + w)
        item = QtWidgets.QGraphicsPathItem(path_graphic, self.path_aerodromes)
        item.setPen(pen)
        for id in path:
            b = self.adapt_scale(self.graph.nodes_dict[id].coord)
            item2 = QtWidgets.QGraphicsEllipseItem(b.x, b.y, node_width, node_width, self.path_aerodromes)
            item2.setBrush(QtGui.QBrush(QtGui.QColor("#00FFEF")))
        self.scene.addItem(self.path_aerodromes)

    def reinitialize(self, graph):
        for (id, node) in graph.nodes_dict.items():
            node.parent, node.H, node.G = None, 0, 0

    def search(self):
        self.scene.removeItem(self.path_aerodromes)
        self.path_aerodromes = QtWidgets.QGraphicsItemGroup()
        while range(self.ui.listWidget.count()):
            self.ui.listWidget.takeItem(0)
        try:
            self.dep = self.graph.nodes_dict[self.ui.comboBox_depart.currentText()]
            self.arr = self.graph.nodes_dict[self.ui.comboBox_arrive.currentText()]
            self.timeStart = self.ui.timeEdit.text()
            self.v_c = self.ui.spinBox_vitesse.value()
            self.alt_inf = self.ui.spinBox_altinf.value()
            self.alt_sup = self.ui.spinBox_altsup.value()
            self.temps_arret = self.ui.spinBox_tempsdarret.value() * 60
            self.airplane = airplane.Airplane(self.alt_inf, self.alt_sup, self.temps_arret, self.v_c)
            self.flight1 = find_path(self.dep, self.arr, self.timeStart, self.airplane, self.wind3D_dict, self.graph,
                                     True)
            self.reinitialize(self.graph)
            self.flight2 = find_path(self.dep, self.arr, self.timeStart, self.airplane, self.wind3D_dict, self.graph,
                                     False)
            self.draw_path(self.flight2.path, "#BF22B4", 2, 6)
            self.draw_path(self.flight1.path, "#00FF22", 3, 8)
            self.ui.listWidget.addItem(str(self.flight1.path))
            self.ui.listWidget.addItem("durrée minimale = " + str(arbre_oaci.hms(self.flight1.duration)))
            self.ui.listWidget.addItem("altitude optimale = " + str(self.flight1.alt) + " hPa")
            self.ui.listWidget.addItem("durrée sans vent = " + str(arbre_oaci.hms(self.flight2.duration)))

        except ValueError:
            return "no path found"
