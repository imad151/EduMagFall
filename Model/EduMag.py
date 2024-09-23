import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')


class EduMag:
    def __init__(self):
        self.B_vec = np.array([[-0.00340, -0.00030, 0.00340, 0.00030], [-0.00030, 0.00340, 0.00030, -0.00340]])
        self.Grad_X = np.array([[-0.23960, 0.16450, -0.23960, 0.16450], [-0.00620, 0.00680, -0.00620, 0.00680]])
        self.Grad_Y = np.array([[-0.00680, 0.00620, -0.00680, 0.00620], [0.16450, -0.23960, 0.16450, -0.23960]])

    def SetFieldForce(self, B: float, F: float, theta: int) -> np.array:
        B /= 1000
        F /= 1000
        theta = np.deg2rad(theta)

        if B == 0:
            return np.array([0, 0, 0, 0])

        unit = np.array([np.cos(theta), np.sin(theta)])

        Breq = np.round(unit * B, 3)
        Freq = np.round(unit * F, 3)

        Sol = np.vstack((self.B_vec, unit.dot(self.Grad_X), unit.dot(self.Grad_Y)))
        I = np.round(np.linalg.pinv(Sol).dot(np.hstack((Breq, Freq))), 3)

        if np.any(I) >= 4:
            return np.array([0, 0, 0, 0])

        else:
            return I


class PlotVectorField:
    def __init__(self):
        self.InitData()
        self.InitPlot()

    def InitData(self):
        self.df = pd.read_excel("Model/VecField_Data.xlsx")

        self.X = self.df['X'].values
        self.Y = self.df['Y'].values

        self.BiX = self.df[['B1X', 'B2X', 'B3X', 'B4X']].values
        self.BiY = self.df[['B1Y', 'B2Y', 'B3Y', 'B4Y']].values

    def InitPlot(self):
        self.fig, self.ax = plt.subplots()
        self.quiver = self.ax.quiver(self.X, self.Y, self.X * 0, self.X * 0, self.X * 0, cmap='jet')
        self.colorbar = self.fig.colorbar(self.quiver, ax=self.ax, label='Bnet')

        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.grid()


    def DrawField(self, I):
        I = I[:, np.newaxis]

        BXnet = np.sum(self.BiX * I.T, axis=1)
        BYnet = np.sum(self.BiY * I.T, axis=1)

        Bnet = np.sqrt(BXnet ** 2 + BYnet ** 2)

        try:
            self.quiver.set_UVC(BXnet * 1000.0, BYnet * 1000.0, Bnet * 1000.0)
            self.quiver.set_array(Bnet * 1000.0)
            self.quiver.set_clim(vmin=np.min(Bnet * 1000.0), vmax=np.max(Bnet * 1000.0))
            self.quiver.scale = np.max(Bnet * 1000.0) * 10
            self.colorbar.update_normal(self.quiver)

        except Exception as e:
            print(f'Error drawing Field: {e}')
            pass


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Model.SerialComm import Serial


class EduMagHandler:
    def __init__(self, window):
        super().__init__()

        self.window = window
        self.Edumag = EduMag()
        self.PlotVectorField = PlotVectorField()
        self.Serial = Serial()
        _ = self.Serial.open('/dev/ttyUSB0')

        self.InitializeUi()

    def InitializeUi(self):
        self.VecView = self.window.findChild(QGraphicsView, 'VecView')
        if self.VecView is not None:
            self.VecScene = QGraphicsScene()
            self.VecView.setScene(self.VecScene)
        self.CurrentsLabel = self.window.findChild(QLabel, "CurrentsLabel")

    def GetCurrents(self, B: float, G: float, theta: int, send=True) -> np.ndarray:
        I = self.Edumag.SetFieldForce(B, G, theta)
        if send:
            self.UpdateLabels(I)
            if np.any(I) != 0:
                self.PlotVectorField.DrawField(I)
                self.PlotField(self.PlotVectorField.fig)

        return I

    def PlotField(self, fig):
        if self.VecView is not None:
            fig.canvas.draw()
            w, h = fig.canvas.get_width_height()
            q_img = QImage(fig.canvas.buffer_rgba(), w, h, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(q_img)
            if self.VecScene.items():
                pixmap_item = self.VecScene.items()[0]
                pixmap_item.setPixmap(pixmap)

            else:
                self.VecScene.addItem(QGraphicsPixmapItem(pixmap))
            self.ResizeVecField()
        else:
            pass

    def UpdateLabels(self, I):
        if self.CurrentsLabel is not None:
            self.CurrentsLabel.setText(f'I1 = {I[0]}A, I2 = {I[1]}A, I3 = {I[2]}A, I4 = {I[3]}A ')

    def SendCurrents(self, I):
        try:
            self.Serial.send(I)
            print(f'Currents Sent: {I}')
        except Exception as e:
            print(f'Error Sending Current: {e}')
            pass

    def ResizeVecField(self):
        self.VecView.fitInView(self.VecScene.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self):
        self.ResizeVecField()