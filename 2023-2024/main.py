import asyncio
import robot

from wheels import Wheels

R = robot.Robot()
W = Wheels(R.motors)
asyncio.run(W.turn(100))