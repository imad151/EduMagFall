from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PyQt5 import uic

from Model.Camera import CameraHandler, ImageProcessing
from Model.ControlBox import ControlsHandler
from Model.ColorWheelLogic import PaintWheel


class Game3(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi('UI/Game3.ui', self)

        self.InitializeClasses()
        self.InitUi()
        self.ConnectSignals()

    def InitializeClasses(self):
        self.Controls = ControlsHandler(self)
        self.Camera = CameraHandler(self)
        self.ImageProcessing = ImageProcessing()

    def InitUi(self):
        self.ColorWheelWidget = self.findChild(PaintWheel, "ColorWheel")

    def ConnectSignals(self):
        self.ColorWheelWidget.colorChanged.connect(self.PrintCurrentColor)

    def PrintCurrentColor(self, color):
        print(f'{color}')

    def closeEvent(self, event):
        self.Camera.closeEvent(event)
        self.closed.emit()
        super().closeEvent(event)
