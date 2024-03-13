import asyncio
import math
from typing import Tuple, Union

from robot.cytron import CytronBoard
from robot.greengiant import GreenGiantMotors
from robot.marker_setup.teams import TEAM

class Wheels:
    arena_length: int = 6
    angular_speed: float = 72
    linear_speed: float = 0.312

    def __init__(self, motors: Union[GreenGiantMotors, CytronBoard], team: TEAM) -> None:
        print("Wheels have started")
        self.motors = motors
        
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        if team == TEAM.MARIS_PIPER:
            self.x = 0.25
            self.y = Wheels.arena_length - 0.25
            self.angle = -45.0

        if team == TEAM.PURPLE:
            self.x = Wheels.arena_length - 0.25
            self.y = Wheels.arena_length - 0.25
            self.angle = -90.0

        if team == TEAM.RUSSET:
            self.x = Wheels.arena_length - 0.25
            self.y = 0.25
            self.angle = 90.0

        if team == TEAM.SWEET:
            self.x = 0.25
            self.y = 0.25
            self.angle = 45.0

        #Todo use better types instead of tuple
        self.locations: list[Tuple[float, float]] = []
        for i in range(Wheels.arena_length):
            self.locations.append((i + 0.5, Wheels.arena_length))
        for i in range(Wheels.arena_length):
            self.locations.append((Wheels.arena_length, 6.5 - i))
        for i in range(Wheels.arena_length):
            self.locations.append((6.5 - i, 0))
        for i in range(Wheels.arena_length):
            self.locations.append((0, i + 0.5))

    def wall_location(self, wall_id: int) -> Tuple[float, float]:
        return self.locations[wall_id - 100]


    async def snap(self, x: float, y: float) -> None:
        """Snap towards a certain point in space. Handles turning and current position"""
        
        direction = math.atan2(y - self.y, x - self.x)
        direction_degrees = math.degrees(direction)
        
        distance = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        
        await self.turn(direction_degrees)
        await self.move(distance)

    async def move(self, meters: float) -> None:
        """Move `meters` meters forwards. Negative numbers turn backwards"""
        
        sign = int(meters / abs(meters))

        # Motors don't rotate at the same speed.
        self.motors[0] = 100 * sign
        self.motors[1] = 95 * sign

        await asyncio.sleep(meters / Wheels.linear_speed)

        self.x += math.cos(self.theta) * meters
        self.y += math.sin(self.theta) * meters

        self.motors[0] = 0
        self.motors[1] = 0
    
    async def turn(self, degrees: float) -> None:
        """Turn `degress` degrees clockwise. Negative numbers turn anticlockwise"""
        
        sign = int(degrees / abs(degrees)) 

        self.motors[0] = -100  * sign
        self.motors[1] = 95 * sign

        await asyncio.sleep(sign * degrees / Wheels.angular_speed)

        self.theta += math.radians(degrees)

        self.motors[0] = 0
        self.motors[1] = 0
