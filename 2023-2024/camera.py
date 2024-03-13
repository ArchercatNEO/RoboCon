import itertools
import math
from typing import Iterable

from robot.vision import Marker
from robot.wrapper import Robot

from wheels import Wheels

def triangulate(wheels: Wheels, sheep: Iterable[Marker]):
    """Set the x, y and angle of the robot based on the wall markers"""

    total_x = 0.0
    total_y = 0.0
    total_angle = 0.0

    count = 0
    # do the loop for every combination of 2 markers we have, no duplicates
    for marker in itertools.permutations(sheep, 2):

        m1 = marker[0]
        m2 = marker[1]

        x1: float = wheels.wall_location(m1.info.id)[0]
        x2: float = wheels.wall_location(m2.info.id)[0]
        y1: float = wheels.wall_location(m1.info.id)[1]
        y2: float = wheels.wall_location(m2.info.id)[1]

        d1: float = m1.dist
        d2: float = m2.dist

        a1: float = m1.bearing.y
        a2: float = m2.bearing.y

        # distance between markers (pythagoras)
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        # trig to find an angle (law of sines)
        angle = math.asin(math.sin(math.radians(a1 - a2)) / distance * d2)

        total_x += math.cos(angle) * d1 - x1
        total_y += math.sin(angle) * d1 - y1
        total_angle += a1 + angle
        count += 1

    wheels.x = total_x / count
    wheels.y = total_y / count
    wheels.theta = total_angle / count

def peek(robot: Robot, wheels: Wheels) -> list[Marker]:
    """Look for markers, feed wall markers to triangulate and return non-wall markers"""

    markers = robot.see()

    wall = filter(lambda marker: marker.info.id > 100, markers)
    triangulate(wheels, wall)

    sheep = filter(lambda marker: marker.info.id < 100, markers)
    return list(sheep) 