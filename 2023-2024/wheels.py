import asyncio
from typing import Union

from robot.cytron import CytronBoard
from robot.greengiant import GreenGiantMotors

class Wheels:
    def __init__(self, motors: Union[GreenGiantMotors, CytronBoard]) -> None:
        print("Wheels have started")
        self.motors = motors
    
    async def move(self, meters: int) -> None:
        sign = int(meters / abs(meters))

        self.motors[0] = 100 * sign
        self.motors[1] = 100 * sign

        await asyncio.sleep(meters / 20)

        self.motors[0] = 0
        self.motors[1] = 0
    
    async def turn(self, degrees: int) -> None:
        sign = int(degrees / abs(degrees))

        self.motors[0] = 100 * sign
        self.motors[1] = 100 * -sign

        await asyncio.sleep(degrees / 20)

        self.motors[0] = 0
        self.motors[1] = 0