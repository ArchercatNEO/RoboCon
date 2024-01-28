"""The robot module, provides an python interface to the RoboCon hardware and
April tags a marker recognition system. Also performs convince functions for use
by shepherd"""

import importlib

has_picamera = importlib.find_loader("picamera") is not None

if not has_picamera:
    import sys
    import fake_rpi

    sys.modules["RPi"] = fake_rpi.RPi
    sys.modules["RPi.GPIO"] = fake_rpi.RPi.GPIO
    sys.modules["picamera"] = fake_rpi.picamera
    sys.modules["smbus2"] = fake_rpi.smbus

import sys

from .wrapper import Robot, NoCameraPresent
from .greengiant import OUTPUT, INPUT, INPUT_ANALOG, INPUT_PULLUP, PWM_SERVO, TIMER, UltrasonicSensor
from .vision import RoboConUSBCamera
from .marker_setup import (
    MARKER,
    BASE_MARKER,
    ARENA_MARKER,
    POTATO_MARKER,
    MARKER_TYPE,
    TEAM
)

MINIUM_VERSION = (3, 6)
    
__all__ = [
    "Robot",
    "NoCameraPresent",
    "OUTPUT",
    "INPUT",
    "INPUT_ANALOG",
    "INPUT_PULLUP",
    "PWM_SERVO",
    "TIMER",
    "UltrasonicSensor",
    "MARKER",
    "BASE_MARKER",
    "ARENA_MARKER",
    "POTATO_MARKER",
    "MARKER_TYPE",
    "TEAM",
    "RoboConUSBCamera"
]
