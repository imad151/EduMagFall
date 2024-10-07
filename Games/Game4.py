from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from PyQt5 import uic

from Model.Camera import CameraHandler
from Model.ControlBox import ControlsHandler

import numpy as np
import random


class Game3(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi('Game4.ui', self)

        self.InitializeUi()
        self.InitializeClasses()
        self.ConnectSignals()

    def InitializeUi(self):
        self.StartButton = self.findChild(QCheckBox, "StartGame")
        self.CheckButton = self.findChild(QPushButton, "CheckButton")

    def InitializeClasses(self):
        self.Camera = CameraHandler(self)
        self.Controls = ControlsHandler(self)

    def ConnectSignals(self):
        self.StartButton.toggled.connect(self.StartGame)
        self.CheckButton.pressed.connect(self.AnalyzeUserInput)

    def StartGame(self):
        if self.StartButton.isChecked():
            self.GenerateNodes()
        else:
            self.EndGame()

    def EndGame(self):...

    def GenerateNodes(self, num_nodes=5, grid_size=100, max_distance=50, min_distance=20):
        """
        Nodes will be a numpy array of size (num_nodes, coords of each node)
        :param grid_size:
        :param num_nodes:
        :param max_distance:
        :param min_distance:
        :return:
        """
        phi = np.random.uniform(0, 2 * np.pi)
        r = np.random.uniform(min_distance, max_distance)

        for _ in range(num_nodes):
            node_x = 150 + (r * np.cos(phi))
            node_y = 150 + (r * np.sin(phi))

            self.nodes = np.column_stack((node_x, node_y))


