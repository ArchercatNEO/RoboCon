import asyncio
import robot
import time

R = robot.Robot()


front_prox = False
def printval():
    print("xx: "+str(front_prox))

    
async def check_front_prox_loop():
    while True:
        if not R.gpio[0].digital:
            global front_prox
            front_prox = True
            print(front_prox)
            time.sleep(1)
            break
    printval()




loop = asyncio.get_event_loop()
loop.run_until_complete(check_front_prox_loop())
