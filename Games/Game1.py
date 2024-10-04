import time

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import numpy as np

from Model.ControlBox import ControlsHandler
from Model.Camera import CameraHandler, ImageProcessing
from Model.Instructions import InstructionsPane


class Game1(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi('UI/Game1.ui', self)

        self.InitializeClasses()
        self.InitializeUi()
        self.ConnectSignals()
        self.SetupTimer()

        self.duration = 0
        self.start_time = 0
        self.target = np.array([150, 150])

    def InitializeClasses(self):
        self.Camera = CameraHandler(self)
        self.Controls = ControlsHandler(self)

    def InitializeUi(self):
        self.StartButton = self.findChild(QCheckBox, 'StartButton')
        self.ScoreSpinbox = self.findChild(QSpinBox, 'ScoreSpinbox')
        self.GameTimer = self.findChild(QSpinBox, 'GameTimer')

    def ConnectSignals(self):
        self.StartButton.toggled.connect(self.StartGame)
        self.InstructionsButton.pressed.connect(self.ShowInstructions)

    def SetupTimer(self, fps: int = 30):
        self.timer = QTimer()
        self.timer.start(1000 // fps)

    def StartGame(self):
        if self.StartButton.isChecked():
            if not self.Camera.CameraCheckbox.isChecked():
                self.Camera.CameraCheckbox.setChecked(True)

            self.duration = self.GameTimer.value()
            self.start_time = time.time()
            self.ScoreSpinbox.setValue(0)
            self.target = np.array([150, 150])
            self.timer.timeout.connect(self.GameLogic)

        else:
            self.StopGame()

    def StopGame(self):
        try: self.timer.timeout.disconnect(self.GameLogic)
        except: pass

        self.Camera.OverlayPoint = None
        self.GameTimer.setValue(60)

    def GameLogic(self):
        elapsed_time = time.time() - self.start_time
        if self.StartButton.isChecked() and elapsed_time <= self.duration:
            self.GameTimer.setValue(int(self.duration - elapsed_time))
            self.Camera.points = np.array([[0, 0, 0, 0, 0], [self.target[0], self.target[1], 255, 0, 0]])
            pos = self.Camera.SendRobotPos()

            if pos is not None:
                if np.linalg.norm(self.target - pos) <= 3:
                    self.target = self.RNG()
                    self.Camera.points = np.array([[0, 0, 0, 0, 0], [self.target[0], self.target[1], 255, 0, 0]])
                    self.ScoreSpinbox.setValue(self.ScoreSpinbox.value() + 1)

        else:
            self.StartButton.setChecked(False)
            self.Camera.points = np.zeros((1, 5))

    def RNG(self, max_distance=40):
        phi = np.random.uniform(0, 2 * np.pi)
        r = np.random.uniform(0, max_distance)

        x = r * np.cos(phi) + 150
        y = r * np.sin(phi) + 150

        return np.array([x, y])

    def ShowInstructions(self):
        self.Instructions = InstructionsPane()
        self.Instructions.ShowInstructionsPane(1)
        self.Instructions.show()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.Camera.closeEvent(event)
        self.Controls.closeEvent()
        self.timer.stop()
        self.closed.emit()
