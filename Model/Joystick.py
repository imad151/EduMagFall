import pygame
import math

class JoystickHandler:
    def __init__(self):
        pygame.joystick.init()
        self.joystick = None

    def initialize_joystick(self) -> bool:
        """Initializes the joystick, returns False if no joystick is connected, else True"""
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            return False
        else:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            return True

    def get_angle(self, threshold: float=0.1) -> float:
        """Returns the angle in degrees of the left joystick of an Xbox 360 controller"""

        left_x = self.joystick.get_axis(0)
        left_y = self.joystick.get_axis(1)

        if abs(left_x) > threshold or abs(left_y) > threshold:
            angle = int(math.degrees(math.atan2(-left_y, left_x)))
            if angle < 0:
                angle += 360
            return angle

        else:
            return None

    def get_triggers(self, threshold: float=0.1, max_increase: float=0.1):
        """Returns trigger value: +1 for right trigger fully pressed, -1 for left, 0 if both fully pressed"""
        if self.joystick is None:
            return None

        right_trigger = (self.joystick.get_axis(5) + 1) / 2
        left_trigger = (self.joystick.get_axis(4) + 1) / 2

        return (right_trigger - left_trigger) * max_increase