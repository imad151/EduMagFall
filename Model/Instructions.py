import sys

from PyQt5 import uic
from PyQt5.QtWidgets import *


class InstructionsPane(QMainWindow):
    def __init__(self):
        super().__init__()

    def ShowInstructionsPane(self, idx: int) -> None:
        if idx == 0:  # For MainPage
            uic.loadUi('UI/InstructionsMain.ui', self)

        if idx == 1:  # Game 1
            uic.loadUi('UI/Game1Instructions.ui', self)

        if idx == 2:  # Game 2
            uic.loadUi('UI/Game2Instructions.ui', self)

