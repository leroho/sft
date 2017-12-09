import sys
from PyQt5.QtWidgets import QApplication
from interface import IHM

app = QApplication(sys.argv)
my_IHM = IHM()
my_IHM.show()
sys.exit(app.exec_())
