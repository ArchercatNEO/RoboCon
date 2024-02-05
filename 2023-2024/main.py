import time
import robot

from wheels import Wheels

R = robot.Robot()
W = Wheels(R.motors)
R.see()
while True:
    print("Running stuff")
    time.sleep(1)