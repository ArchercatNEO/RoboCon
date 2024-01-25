import asyncio
import terminator

R = terminator.Terminator(10)

async def movement():
    pass

async def arms():
    pass

async def camera():
    pass

async def collision():
    pass

asyncio.coroutine(movement)
asyncio.coroutine(arms)
asyncio.coroutine(camera)
asyncio.coroutine(collision)

state: str = "None"


asyncio.run(R.move(1))

while True:


    while state == "Moving To Pen":
        pass

    while state == "Finding Sheep":
        pass

    while state == "Grabbing sheep":
        pass

    state = "movingToPen"
