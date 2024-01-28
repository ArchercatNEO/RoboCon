"""A script for getting the focal length luts for a camera
It losely follows the ideas of a PD controller combinded with a NM gradient
descent algo.
Usage:
import robot.calibrate_camera
"""
TARGET = 3.0
THRESHOLD = 0.01
KP = 100
KD = 5
K_READING_COUNTS = 0.5


def get_reading() -> float: pass
def get_reading_number(error: float) -> int: pass