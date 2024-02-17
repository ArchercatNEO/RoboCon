"""
Contains the `Terminator` class
"""
import math
import itertools
import asyncio
import time
from enum import Enum
from typing import Iterable
from robot import Robot
from robot import markers
from robot import vision


def is_arena_marker(marker: vision.Marker) -> bool:
    """
    e
    """
    return marker.info.owner == markers.MARKER_OWNER.ARENA


def is_sheep_marker(marker: vision.Marker) -> bool:
    """
    e
    """
    return marker.info.owner in (markers.MARKER_OWNER.ME, markers.MARKER_OWNER.ANOTHER_TEAM)


class Team(Enum):
    """
    Enum for the different teams
    """
    LEON = 0
    ZHORA = 0
    ROY = 0
    PRIS = 0


class Logging(Enum):
    """
    Enum to set what level of logging we want
    """
    DEBUG = 5
    ZERO = 4
    MAIN = 3
    MINOR = 2
    PEDANTIC = 1
    GET = 0


class Terminator(Robot):
    """
    Custom class to extend the functionality of `Robot`
    """

    max_speed: float = 0
    zero: float
    zone: Team
    locations: list[list[float]]
    x: float
    y: float
    angle: float
    log_level: Logging
    log_list: dict[str, Logging]

    log_list = {
        "move": Logging.PEDANTIC,
        "turn": Logging.PEDANTIC,
        "goto": Logging.MINOR,
        "snap": Logging.MINOR,
        "peek": Logging.PEDANTIC,
        "triangulate": Logging.PEDANTIC,
        "get_power": Logging.GET,
    }

    def __init__(self, max_speed: float, logging: Logging, length: int = 6):
        """
        Initialize the robot and how big the arena is
        """
        super().__init__()

        self.max_speed = max_speed
        self.zero = time.time()
        self.log_level = logging

        # set initial coords to 0.25m either side away from corner and pointing to the center
        match self.zone:

            case Team.LEON:
                self.x = 0.25
                self.y = length - 0.25
                self.angle = -45.0

            case Team.ZHORA:
                self.x = length - 0.25
                self.y = length - 0.25
                self.angle = -90.0

            case Team.ROY:
                self.x = length - 0.25
                self.y = 0.25
                self.angle = 90.0

            case Team.PRIS:
                self.x = 0.25
                self.y = 0.25
                self.angle = 45.0

        # set up the coords of the wall markers to be used in triangulate
        self.locations = []
        for i in range(length):
            self.locations.append([i + 0.5, length])
        for i in range(length):
            self.locations.append([length, 6.5 - i])
        for i in range(length):
            self.locations.append([6.5 - i, 0])
        for i in range(length):
            self.locations.append([0, i + 0.5])

    def now(self):
        """Seconds since we started"""

        return time.time() - self.zero

    def trace(self, parent: str, log: str):
        """
        Print a log if the method's priority is larger than the level
        """
        if self.log_list[parent].value >= self.log_level.value:
            print(log)

    async def move(self, meters: float, speed: float = max_speed):
        """
        Move x meters at max speed.
        Takes additional arguments to go slower.
        """

        self.x += math.cos(self.angle * math.pi / 180) * meters
        self.y += math.sin(self.angle * math.pi / 180) * meters

        self.motors[0] = self.get_power(speed)
        self.motors[1] = self.get_power(speed)

        await asyncio.sleep(meters / speed)

        self.motors[0] = 0
        self.motors[1] = 0

    async def turn(self, degrees: float, speed: float = max_speed):
        """
        Turns x degrees at max speed.
        Takes additional arguments to go slower.
        """

        self.angle += degrees * math.pi / 180

        sign = degrees / abs(degrees)

        self.motors[0] = self.get_power(speed) * sign
        self.motors[1] = self.get_power(speed) * -sign

        await asyncio.sleep(degrees / speed)

        self.motors[0] = 0
        self.motors[1] = 0

    async def goto(self, marker: vision.Marker):
        """
        Uses the properties of a marker object to turn and move towards it.
        """

        await self.turn(marker.bearing.y)
        await self.move(marker.dist)

    async def snap(self, x: float, y: float):
        """
        Uses the robot's position and rotation to move towards a location in the arena.
        """

        x -= self.x
        y -= self.y

        dist = math.sqrt(x ** 2 + y ** 2)
        angle = math.asin(y / dist)

        await self.turn(angle)
        await self.move(dist)

    def get_power(self, speed: float):
        """
        Get the power needed to achieve speed 
        """
        return 100

    # use wall markers and their positions to calculate our position and angle
    def triangulate(self, sheep: list[vision.Marker]):
        """
        Set the x, y and angle of the robot
        """

        mean_x = 0
        mean_y = 0
        mean_angle = 0
        count = 0

        # do the loop for every combination of 2 markers we have, no duplicates
        for marker in itertools.permutations(sheep, 2):
            count += 1

            m1 = marker[0]
            m2 = marker[1]

            x1: float = self.locations[m1.info.id - 100][0]
            x2: float = self.locations[m2.info.id - 100][0]
            y1: float = self.locations[m1.info.id - 100][1]
            y2: float = self.locations[m2.info.id - 100][1]

            d1: float = m1.dist
            d2: float = m2.dist

            a1: float = m1.bearing.y
            a2: float = m2.bearing.y

            # distance between markers (pythagoras)
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            # trig to find an angle (law of sines)
            angle = math.asin(math.sin((a1 - a2) * math.pi / 180) / distance * d2)

            mean_x += math.cos(angle) * d1 - x1
            mean_y += math.sin(angle) * d1 - y1
            mean_angle += a1 + angle

        self.x = mean_x / count
        self.y = mean_y / count
        self.angle = mean_angle / count

    def peek(self):
        """
        Look for markers, feed wall markers to triangulate and return non-wall markers
        """

        marker: Iterable[vision.Marker] = self.see()
        wall = list(filter(is_arena_marker, marker))
        sheep = list(filter(is_sheep_marker, marker))

        self.triangulate(wall)

        return sheep
