import asyncio
import math
from time import sleep

from robot import Robot

import servos
from wheels import Wheels

NUMBER_OF_TRAJECTORY_CALCULATIONS_PER_METER = 15

#does not keep track of position or rotation
async def search_for_marker(robot: Robot, robot_dir: int, delay: float):
    print("Searching for marker(s)...")
    markers = robot.see()
    print(f"Found {len(markers)} marker(s).")

    while len(markers) < 1:
        print("Rotating to find new marker(s).")

        robot.motors[0] = 100 * robot_dir
        robot.motors[1] =-100 * robot_dir
        await asyncio.sleep(0.2)

        robot.motors[0] = 0
        robot.motors[1] = 0
        await asyncio.sleep(delay)

        markers = robot.see()

    return markers[0]

robot = Robot()
async def main() -> int:
    wheels = Wheels(robot.motors)
    servos.open_arms(robot)
    
    x = 0
    y = 0
    theta = 0

    while True:
        print("Finding cube")
        cube = await search_for_marker(robot, 1, 0.5)

        print("Going to cube")
        
        #Dennis goto
        number_of_trajectory_calculations = int(cube.dist * NUMBER_OF_TRAJECTORY_CALCULATIONS_PER_METER)
        print(f"Traj. Calc. N. = {number_of_trajectory_calculations}")
        
        for i in range(number_of_trajectory_calculations):
            print("Moving towards marker...")
            await wheels.move(cube.dist / number_of_trajectory_calculations)
            x += math.cos(math.radians(theta)) * cube.dist
            y += math.sin(math.radians(theta)) * cube.dist
    
            print("Rotating towards marker...")
            await wheels.turn(cube.bearing.y / 5) # Divide by 5 to decrease chance of marker getting out of camera FOV
            theta += cube.bearing.y / 5

            print("Updating marker info...")
            robot_dir = 1
            if (cube.bearing.y > 0): robot_dir *=- 1 # Search for marker in last direction it has been seen.
            cube = await search_for_marker(robot, robot_dir, 0.5)
    
            print(f"Distance: {cube.dist}m | Angle: {cube.bearing.y} | i: {i}")

            if (cube.dist < 0.4): # Robot reached the marker.
               await wheels.move(0.1) # Move closer to the marker.
               print("Reached the marker.")
               servos.close(robot)
               

        #Ernesto goto
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
