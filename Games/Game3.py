from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PyQt5 import uic

from Model.Camera import CameraHandler
from Model.ControlBox import ControlsHandler
from Model.ColorWheelLogic import PaintWheel

import numpy as np


class Game3(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi('UI/Game3.ui', self)

        self.InitializeClasses()
        self.InitUi()
        self.ConnectSignals()
        self.SetupTimer()

        self.color = np.array([[255, 0, 0]])  # default red

    def InitializeClasses(self):
        self.Controls = ControlsHandler(self)
        self.Camera = CameraHandler(self)

    def InitUi(self):
        self.ColorWheelWidget = self.findChild(PaintWheel, "ColorWheel")
        self.JoystickCheckbox = self.findChild(QCheckBox, "JoystickCheckbox")

    def ConnectSignals(self):
        self.ColorWheelWidget.colorChanged.connect(self.ChangeSelectedColor)

    def SetupTimer(self):
        self.timer = QTimer()
        self.timer.start(1000 // 33)
        self.timer.timeout.connect(self.UpdateWheelFromJoystick)
        self.timer.timeout.connect(self.GetJoystickButtons)

    def UpdateWheelFromJoystick(self):
        if self.JoystickCheckbox.isChecked():
            angle = self.Controls.GetRightStickValue()
            if angle is not None:
                self.ColorWheelWidget.UpdateFromJoystickAngle(angle)

    def GetJoystickButtons(self):
        Joy_Input = self.Controls.GetJoyButtons()
        if Joy_Input == 'a':
            self.HandleDraw()
        if Joy_Input == 'start':
            self.ClearAllElements()

    def HandleDraw(self):
        pos = self.Camera.SendRobotPos()
        if pos is not None:
            current_point_mat = np.hstack((pos.reshape(1, -1), self.color))
            self.Camera.AddPoints(current_point_mat)

    def ClearAllElements(self):
        self.Camera.points = np.array([[0, 0, 0, 0, 0]])

    def ChangeSelectedColor(self, color):
        self.color = np.array([[color.red(), color.green(), color.blue()]])

    def closeEvent(self, event):
        super().closeEvent(event)
        self.Camera.closeEvent(event)
        self.Controls.closeEvent()
        self.closed.emit()
