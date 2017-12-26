import arbre_oaci
import wind
import geometry
import py_airplane
from ui_interface import Ui_Interface
from PyQt5 import QtCore, QtGui, QtWidgets
import math
import numpy as np

ERROR_1 = "fichier incorect. Veillez selectionner à nouveau"
ERROR_2 = "Pas de chemin trouvé. Essayez de modifier les entrées"
ERROR_3 = "Une erreur est survenue. Vérifiez les données entrées"


def create_wind3D_dict(files):
    wind3D_dict = {}
    for file in files:
        for (date, wind3D) in wind.from_file(file).items():
            wind3D_dict[date] = wind3D
    return wind3D_dict


def find_path(dep, arr, timeStart, airplane, wind3D_dict, graphe, with_wind):
    if with_wind:
        dico = {}
        for pression in range(airplane.pression_inf, airplane.pression_sup + 100, 100):
            flight = arbre_oaci.Flight(dep, arr, pression, arbre_oaci.time(timeStart))
            dico[pression] = arbre_oaci.astar(flight, airplane, wind3D_dict, graphe, with_wind)
        return min(dico.values(), key=lambda x: x.duration)
    flight = arbre_oaci.Flight(dep, arr, airplane.pression_inf, arbre_oaci.time(timeStart))
    return arbre_oaci.astar(flight, airplane, wind3D_dict, graphe, with_wind)


def get_direction(a, b):
    ab = b - a
    if abs(ab.x) - abs(ab.y) > 0:
        return 4 if ab.x > 0 else 0
    elif abs(ab.x) == abs(ab.y) == 0:
        return 8
    else:
        return 2 if ab.y > 0 else 6


class ErrorWidget(QtWidgets.QDialog):
    def __init__(self, ihm, mes):
        super().__init__(ihm)
        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.setWindowTitle("Message d'erreur")
        message = QtWidgets.QLabel()
        message.setText(mes)
        button = QtWidgets.QPushButton("OK")
        button.setMaximumSize(100, 20)
        button.clicked.connect(self.close)
        self.vlayout.addWidget(message)
        self.vlayout.addWidget(button, alignment=QtCore.Qt.AlignRight)
        self.show()


class RoseDesVent(QtWidgets.QGraphicsItemGroup):
    def __init__(self, p0=np.array([50, 550])):
        super().__init__()
        self.p0 = p0
        self.roseItem = QtWidgets.QGraphicsPathItem()
        self.dirItem = QtWidgets.QGraphicsPathItem()

        def produit(x, A):
            n = len(x)
            y = np.zeros(n)
            for j in range(n):
                yj = 0
                for i in range(n):
                    yj += x[i] * A[i][j]
                y[j] = yj
            return y

        A = np.array([[0, 1], [-1, 0]])
        po = np.array([-40, 0])
        pno = np.array([-5, -5])
        self.l = [po, pno]
        for i in range(3):
            po = produit(po, A)
            self.l.append(po)
            pno = produit(pno, A)
            self.l.append(pno)

    def draw(self, s=8):
        painter = QtGui.QPainterPath()
        if s == 8:
            painter.moveTo((self.l[0] + self.p0)[0], (self.l[0] + self.p0)[1])
            pen = QtGui.QPen(QtGui.QColor("grey"), 2)
            for i in range(1, len(self.l)):
                painter.lineTo((self.l[i] + self.p0)[0], (self.l[i] + self.p0)[1])
            painter.lineTo((self.l[0] + self.p0)[0], (self.l[0] + self.p0)[1])
            painter.moveTo((self.l[1] + self.p0)[0], (self.l[1] + self.p0)[1])
            painter.lineTo((self.l[5] + self.p0)[0], (self.l[5] + self.p0)[1])
            painter.moveTo((self.l[3] + self.p0)[0], (self.l[3] + self.p0)[1])
            painter.lineTo((self.l[7] + self.p0)[0], (self.l[7] + self.p0)[1])
            self.roseItem = QtWidgets.QGraphicsPathItem(painter, self)
            self.roseItem.setPen(pen)
        else:
            self.removeFromGroup(self.dirItem)
            pen = QtGui.QPen(QtGui.QColor("#00FF22"), 4)
            painter.moveTo(self.p0[0], self.p0[1])
            for i in range(-1, 2):
                painter.lineTo((self.l[s + i] + self.p0)[0], (self.l[s + i] + self.p0)[1])
            painter.lineTo(self.p0[0], self.p0[1])
            self.dirItem = QtWidgets.QGraphicsPathItem(painter, self)
            self.dirItem.setPen(pen)


class NodeItems(QtWidgets.QGraphicsItemGroup):
    def __init__(self, ihm, node):
        super().__init__()
        self.ihm = ihm
        self.node = node
        a = self.node.coord.adapt_scale()
        self.nodeItem = QtWidgets.QGraphicsEllipseItem(a.x, a.y, 6, 6, self)
        self.nodeItem.setBrush(QtGui.QBrush(QtGui.QColor("#0000CC")))
        self.nodeItem.setToolTip(self.node.id)


class Windlocal_Item(QtWidgets.QGraphicsItemGroup):
    def __init__(self, ihm, windlocal):
        super().__init__()
        self.ihm = ihm
        self.windlocal = windlocal
        pen = QtGui.QPen(QtGui.QColor("#003366"), 1)
        vectPainter = QtGui.QPainterPath()
        p1, p2, p3, p4 = self.windlocal.arrow_repr()
        vectPainter.addEllipse(p1[0], p1[1], 2, 2)
        vectPainter.moveTo(p1[0] + 1, p1[1] + 1)
        vectPainter.lineTo(p2[0] + 1, p2[1] + 1)
        self.vectItem = QtWidgets.QGraphicsPathItem(vectPainter, self)
        self.vectItem.setPen(pen)


class WindPlan_Item(QtWidgets.QGraphicsItemGroup):
    def __init__(self, ihm, windPlan):
        super().__init__()
        self.ihm = ihm
        self.windPlan = windPlan
        for wind in self.windPlan.dict.values():
            self.addToGroup(Windlocal_Item(self.ihm, wind))


class PanZoomView(QtWidgets.QGraphicsView):
    """An interactive view that supports Pan and Zoom functions"""

    def __init__(self, scene):
        super().__init__(scene)
        # enable anti-aliasing
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        # enable drag and drop of the view
        # self.setDragMode(self.ScrollHandDrag)

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
        self.path_Group = QtWidgets.QGraphicsItemGroup()
        self.nodes_Group = QtWidgets.QGraphicsItemGroup()
        self.windPlanItem = None
        self.rose = RoseDesVent()
        self.scene.addItem(self.rose)

        self.ui.pushButton_a.clicked.connect(self.load_nodes)
        self.ui.pushButton_v.clicked.connect(self.load_winds)
        self.ui.pushButton_recherche.clicked.connect(self.search)
        self.ui.pushButton_save.clicked.connect(self.save_data)

    def load_nodes(self):
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Charger les aérodromes", "", "Text Files (*.txt)",
                                                            options=options)
        if filename:
            try:
                self.graph = arbre_oaci.arbre_creation(filename)
                self.add_nodes()
            except Exception:
                error_windows = ErrorWidget(self, ERROR_1)

    def add_nodes(self):
        self.scene.removeItem(self.nodes_Group)
        self.nodes_Group = QtWidgets.QGraphicsItemGroup()
        for id, node in self.graph.nodes_dict.items():
            self.ui.comboBox_depart.addItem(id)
            self.ui.comboBox_arrive.addItem(id)
            item = NodeItems(self, node)
            self.nodes_Group.addToGroup(item)
            self.scene.addItem(self.nodes_Group)
        self.rose.draw()

    def load_winds(self):
        options = QtWidgets.QFileDialog.Options()
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Charger les aérodromes", "", "Text Files (*.txt)",
                                                          options=options)
        if files:
            try:
                self.wind3D_dict = create_wind3D_dict(files)
                self.add_windPlan(self.wind3D_dict[20171104060000].dict[400])
            except Exception:
                error_windows = ErrorWidget(self, ERROR_1)

    def add_windPlan(self, windPlan):
        if self.windPlanItem:
            self.scene.removeItem(self.windPlanItem)
        self.windPlanItem = WindPlan_Item(self, windPlan)
        self.scene.addItem(self.windPlanItem)

    def draw_path(self, flight, color, path_width, node_width):
        pen = QtGui.QPen(QtGui.QColor(color), path_width)
        painter = QtGui.QPainterPath()
        w = node_width / 2
        a = flight.dep.coord.adapt_scale()
        painter.moveTo(a.x + w, a.y + w)
        for k in range(len(flight.path) - 1):
            b = self.graph.nodes_dict[flight.path[k + 1]].coord.adapt_scale()
            painter.lineTo(b.x + w, b.y + w)
        item = QtWidgets.QGraphicsPathItem(painter, self.path_Group)
        item.setPen(pen)
        item.setToolTip("Trajectoire avec vent") if node_width >= 8 else item.setToolTip("Trajectoire sans vent")
        for id in flight.path:
            b = self.graph.nodes_dict[id].coord.adapt_scale()
            item2 = QtWidgets.QGraphicsEllipseItem(b.x, b.y, node_width, node_width, self.path_Group)
            item2.setBrush(QtGui.QBrush(QtGui.QColor("#00FFEF")))
            item2.setToolTip(id)
        self.scene.addItem(self.path_Group)
        self.rose.draw(get_direction(flight.dep.coord, flight.arr.coord))

    def reinitialize(self, graph):
        for (id, node) in graph.nodes_dict.items():
            node.parent, node.H, node.G = None, 0, 0

    def search(self):
        self.scene.removeItem(self.path_Group)
        self.path_Group = QtWidgets.QGraphicsItemGroup()
        while range(self.ui.listWidget.count()):
            self.ui.listWidget.takeItem(0)
        try:
            dep = self.graph.nodes_dict[self.ui.comboBox_depart.currentText()]
            arr = self.graph.nodes_dict[self.ui.comboBox_arrive.currentText()]
            timeStart = self.ui.timeEdit.text()
            v_c = self.ui.spinBox_vitesse.value()
            pression_inf = self.ui.spinBox_pression_inf.value()
            pression_sup = self.ui.spinBox_pression_sup.value()
            temps_arret = self.ui.spinBox_tempsdarret.value() * 60
            airplane = py_airplane.Airplane(pression_inf, pression_sup, temps_arret, v_c)
            self.flight1 = find_path(dep, arr, timeStart, airplane, self.wind3D_dict, self.graph, True)
            self.reinitialize(self.graph)
            flight2 = find_path(dep, arr, timeStart, airplane, self.wind3D_dict, self.graph, False)
            self.draw_path(flight2, "#BF22B4", 2, 6)
            self.draw_path(self.flight1, "#00FF22", 3, 8)
            self.ui.listWidget.addItem("chemin avec vent : " + str(self.flight1.path))
            self.ui.listWidget.addItem("durée minimale = " + str(arbre_oaci.hms(self.flight1.duration)))
            self.ui.listWidget.addItem("pression optimale = " + str(self.flight1.pression) + " hPa")
            self.ui.listWidget.addItem("durée sans vent = " + str(arbre_oaci.hms(flight2.duration)))
            self.ui.pushButton_save.setEnabled(True)
        except arbre_oaci.NoPathError:
            error_window = ErrorWidget(self, ERROR_2)
        except Exception:
            error_window = ErrorWidget(self, ERROR_3)

    def load_saveFile(self):
        options = QtWidgets.QFileDialog.Options()
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Charger les aérodromes", "", "Text Files (*.txt)",
                                                        options=options)
        if file:
            try:
                self.wind3D_dict = create_wind3D_dict(file)
                self.add_windPlan(self.wind3D_dict[20171104060000].dict[400])
            except Exception:
                error_windows = ErrorWidget(self, ERROR_1)

    def save_data(self):
        options = QtWidgets.QFileDialog.Options()
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Charger les aérodromes", "", "Text Files (*.txt)",
                                                        options=options)
        if file:
            with open(file, "a") as f:
                f.write("\nDepart            : " + str(self.flight1.dep.id))
                f.write("\nArrive            : " + str(self.flight1.arr.id))
                f.write("\nHeure de depart   : " + str(arbre_oaci.hms(self.flight1.time_start)))
                f.write("\nChemin optimal    : " + str(self.flight1.path))
                f.write("\nduree minimale    = " + str(self.flight1.duration) + " sec")
                f.write("\npression optimale = " + str(self.flight1.pression) + " hPa\n")