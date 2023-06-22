import math, itertools, asyncio, time, robot
from enum import Enum
from robot.sheepdog_trials import markers

class Terminator(robot.Robot):
    
    speed = 0.0

    zero = time.time()
    def now(self):
        return time.time() - self.zero
    
    class Logging(Enum):
        Debug = 5
        Zero = 4
        Main = 3
        Minor = 2
        Pedantic = 1
        Get = 0
    
    log_level = Logging.Main
    log_list = {
        "move" : Logging.Pedantic,
        "turn" : Logging.Pedantic,
        "goto" : Logging.Minor,
        "snap" : Logging.Minor,
        "peek" : Logging.Pedantic,
        "triangulate" : Logging.Pedantic,
        "getPower" : Logging.Get,
    }
    
    def trace(self, parent: str, log: str, format: dict):
        if self.log_list[parent].value >= self.log_level.value:
            print(log)

    # Called when making the variable we'll interact with
    # Just sets some values to initial positions
    def __init__(self, maxSpeed: float, length = 6):
        
        self.speed = maxSpeed
        
        #set initial coords to 0.25m either side away from corner and pointing to the center
        match self.zone:

            case robot.TEAM.LEON:
                self.x = 0.25
                self.y = length - 0.25
                self.angle = -45.0
            
            case robot.TEAM.ZHORA:
                self.x = length - 0.25
                self.y = length - 0.25
                self.angle = -90.0
            
            case robot.TEAM.ROY:
                self.x = length - 0.25
                self.y = 0.25
                self.angle = 90.0
            
            case robot.TEAM.PRIS:
                self.x = 0.25
                self.y = 0.25
                self.angle = 45.0

        #set up the coords of the wall markers to be used in triangulate
        self.locations = []
        for i in range(length):
            self.locations.append([i + 0.5, length])
        for i in range(length):
            self.locations.append([length, 6.5 - i])
        for i in range(length):
            self.locations.append([6.5 - i, 0])
        for i in range(length):
            self.locations.append([0, i + 0.5])
            
    async def move(self, meters: float, speed = speed):
        """
        Move x meters at max speed.
        Takes additional arguments to go slower.
        """

        
        
        self.x += math.cos(self.angle * math.pi/180) * meters
        self.y += math.sin(self.angle * math.pi/180) * meters

        self.motors[0] = self.getPower(speed)
        self.motors[1] = self.getPower(speed)

        await asyncio.sleep(meters / speed)

        self.motors[0] = 0
        self.motors[1] = 0

    async def turn(self, degrees: float, speed = speed):
        """
        Turns x degrees at max speed.
        Takes additional arguments to go slower.
        """

        self.angle += degrees * math.pi/180

        sign = degrees/abs(degrees)

        self.motors[0] = self.getPower(speed) * sign
        self.motors[1] = self.getPower(speed) * -sign 

        await asyncio.sleep(degrees / speed)

        self.motors[0] = 0
        self.motors[1] = 0

    async def goto(self, marker):
        """
        Uses the properties of a marker object to turn and move towards it.
        """

        await self.turn(marker.bearing.y)
        await self.move(marker.dist)

    async def snap(self, x: float, y: float):
        """
        Uses the robot's position and rotation to move towards a location in the arena.
        """

        x -= self.x
        y -= self.y

        dist = math.sqrt(x**2 + y**2)
        angle = math.asin(y/dist)

        await self.turn(angle)
        await self.move(dist)

    def getPower(self, speed: float):
        return 100
    
    #use wall markers and their positions to calculate our position and angle
    def triangulate(self, markers):

        averageX = 0
        averageY = 0
        averageAngle = 0
        count = 0

        #do the loop for every combination of 2 markers we have, no duplicates
        for i in itertools.permutations(markers, 2):

            count += 1
            
            m1 = i[0]
            m2 = i[1]

            x1 = self.locations[m1.info.id -100].x
            x2 = self.locations[m2.info.id -100].x
            y1 = self.locations[m1.info.id -100].y
            y2 = self.locations[m2.info.id -100].y

            d1 = m1.dist
            d2 = m2.dist

            a1 = m1.bearing.y
            a2 = m2.bearing.y

            #distance between markers (pythagoras)
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

            #trig to find an angle (law of sines)
            angle = math.asin(math.sin((a1 - a2) * math.pi/180) /distance * d2)

            averageX += math.cos(angle) * d1 - x1
            averageY += math.sin(angle) * d1 - y1
            averageAngle += a1 + angle

        self.x = averageX /count
        self.y = averageY /count
        self.angle = averageAngle /count

    #Look for markers, feed wall markers to triangulate and return non-wall markers
    def peek(self):

        sheep = self.see()
        self.triangulate(filter(lambda marker: (marker.info.owner == markers.MARKER_OWNER.ARENA), sheep)) 

        return filter(lambda marker: (marker.info.owner != markers.MARKER_OWNER.ARENA), sheep)
    
