import asyncio
from typing import Union

from robot.apriltags3 import Detection
from robot.cytron import CytronBoard
from robot.greengiant import GreenGiantMotors

class Wheels:
    angular_speed: float = 60
    linear_speed: float = 0.1

    def __init__(self, motors: Union[GreenGiantMotors, CytronBoard]) -> None:
        print("Wheels have started")
        self.motors = motors

    async def goto(self, marker: Detection) -> None:
        await self.turn(marker.bearing.y)
        await self.move(marker.dist)
    
    async def move(self, meters: float) -> None:
        sign = int(meters / abs(meters))

        self.motors[0] = 95 * sign
        self.motors[1] = 100 * sign

        await asyncio.sleep(meters / Wheels.linear_speed)

        self.motors[0] = 0
        self.motors[1] = 0
    
    async def turn(self, degrees: float) -> None:
        sign = int(degrees / abs(degrees)) 

        self.motors[0] = -100  * sign
        self.motors[1] = 100 * sign

        await asyncio.sleep(sign * degrees / Wheels.angular_speed)

        self.motors[0] = 0
        self.motors[1] = 0