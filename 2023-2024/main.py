import asyncio
import sys

from robot import Robot
from wheels import Wheels

NUMBER_OF_TRAJECTORY_CALCULATIONS_PER_METER = 15

# Motors:
# Right - 0
# Left  - 1

async def search_for_marker(robot, robot_dir, delay):
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

async def main() -> int:
    print("Expecting python3.9")
    print(sys.version)

    robot = Robot()
    wheels = Wheels(robot.motors)

    while True:
        print("Main loop start.")
        marker = await search_for_marker(robot, 1, 0.5)
    
        number_of_trajectory_calculations = int(marker.dist * NUMBER_OF_TRAJECTORY_CALCULATIONS_PER_METER)
        print(f"Traj. Calc. N. = {number_of_trajectory_calculations}")
        for i in range(number_of_trajectory_calculations):
            print("Moving towards marker...")
            await wheels.move(marker.dist / number_of_trajectory_calculations)
    
            print("Rotating towards marker...")
            await wheels.turn(marker.bearing.y / 5) # Divide by 5 to decrease chance of marker getting out of camera FOV

            print("Updating marker info...")
            robot_dir = 1
            if (marker.bearing.y > 0): robot_dir *=- 1 # Search for marker in last direction it has been seen.
            marker = await search_for_marker(robot, robot_dir, 0.5)
    
            print(f"Distance: {marker.dist}m | Angle: {marker.bearing.y} | i: {i}")

            if (marker.dist < 0.4): # Robot reached the marker.
               await wheels.move(0.1) # Move closer to the marker.
               print("Reached the marker.")
               await asyncio.sleep(5)
               break
    
        print("Main loop end.")

    print("Exiting main")
    return 0

if __name__ == "__main__":
    asyncio.run(main())
