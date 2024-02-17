import asyncio
import sys

from robot import Robot

from wheels import Wheels

async def main() -> int:
    print("Expecting python3.9")
    print(sys.version)

    robot = Robot()
    wheels = Wheels(robot.motors)

    sheep = robot.see()
    for marker in sheep:
        await wheels.goto(marker)

    await wheels.move(100)

    return 0

if __name__ == "__main__":
    asyncio.run(main())