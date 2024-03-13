import asyncio
import time

from robot import Robot
from robot.vision import Marker

import servos
from wheels import Wheels

#Sorry dennis for ignoring your code
NUMBER_OF_TRAJECTORY_CALCULATIONS_PER_METER = 15
async def dennis_goto(robot: Robot, wheels: Wheels, marker: Marker):
    number_of_trajectory_calculations = int(marker.dist * NUMBER_OF_TRAJECTORY_CALCULATIONS_PER_METER)
    print(f"Traj. Calc. N. = {number_of_trajectory_calculations}")
    
    for i in range(number_of_trajectory_calculations):
        print("Moving towards marker...")
        await wheels.move(marker.dist / number_of_trajectory_calculations)

        print("Rotating towards marker...")
        await wheels.turn(marker.bearing.y / 5) # Divide by 5 to decrease chance of marker getting out of camera FOV

        print("Updating marker info...")
        marker = robot.see()[0]

        print(f"Distance: {marker.dist}m | Angle: {marker.bearing.y} | i: {i}")

        if (marker.dist < 0.4): # Robot reached the marker.
            await wheels.move(0.1) # Move closer to the marker.
            print("Reached the marker.")
            servos.close(robot)

robot = Robot()
async def main() -> int:
    wheels = Wheels(robot.motors, robot.zone)
    servos.open(robot)

    #Simulate 3 minute time limit in loop
    start_time = time.time()
    while time.time() - start_time > 180:
        
        print("Searching for marker(s)...")
        markers = robot.see()
        
        print(f"Found {len(markers)} marker(s).")
        
        while len(markers) < 1:
            await wheels.turn(15)
            await asyncio.sleep(0.5)
            markers = robot.see()

        marker = markers[0]

        print("Going to 1st marker")
        await wheels.turn(marker.bearing.y)
        await wheels.move(marker.dist)

        print("Proximity detected, grabbing marker")
        servos.close(robot)

        print("Dropping hot potato at (2, 4)")
        await wheels.snap(2, 4)
        servos.open(robot)
        
        print("Dropoff succeded, returning to base")
        await wheels.snap(1, 1)
        await wheels.turn(180)

    print("3 Minutes exeded, exiting successfully")
    return 0

if __name__ == "__main__":
    asyncio.run(main())
