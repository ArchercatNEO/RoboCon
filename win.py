from library import terminator
import asyncio

R = terminator.Terminator(10)

async def  movement():
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

state = ""

asyncio.run(R.move(1))

while True:

    while state == "Moving To Pen":
        pass

    while state == "Finding Sheep":
        pass

    while state == "Grabbing sheep":
        pass

    state = "movingToPen"
