import cv2
import numpy as np

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class CameraThread(QThread):
    frame_captured = pyqtSignal(np.ndarray)

    def __init__(self, idx: int = 0):
        super().__init__()
        self.cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        self.running = False
        self.ImageProcessing = ImageProcessing()

    def run(self):
        while self.running:
            if not self.running:
                break
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = self.ImageProcessing.OutputProcessedCameraFrame(frame)
                if frame is not None:
                    self.frame_captured.emit(frame)

    def start(self, **kwargs):
        self.running = True
        super().start()

    def stop(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.quit()
        self.wait()


class ImageProcessing:
    def __init__(self):
        self.frame = None

    def CropImage(self, frame):
        return frame[100:400, 170:470]

    def RotateImage(self, frame):
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

    def OutputProcessedCameraFrame(self, frame, color=(255, 0, 0), dotPoint=None, linePoint=None):
        if dotPoint is not None:
            cv2.circle(frame, center=(dotPoint[0], dotPoint[1]), radius=3, color=color, thickness=-1)
            return frame

        if linePoint is not None:
            cv2.line(frame, (linePoint[0],  linePoint[1]), (linePoint[2], linePoint[3]), color=color, thickness=2)
            return frame

        else:
            frame = self.RotateImage(self.CropImage(frame))
            return frame

    def GetPos(self, frame):
        if frame is not None:
            Image = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
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
        self.ImageProcessing = ImageProcessing()

        self.InitializeUi()
        self.ConnectSignals()
        self.StartThread()

        self.ShowFrame = False
        self.frame = None

        self.points = np.array([[0, 0, 0, 0, 0]])


    def InitializeUi(self):
        self.CamView = self.window.findChild(QGraphicsView, "CamView")
        self.CameraCheckbox = self.window.findChild(QGroupBox, "CameraCheckbox")

        self.CamScene = QGraphicsScene()
        self.CamView.setScene(self.CamScene)

    def ConnectSignals(self):
        self.CameraCheckbox.toggled.connect(self.CamEnabled)
        self.CameraThread.frame_captured.connect(self.DisplayFrame)

    def StartThread(self):
        self.CameraThread.start()

    def CamEnabled(self):
        if self.CameraCheckbox.isChecked():
            self.ShowFrame = True
        else:
            self.ShowFrame = False

    def DisplayFrame(self, frame):
        if self.ShowFrame:
            self.CamScene.clear()
            self.frame = frame
            try: self.DrawElements()
            except: pass
            h, w, ch = self.frame.shape
            bytes_per_line = ch * w
            q_img = QImage(self.frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.CamScene.addPixmap(QPixmap.fromImage(q_img))
            self.CamView.fitInView(self.CamScene.sceneRect(), Qt.KeepAspectRatio)
        else:
            self.CamScene.clear()

    def AddPoints(self, point_matrix):
        self.points = np.vstack((self.points, point_matrix))

    def DrawElements(self):
        m, n = self.points.shape
        if np.all(self.points): pass  # pass if all elements are 0
        else:
            if m <= 2 and np.any(self.points):
                color = tuple(int(c) for c in self.points[1][2:5])
                cv2.circle(self.frame,
                           (int(self.points[1][0]), int(self.points[1][1])),
                           thickness=-1, color=color,
                           radius=3)
            elif m > 2:
                for i in range(1, m - 1):
                    color = tuple(int(c) for c in self.points[i][2:5])
                    cv2.line(self.frame,
                             (int(self.points[i][0]), int(self.points[i][1])),
                             (int(self.points[i + 1][0]), int(self.points[i + 1][1])),
                             color=color, thickness=1)
            else:
                pass

    def SendRobotPos(self):
        return self.ImageProcessing.GetPos(self.frame)

    def SaveFrame(self, file_name='img.png'):
        cv2.imwrite(file_name, cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))

    def closeEvent(self, event):
        self.points = np.array([0, 0, 0, 0, 0])
        self.CameraThread.stop()
        self.CamScene.clear()
        event.accept()
