import pygame
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from Model.EduMag import EduMagHandler
from Model.Joystick import JoystickHandler


class ControlsHandler:
    def __init__(self, window: QMainWindow):
        super().__init__()

        self.window = window
        self.Edumag = EduMagHandler(window)
        self.Joystick = JoystickHandler()

        self.InitializeUi()
        self.ConnectSignals()
        self.SendParams()
        self.SetupTimer()


    def InitializeUi(self) -> None:
        self.B_spinbox = self.window.findChild(QDoubleSpinBox, "B_spinbox")
        self.G_spinbox = self.window.findChild(QDoubleSpinBox, "G_spinbox")

        self.B_slider = self.window.findChild(QSlider, "B_slider")
        self.G_slider = self.window.findChild(QSlider, "G_slider")

        self.theta_dial = self.window.findChild(QDial, "theta_dial")
        self.theta_spinbox = self.window.findChild(QSpinBox, "theta_spinbox")

        self.G_Max = self.window.findChild(QDoubleSpinBox, "MaxG")

        self.JoystickCheckbox = self.window.findChild(QCheckBox, "JoystickCheckbox")

    def ConnectSignals(self) -> None:
        self.B_spinbox.valueChanged.connect(self.UpdateMinMax)
        self.G_spinbox.valueChanged.connect(self.UpdateMinMax)

        self.theta_dial.sliderPressed.connect(self.OnDialPressed)
        self.theta_dial.sliderReleased.connect(self.OnDialReleased)
        self.theta_dial.valueChanged.connect(self.OnDialChanged)

        self.JoystickCheckbox.toggled.connect(self.HandleInputType)

    def HandleInputType(self):
        if self.JoystickCheckbox.isChecked():
            if self.Joystick.initialize_joystick():
                self.theta_dial.setEnabled(False)
                self.UpdateJoystickStatus(0)  # Joy Connected
                self.ConnectTimer()
            else:
                self.UpdateJoystickStatus(3)  # Joy Error

        else:
            self.theta_dial.setEnabled(True)
            self.DisconnectTimer()
            self.UpdateJoystickStatus(1)  # Joy Disconnected

    def SetupTimer(self, fps: int=30):
        self.timer = QTimer()
        self.timer.setInterval(1000 // fps)
        self.timer.start()

    def ConnectTimer(self):
        self.timer.timeout.connect(self.JoystickLogic)

    def DisconnectTimer(self):
        try:
            self.timer.timeout.disconnect(self.JoystickLogic)
        except:
            pass

    def JoystickLogic(self):
        angle = self.Joystick.get_angle()
        triggers = self.Joystick.get_triggers()

        if angle is not None:
            self.theta_dial.setValue(self.TranslateThetaToDial(angle))
            self.theta_spinbox.setValue(angle)
            self.SendParams()

        else:
            self.SendParams(send=False)  # sends 0, 0, 0, 0

        self.B_spinbox.setValue(self.B_spinbox.value() + triggers)
        self.UpdateMinMax()
        self.G_spinbox.setValue(self.GetMaxG(self.B_spinbox.value()) * 0.3)

    def GetJoyButtons(self):
        input = self.Joystick.GetJoystickButtons()
        return input

    def GetRightStickValue(self):
        return self.Joystick.MapRightStick()

    def UpdateJoystickStatus(self, idx: int):
        if idx == 0:
            self.JoystickCheckbox.setText(f'Joystick Connected')
        elif idx == 1:
            self.JoystickCheckbox.setText(f'Joystick Disconnected')
        else:
            self.JoystickCheckbox.setText(f"Joystick Error")

    def TranslateThetaToDial(self, theta: int):
        return (360 - theta - 90) % 360

    def SendParams(self, send=True):
        B = self.B_spinbox.value()
        G = self.G_spinbox.value()

        theta = self.NormalizeDialToTheta(self.theta_dial.value())

        if send:
            _ = self.Edumag.GetCurrents(B, G, theta, send)

        else:
            _ = self.Edumag.GetCurrents(0, 0, 0, send=True)

    def NormalizeDialToTheta(self, val: int) -> int:
        return -(val + 90) % 360

    def UpdateMinMax(self):
        B = self.B_spinbox.value()

        b_proximity = (self.B_spinbox.value() / 24) * 100
        self.B_slider.setValue(int(b_proximity))

        g_max = self.GetMaxG(B)
        self.G_spinbox.setMaximum(g_max - g_max * 0.1)
        self.G_Max.setValue(g_max - g_max * 0.1)
        self.G_spinbox.setSingleStep(g_max * 0.1)

        g_proximity = (self.G_spinbox.value() / g_max) * 100
        self.G_slider.setValue(int(g_proximity))

    def GetMaxG(self, B):
        return -38.5633 * B + 997.3362

    def OnDialPressed(self):
        self.SendParams(send=True)

    def OnDialReleased(self):
        self.SendParams(send=False)

    def OnDialChanged(self):
        self.theta_spinbox.setValue(self.NormalizeDialToTheta(self.theta_dial.value()))
        self.SendParams(send=True)

    def closeEvent(self):
        if pygame.get_init():
            self.Joystick.QuitPygame()
