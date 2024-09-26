import cv2
import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class CameraThread(QThread):
    frame_captured = pyqtSignal(QImage)

    def __init__(self, idx: int = 0):
        super().__init__()
        self.cap = cv2.VideoCapture(idx)
        self.running = True
        self.ImageProcessing = ImageProcessing()

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = self.ImageProcessing.OutputProcessedCameraFrame(frame)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.frame_captured.emit(q_img)

    def start(self, **kwargs):
        self.running = True
        super().start()

    def stop(self):
        print('Stopping Camera thread...')
        self.running = False
        self.quit()
        self.wait()
        if self.cap.isOpened():
            self.cap.release()
            print("Camera resource released.")



class ImageProcessing:
    def __init__(self):
        self.overlay_point = None
        self.frame = None

    def CropImage(self, frame):
        return frame[100:400, 170:470]

    def RotateImage(self, frame):
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

    def OutputProcessedCameraFrame(self, frame):
        if self.overlay_point is None:
            self.frame = self.RotateImage(self.CropImage(frame))
            return self.frame

        else:
            self.frame = self.RotateImage(self.CropImage(frame))
            self.frame = cv2.circle(self.frame, center=(self.overlay_point[0], self.overlay_point[1]), radius=3, color=(0, 0, 255), thickness=-1)
            return self.frame

    def GetPos(self):
        if self.frame is not None:
            Image = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
            ret, BinaryImage = cv2.threshold(Image, 110, 255, cv2.THRESH_BINARY_INV)
            kernel = np.ones((3, 3), np.uint8)
            dilate = cv2.dilate(BinaryImage, kernel, iterations=1)
            contours, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return np.array([cx, cy])

        return None



class CameraHandler:
    def __init__(self, window: QMainWindow):
        self.window = window

        self.CameraThread = CameraThread()
        self.InitializeUi()
        self.ConnectSignals()

    def InitializeUi(self):
        self.CamView = self.window.findChild(QGraphicsView, "CamView")
        self.CameraCheckbox = self.window.findChild(QGroupBox, "CameraCheckbox")

        self.CamScene = QGraphicsScene()
        self.CamView.setScene(self.CamScene)

    def ConnectSignals(self):
        self.CameraCheckbox.toggled.connect(self.CamEnabled)
        self.CameraThread.frame_captured.connect(self.DisplayFrame)

    def CamEnabled(self):
        if self.CameraCheckbox.isChecked():
            if not self.CameraThread.isRunning():
                print("Starting camera thread...")
                self.CameraThread.start()
        else:
            if self.CameraThread.isRunning():
                print("Started Stopping camera thread...")
                self.CameraThread.stop()
                self.CamScene.clear()

    def DisplayFrame(self, frame):
        self.CamScene.clear()
        self.CamScene.addPixmap(QPixmap.fromImage(frame))
        self.CamView.fitInView(self.CamScene.sceneRect(), Qt.KeepAspectRatio)

    def closeEvent(self, event):
        self.CameraThread.stop()
        self.CamScene.clear()
        event.accept()


