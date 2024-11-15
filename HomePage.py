import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic


class HomePage(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi("UI/HomePage.ui", self)

        self.InitializeUi()
        self.ConnectSignals()

        self.CurrentGame = None

    def InitializeUi(self):
        self.HomeButton = self.findChild(QPushButton, "HomeButton")
        self.Game1Button = self.findChild(QPushButton, "Game1Button")
        self.Game2Button = self.findChild(QPushButton, "Game2Button")
        self.Game3Button = self.findChild(QPushButton, "Game3Button")
        self.Game4Button = self.findChild(QPushButton, "Game4Button")
        self.ExitButton = self.findChild(QPushButton, "ExitButton")

    def ConnectSignals(self):
        self.HomeButton.pressed.connect(lambda: self.LaunchGame(0))
        self.Game1Button.pressed.connect(lambda: self.LaunchGame(1))
        self.Game2Button.pressed.connect(lambda: self.LaunchGame(2))
        self.Game3Button.pressed.connect(lambda: self.LaunchGame(3))
        self.Game4Button.pressed.connect(lambda: self.LaunchGame(4))
        self.ExitButton.pressed.connect(self.CloseAll)

    def LaunchGame(self, idx: int) -> None:
        if self.CurrentGame:
            self.CurrentGame.close()
        self.hide()

        if idx == 0:
            from MainPage import MainWindow
            self.CurrentGame = MainWindow()

        if idx == 1:  # Whack a Mole
            from Games.Game1 import Game1
            self.CurrentGame = Game1()

        if idx == 2:  # Maze Navigator
            from Games.Game2 import Game2
            self.CurrentGame = Game2()

        if idx == 3:  # Paint
            from Games.Game3 import Game3
            self.CurrentGame = Game3()

        if idx == 4:  # Route Designer
            from Games.Game4 import Game4
            self.CurrentGame = Game4()

        self.CurrentGame.showMaximized()
        self.CurrentGame.closed.connect(self.OnGameClosed)

    def OnGameClosed(self):
        self.CurrentGame = None
        self.showMaximized()

    def CloseAll(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myapp = HomePage()
    myapp.showMaximized()
    sys.exit(app.exec_())

