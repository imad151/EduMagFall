import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import pyqtSignal

from Model.Camera import CameraHandler
from Model.ControlBox import ControlsHandler

from Model.Instructions import InstructionsPane


class MainWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("UI/MainPage.ui", self)
        self.InitializeClasses()

        self.InstructionsButton.pressed.connect(self.ShowInstructions)

    def InitializeClasses(self):
        self.Camera = CameraHandler(self)
        self.Controls = ControlsHandler(self)

    def ShowInstructions(self):
        self.InstructionsPane = InstructionsPane()
        self.InstructionsPane.ShowInstructionsPane(0)
        self.InstructionsPane.show()

    def closeEvent(self, event):
        self.Camera.closeEvent(event)
        self.closed.emit()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myapp = MainWindow()
    myapp.showMaximized()
    sys.exit(app.exec_())

