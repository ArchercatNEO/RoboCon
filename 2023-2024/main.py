import asyncio
import math
from time import sleep

from robot import Robot

import servos
from wheels import Wheels

robot = Robot()
async def main() -> int:
    wheels = Wheels(robot.motors)
    servos.open_arms(robot)
    
    x = 0
    y = 0
    theta = 0

    #Find cube
    sheep = robot.see()
    while len(sheep) < 1:
        await wheels.turn(15)
        theta += 5
        await asyncio.sleep(0.5)
        sheep = robot.see()

    #Goto cube
    cube = sheep[0]
    await wheels.turn(cube.bearing.y)
    theta += cube.bearing.y
    await wheels.move(cube.dist)
    x += math.cos(math.radians(theta)) * cube.dist
    y += math.sin(math.radians(theta)) * cube.dist
    servos.close(robot)

    #Goto nearest thing
    direction = math.degrees(math.atan2(4 - y, 1 - x))
    await wheels.turn(direction)
    theta += direction

    distance = math.sqrt((1 - x) ** 2 + (4 - y) ** 2)
    await wheels.move(distance)
    x = 1
    y = 4
    servos.open_arms(robot)
    
    #Return
    returnAngle = math.degrees(math.atan2(-4, -1))
    await wheels.turn(theta - returnAngle)
    theta = returnAngle

    returnDistance = math.sqrt(3 ** 2 + 1 ** 2)
    await wheels.move(returnDistance)
    x = 1
    y = 1

    await wheels.turn(180)
    theta += 180

    print("Exiting main")
    return 0

if __name__ == "__main__":
    sleep(5)
    print("Starting")
    asyncio.run(main())