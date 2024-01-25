"""
Do not import. This is the main file that will run on competition
"""
import asyncio
from terminator import Terminator
from terminator import Logging

R = Terminator(10, Logging.MAIN)

async def main() -> None:
    """
    Run the main thread
    """

asyncio.run(main())
