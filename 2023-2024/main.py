import asyncio
import sys
import robot

from wheels import Wheels

R = robot.Robot()
R.see()

W = Wheels(R.motors)
asyncio.run(W.move(100))

print(sys.version)